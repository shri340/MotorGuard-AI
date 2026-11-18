"""
Engineering Mathematics Engine - Univariate Statistics & Distribution Testing.
Analyzes actual extracted CWRU bearing vibration features:
  - Random variable characterization
  - Expectation, Variance, Standard Deviation, Higher Moments
  - Normality Assumption Checking (Shapiro-Wilk, D'Agostino-Pearson Omnibus, Kolmogorov-Smirnov)
  - Empirical PDF, CDF, Percentiles vs Theoretical Gaussian
  - Z-score transformation and Statistical Process Control (SPC) thresholds
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

from backend.app.data.cwru_metadata import CLASS_NAMES
from backend.app.data.feature_extractor import FEATURE_COLUMNS


def analyze_feature_moments(data: np.ndarray, feature_name: str) -> Dict[str, Any]:
    """
    Computes rigorous probabilistic moments and summary statistics for a feature random variable.
    """
    clean_data = np.asarray(data, dtype=np.float64)
    clean_data = clean_data[~np.isnan(clean_data)]
    n = len(clean_data)
    if n == 0:
        raise ValueError("Cannot analyze empty dataset")
        
    mean_val = float(np.mean(clean_data))
    var_val = float(np.var(clean_data, ddof=1))
    std_val = float(np.std(clean_data, ddof=1))
    median_val = float(np.median(clean_data))
    min_val = float(np.min(clean_data))
    max_val = float(np.max(clean_data))
    iqr_val = float(stats.iqr(clean_data))
    
    # Mathematical higher moments
    skew_val = float(stats.skew(clean_data, bias=False)) if std_val > 1e-12 else 0.0
    kurt_val = float(stats.kurtosis(clean_data, fisher=False, bias=False)) if std_val > 1e-12 else 3.0  # Pearson
    excess_kurt = kurt_val - 3.0
    
    # Percentiles
    percentiles = {
        "p5": float(np.percentile(clean_data, 5)),
        "p25": float(np.percentile(clean_data, 25)),
        "p50": median_val,
        "p75": float(np.percentile(clean_data, 75)),
        "p95": float(np.percentile(clean_data, 95)),
        "p99": float(np.percentile(clean_data, 99))
    }
    
    return {
        "feature_name": feature_name,
        "sample_size": n,
        "expectation_E_X": mean_val,
        "variance_Var_X": var_val,
        "standard_deviation_sigma": std_val,
        "median": median_val,
        "interquartile_range_IQR": iqr_val,
        "min": min_val,
        "max": max_val,
        "skewness": skew_val,
        "pearson_kurtosis": kurt_val,
        "excess_kurtosis": excess_kurt,
        "percentiles": percentiles,
        "engineering_explanation": (
            f"Expectation E[{feature_name}] represents the steady-state baseline ({mean_val:.4f}). "
            f"The standard deviation ({std_val:.4f}) reflects amplitude variability across motor loads. "
            f"Excess kurtosis of {excess_kurt:+.2f} indicates "
            f"{'heavy-tailed, impulse-dominated behaviour typical of mechanical defects' if excess_kurt > 0.5 else 'near-normal or platykurtic distribution'}."
        )
    }


def check_distribution_assumptions(data: np.ndarray, feature_name: str) -> Dict[str, Any]:
    """
    Checks the normality assumption instead of blind Gaussian assumption.
    Implements:
      1. Shapiro-Wilk Test (sample size up to 5000)
      2. D'Agostino-Pearson Omnibus Test (combines skew and kurtosis)
      3. Kolmogorov-Smirnov Test against fitted Normal distribution
    """
    clean_data = np.asarray(data, dtype=np.float64)
    clean_data = clean_data[~np.isnan(clean_data)]
    n = len(clean_data)
    
    mean_val = float(np.mean(clean_data))
    std_val = float(np.std(clean_data, ddof=1))
    
    # 1. Shapiro-Wilk test (subset to 2000 if larger for computational speed and scipy limit)
    sample_for_sw = clean_data if n <= 2000 else np.random.choice(clean_data, size=2000, replace=False)
    sw_stat, sw_p = stats.shapiro(sample_for_sw)
    
    # 2. D'Agostino Pearson Omnibus test (requires n >= 20)
    if n >= 20 and std_val > 1e-12:
        dag_stat, dag_p = stats.normaltest(clean_data)
        dag_stat = float(dag_stat)
        dag_p = float(dag_p)
    else:
        dag_stat, dag_p = 0.0, 1.0
        
    # 3. Kolmogorov-Smirnov test against fitted normal distribution
    if std_val > 1e-12:
        ks_res = stats.kstest(clean_data, stats.norm(loc=mean_val, scale=std_val).cdf)
        ks_stat = float(ks_res.statistic)
        ks_p = float(ks_res.pvalue)
    else:
        ks_stat, ks_p = 0.0, 1.0
        
    alpha = 0.05
    is_normal = bool(dag_p > alpha and sw_p > alpha)
    
    return {
        "feature_name": feature_name,
        "sample_size": n,
        "assumed_distribution": "Gaussian / Normal N(mu, sigma^2)",
        "shapiro_wilk": {
            "statistic_W": float(sw_stat),
            "p_value": float(sw_p),
            "reject_normality_at_5pct": bool(sw_p < alpha)
        },
        "dagostino_pearson": {
            "statistic_K2": float(dag_stat),
            "p_value": float(dag_p),
            "reject_normality_at_5pct": bool(dag_p < alpha)
        },
        "kolmogorov_smirnov": {
            "statistic_D": float(ks_stat),
            "p_value": float(ks_p),
            "reject_normality_at_5pct": bool(ks_p < alpha)
        },
        "overall_normality_accepted": is_normal,
        "engineering_interpretation": (
            f"For {feature_name}, the empirical distribution "
            f"{'conforms to a Normal distribution (p > 0.05)' if is_normal else 'STRICTLY REJECTS normality (p < 0.05)'}. "
            f"In bearing monitoring, mechanical impact shocks produce asymmetric distributions and heavy tails, "
            f"making non-parametric thresholds or empirical quantiles essential over naive 3-sigma Gaussian models."
        )
    }


def compute_empirical_vs_normal_pdf(data: np.ndarray, num_bins: int = 30) -> Dict[str, Any]:
    """
    Computes the empirical histogram/density and theoretical normal PDF overlay for visualization.
    """
    clean_data = np.asarray(data, dtype=np.float64)
    clean_data = clean_data[~np.isnan(clean_data)]
    
    counts, bin_edges = np.histogram(clean_data, bins=num_bins, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    
    # Theoretical normal PDF evaluated at bin centers
    mu = float(np.mean(clean_data))
    sigma = float(np.std(clean_data, ddof=1))
    
    if sigma > 1e-12:
        theoretical_pdf = stats.norm.pdf(bin_centers, loc=mu, scale=sigma)
    else:
        theoretical_pdf = np.zeros_like(bin_centers)
        
    # Empirical CDF
    sorted_data = np.sort(clean_data)
    cdf_x = np.linspace(sorted_data[0], sorted_data[-1], 50)
    empirical_cdf = [float(np.mean(sorted_data <= x)) for x in cdf_x]
    theoretical_cdf = [float(stats.norm.cdf(x, loc=mu, scale=sigma)) for x in cdf_x]
    
    histogram_points = [
        {
            "bin_center": round(float(bc), 5),
            "bin_left": round(float(be_left), 5),
            "bin_right": round(float(be_right), 5),
            "empirical_density": round(float(ed), 5),
            "theoretical_density": round(float(td), 5)
        }
        for bc, be_left, be_right, ed, td in zip(bin_centers, bin_edges[:-1], bin_edges[1:], counts, theoretical_pdf)
    ]
    
    cdf_points = [
        {
            "x": round(float(x), 5),
            "empirical_cdf": round(ecdf, 5),
            "theoretical_cdf": round(tcdf, 5)
        }
        for x, ecdf, tcdf in zip(cdf_x, empirical_cdf, theoretical_cdf)
    ]
    
    return {
        "mu": mu,
        "sigma": sigma,
        "histogram_points": histogram_points,
        "cdf_points": cdf_points
    }


def compute_zscores_and_spc(
    test_values: np.ndarray, 
    baseline_mu: float, 
    baseline_sigma: float
) -> Dict[str, Any]:
    """
    Computes standard normal Z-score transformation:
      Z = (X - mu_baseline) / sigma_baseline
    And applies Statistical Process Control (SPC) Shewhart rules:
      - Warning: |Z| > 2 (2-sigma limit, ~95.45% confidence under normal)
      - Alarm/Fault: |Z| > 3 (3-sigma limit, ~99.73% confidence under normal)
    """
    test_values = np.asarray(test_values, dtype=np.float64)
    if baseline_sigma < 1e-12:
        baseline_sigma = 1e-6
        
    z_scores = (test_values - baseline_mu) / baseline_sigma
    
    exceed_2sigma = int(np.sum(np.abs(z_scores) > 2.0))
    exceed_3sigma = int(np.sum(np.abs(z_scores) > 3.0))
    
    return {
        "baseline_mean": baseline_mu,
        "baseline_sigma": baseline_sigma,
        "total_evaluated": len(test_values),
        "mean_z_score": float(np.mean(z_scores)),
        "max_z_score": float(np.max(z_scores)),
        "min_z_score": float(np.min(z_scores)),
        "exceed_2sigma_count": exceed_2sigma,
        "exceed_2sigma_pct": round(float(exceed_2sigma / len(test_values) * 100), 2),
        "exceed_3sigma_count": exceed_3sigma,
        "exceed_3sigma_pct": round(float(exceed_3sigma / len(test_values) * 100), 2),
        "spc_state": "CRITICAL_OUT_OF_CONTROL" if exceed_3sigma > 0.1 * len(test_values) else (
            "WARNING_DRIFT" if exceed_2sigma > 0.2 * len(test_values) else "IN_CONTROL"
        ),
        "engineering_significance": (
            "Z-scores normalize vibration features against pristine baseline parameters. "
            "A Z-score above 3 indicates vibration levels over 3 standard deviations above normal, "
            "providing a standardized, unitless anomaly alarm threshold."
        )
    }
