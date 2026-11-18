"""
Engineering Mathematics Engine - Multivariate Analysis & Bayesian Conditioning.
Implements:
  - Covariance matrix and Pearson Correlation matrix
  - 2D Joint Probability Distribution P(X, Y)
  - Marginal Distributions P(X) and P(Y) via integration/summation
  - Bayesian Conditional Probabilities P(Fault | Feature > Threshold)
  - Physical interpretation in rolling element bearing diagnostics
"""

from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats

from backend.app.data.cwru_metadata import CLASS_NAMES
from backend.app.data.feature_extractor import FEATURE_COLUMNS


def compute_covariance_and_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes full Covariance and Pearson Correlation matrices for the 8 features.
    Extracts top correlated pairs and explains physical mechanical dependencies.
    """
    features_df = df[FEATURE_COLUMNS]
    
    cov_matrix = features_df.cov().to_numpy()
    corr_matrix = features_df.corr().to_numpy()
    
    # Identify notable pairs
    pairs = []
    n = len(FEATURE_COLUMNS)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append({
                "feature_1": FEATURE_COLUMNS[i],
                "feature_2": FEATURE_COLUMNS[j],
                "correlation": float(corr_matrix[i, j]),
                "covariance": float(cov_matrix[i, j])
            })
            
    # Sort by absolute correlation
    pairs_sorted = sorted(pairs, key=lambda x: abs(x["correlation"]), reverse=True)
    
    return {
        "features": FEATURE_COLUMNS,
        "covariance_matrix": [[round(float(v), 6) for v in row] for row in cov_matrix],
        "correlation_matrix": [[round(float(v), 4) for v in row] for row in corr_matrix],
        "top_correlated_pairs": pairs_sorted[:5],
        "engineering_interpretation": (
            "RMS and Standard Deviation exhibit near-perfect correlation (rho ~ 1.0) because vibration signals "
            "oscillate symmetrically about zero mean (E[X] ~ 0), making RMS = sqrt(mu^2 + sigma^2) approx equal to sigma. "
            "In contrast, Crest Factor and Kurtosis show moderate or orthogonal correlation to RMS, capturing transient "
            "spikes and impulse sharpness that raw energy metrics miss. Monitoring both provides balanced sensitivity "
            "to both overall wear (RMS) and localized pitting (Kurtosis/Crest Factor)."
        )
    }


def compute_joint_and_marginal_distribution(
    df: pd.DataFrame,
    feat_x: str = "rms",
    feat_y: str = "kurtosis",
    bins: int = 15
) -> Dict[str, Any]:
    """
    Calculates the 2D Joint Probability Distribution P(X, Y) and derives
    the Marginal Distributions P(X) and P(Y) by discrete summation.
    Verifies the Law of Total Probability: sum_{x,y} P(X=x, Y=y) = 1.0.
    """
    if feat_x not in df.columns or feat_y not in df.columns:
        raise ValueError(f"Features {feat_x} or {feat_y} not found in dataset")
        
    x = df[feat_x].to_numpy(dtype=np.float64)
    y = df[feat_y].to_numpy(dtype=np.float64)
    
    # 2D histogram
    hist_2d, x_edges, y_edges = np.histogram2d(x, y, bins=bins, density=False)
    total_samples = len(x)
    
    # Joint Probability Mass Function (P(X=xi, Y=yj))
    joint_pmf = hist_2d / float(total_samples)
    
    # Deriving marginals by summing over columns / rows
    marginal_x = np.sum(joint_pmf, axis=1)  # sum over Y
    marginal_y = np.sum(joint_pmf, axis=0)  # sum over X
    
    # Verification
    sum_total = float(np.sum(joint_pmf))
    sum_marg_x = float(np.sum(marginal_x))
    sum_marg_y = float(np.sum(marginal_y))
    
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2.0
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2.0
    
    # Format for JSON visualization
    joint_grid = []
    for i in range(bins):
        for j in range(bins):
            if joint_pmf[i, j] > 0:  # Sparse representation
                joint_grid.append({
                    "x": round(float(x_centers[i]), 4),
                    "y": round(float(y_centers[j]), 4),
                    "probability": round(float(joint_pmf[i, j]), 5)
                })
                
    marginal_x_points = [
        {"val": round(float(xc), 4), "prob": round(float(p), 5)}
        for xc, p in zip(x_centers, marginal_x)
    ]
    marginal_y_points = [
        {"val": round(float(yc), 4), "prob": round(float(p), 5)}
        for yc, p in zip(y_centers, marginal_y)
    ]
    
    return {
        "feature_x": feat_x,
        "feature_y": feat_y,
        "total_samples": total_samples,
        "law_of_total_probability_sum": round(sum_total, 6),
        "marginal_x_sum": round(sum_marg_x, 6),
        "marginal_y_sum": round(sum_marg_y, 6),
        "joint_grid": joint_grid,
        "marginal_x": marginal_x_points,
        "marginal_y": marginal_y_points,
        "engineering_interpretation": (
            f"The Joint Distribution P({feat_x}, {feat_y}) captures the simultaneous likelihood of vibration energy and "
            f"impulse sharpness. Summing across columns integrates out {feat_y} to yield the marginal distribution P({feat_x}), "
            f"confirming the Law of Total Probability (sum = {sum_total:.4f}). Healthy bearings cluster at low energy and low kurtosis, "
            f"while severe faults shift the joint density towards the high-{feat_x}, high-{feat_y} quadrant."
        )
    }


def compute_bayesian_conditional_probabilities(
    df: pd.DataFrame,
    threshold_feature: str = "rms",
    num_thresholds: int = 5
) -> Dict[str, Any]:
    """
    Computes Bayesian Conditional Probability:
      P(Condition = C_k | Feature > tau) = [ P(Feature > tau | C_k) * P(C_k) ] / P(Feature > tau)
    Demonstrating diagnostic positive predictive value (PPV) as vibration threshold tau increases.
    """
    total_n = len(df)
    feat_vals = df[threshold_feature].to_numpy()
    
    # Priors P(C_k)
    priors = {}
    class_dfs = {}
    for cname in CLASS_NAMES:
        c_subset = df[df["condition"] == cname]
        priors[cname] = len(c_subset) / float(total_n)
        class_dfs[cname] = c_subset[threshold_feature].to_numpy()
        
    # Generate thresholds across feature range
    min_val = np.percentile(feat_vals, 10)
    max_val = np.percentile(feat_vals, 95)
    thresholds = np.linspace(min_val, max_val, num_thresholds)
    
    results = []
    for tau in thresholds:
        tau_val = float(tau)
        
        # P(Feature > tau)
        p_exceed = np.mean(feat_vals > tau_val)
        
        posteriors = {}
        likelihoods = {}
        
        if p_exceed > 0:
            for cname in CLASS_NAMES:
                # Likelihood P(Feature > tau | C_k)
                c_vals = class_dfs[cname]
                p_exceed_given_c = float(np.mean(c_vals > tau_val))
                likelihoods[cname] = round(p_exceed_given_c, 4)
                
                # Bayes: P(C_k | Feature > tau)
                post = (p_exceed_given_c * priors[cname]) / p_exceed
                posteriors[cname] = round(float(post), 4)
        else:
            for cname in CLASS_NAMES:
                likelihoods[cname] = 0.0
                posteriors[cname] = round(float(priors[cname]), 4)
                
        results.append({
            "threshold": round(tau_val, 4),
            "p_exceedance_overall": round(float(p_exceed), 4),
            "likelihood_P_exceed_given_class": likelihoods,
            "posterior_P_class_given_exceed": posteriors
        })
        
    return {
        "feature": threshold_feature,
        "priors": {k: round(v, 4) for k, v in priors.items()},
        "threshold_evaluations": results,
        "engineering_significance": (
            "Bayesian conditional probability formalizes predictive maintenance alarm logic: "
            "As the vibration threshold increases, the posterior probability of Healthy condition collapses to zero, "
            "while the posterior probability of Outer Race and Inner Race faults rapidly approaches 1.0. "
            "This confirms how sensor threshold exceedances update belief regarding true mechanical state."
        )
    }
