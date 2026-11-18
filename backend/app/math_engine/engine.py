"""
Unified Mathematical Engine Service for MotorGuard AI.
Coordinates statistical analysis, hypothesis testing, bivariate distributions,
and educational demonstrations on the actual CWRU feature dataset.
"""

import os
import sys
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.data.generate_dataset import CSV_OUTPUT_PATH
from backend.app.data.cwru_metadata import CLASS_NAMES
from backend.app.data.feature_extractor import FEATURE_COLUMNS
from backend.app.math_engine.statistics import (
    analyze_feature_moments,
    check_distribution_assumptions,
    compute_empirical_vs_normal_pdf,
    compute_zscores_and_spc
)
from backend.app.math_engine.multivariate import (
    compute_covariance_and_correlation,
    compute_joint_and_marginal_distribution,
    compute_bayesian_conditional_probabilities
)
from backend.app.math_engine.educational import (
    demonstrate_binomial_alarm_filter,
    demonstrate_poisson_shock_arrivals,
    demonstrate_mgf,
    demonstrate_characteristic_function
)


class MathEngineService:
    """
    Central service providing mathematical analytics on CWRU extracted features.
    """
    
    def __init__(self, dataset_path: str = CSV_OUTPUT_PATH):
        self.dataset_path = dataset_path
        self._df: Optional[pd.DataFrame] = None

    @property
    def df(self) -> pd.DataFrame:
        if self._df is None:
            if not os.path.exists(self.dataset_path):
                raise FileNotFoundError(f"Processed dataset not found at {self.dataset_path}")
            self._df = pd.read_csv(self.dataset_path)
        return self._df

    def get_feature_overview(self) -> List[Dict[str, Any]]:
        """Summarizes all 8 features across the full experimental dataset."""
        overview = []
        for feat in FEATURE_COLUMNS:
            m = analyze_feature_moments(self.df[feat].to_numpy(), feat)
            norm = check_distribution_assumptions(self.df[feat].to_numpy(), feat)
            overview.append({
                "feature": feat,
                "mean": round(m["expectation_E_X"], 5),
                "std": round(m["standard_deviation_sigma"], 5),
                "variance": round(m["variance_Var_X"], 6),
                "skewness": round(m["skewness"], 4),
                "kurtosis": round(m["pearson_kurtosis"], 4),
                "normality_p_value": round(norm["dagostino_pearson"]["p_value"], 6),
                "normality_accepted": norm["overall_normality_accepted"]
            })
        return overview

    def get_condition_comparison(self, feature_name: str = "rms") -> Dict[str, Any]:
        """Compares a specific feature across all four bearing operating conditions."""
        if feature_name not in FEATURE_COLUMNS:
            raise ValueError(f"Feature '{feature_name}' not in {FEATURE_COLUMNS}")
            
        res = {}
        for cname in CLASS_NAMES:
            subset = self.df[self.df["condition"] == cname][feature_name].to_numpy()
            moments = analyze_feature_moments(subset, feature_name)
            norm = check_distribution_assumptions(subset, feature_name)
            res[cname] = {
                "moments": moments,
                "normality_test": norm
            }
        return {
            "feature": feature_name,
            "conditions": res
        }

    def get_feature_distribution(self, feature_name: str = "rms", condition: Optional[str] = None) -> Dict[str, Any]:
        """Returns empirical PDF and theoretical normal overlay for a feature."""
        if feature_name not in FEATURE_COLUMNS:
            raise ValueError(f"Feature '{feature_name}' not in {FEATURE_COLUMNS}")
            
        data = self.df[feature_name].to_numpy() if not condition else self.df[self.df["condition"] == condition][feature_name].to_numpy()
        moments = analyze_feature_moments(data, feature_name)
        norm_test = check_distribution_assumptions(data, feature_name)
        pdf_data = compute_empirical_vs_normal_pdf(data)
        
        return {
            "feature": feature_name,
            "condition": condition or "All Conditions",
            "moments": moments,
            "normality_testing": norm_test,
            "distribution_curves": pdf_data
        }

    def get_zscore_analysis(self, feature_name: str = "rms", target_condition: str = "Inner Race Fault") -> Dict[str, Any]:
        """Z-score transformation of a target condition against Healthy baseline parameters."""
        healthy_vals = self.df[self.df["condition"] == "Healthy"][feature_name].to_numpy()
        target_vals = self.df[self.df["condition"] == target_condition][feature_name].to_numpy()
        
        baseline_mu = float(np.mean(healthy_vals))
        baseline_sigma = float(np.std(healthy_vals, ddof=1))
        
        spc = compute_zscores_and_spc(target_vals, baseline_mu, baseline_sigma)
        spc["feature"] = feature_name
        spc["evaluated_condition"] = target_condition
        return spc

    def get_multivariate_analysis(self, feat_x: str = "rms", feat_y: str = "kurtosis") -> Dict[str, Any]:
        """Returns correlation matrix, covariance matrix, and 2D joint distribution."""
        cov_corr = compute_covariance_and_correlation(self.df)
        joint = compute_joint_and_marginal_distribution(self.df, feat_x=feat_x, feat_y=feat_y)
        bayesian = compute_bayesian_conditional_probabilities(self.df, threshold_feature=feat_x)
        
        return {
            "covariance_and_correlation": cov_corr,
            "joint_and_marginal": joint,
            "bayesian_conditioning": bayesian
        }

    def get_educational_demos(self) -> Dict[str, Any]:
        """Returns all 4 interactive educational demonstrations."""
        return {
            "binomial_persistence": demonstrate_binomial_alarm_filter(),
            "poisson_shock_rate": demonstrate_poisson_shock_arrivals(),
            "moment_generating_function": demonstrate_mgf(mu=0.0, sigma=1.0),
            "characteristic_function": demonstrate_characteristic_function(mu=0.0, sigma=1.0)
        }


# Singleton service
_math_engine = None

def get_math_engine() -> MathEngineService:
    global _math_engine
    if _math_engine is None:
        _math_engine = MathEngineService()
    return _math_engine
