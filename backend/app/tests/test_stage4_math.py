"""
Automated Validation Suite for Stage 4: Mathematical Analysis Engine.
Tests all engineering mathematics components on actual CWRU vibration features:
  - Random variable moments and expectation
  - Distribution assumption tests (Shapiro-Wilk, D'Agostino, KS)
  - Normal Z-score transformations and SPC limit violations
  - Covariance, Pearson correlation, and symmetry
  - 2D Joint and Marginal distributions (Law of Total Probability)
  - Bayesian conditional probabilities
  - Binomial, Poisson, MGF, and Characteristic Function demonstrations
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.math_engine.engine import get_math_engine
from backend.app.data.feature_extractor import FEATURE_COLUMNS
from backend.app.data.cwru_metadata import CLASS_NAMES


def test_stage4_math_engine():
    print("=" * 70)
    print("STAGE 4 VALIDATION: MATHEMATICAL ANALYSIS ENGINE")
    print("=" * 70)

    engine = get_math_engine()
    df = engine.df
    assert len(df) == 3064, f"Dataset must have 3064 rows, got {len(df)}"

    # 1. Feature Overview & Moments
    print("\n1. Testing Feature Moments on CWRU Dataset...")
    overview = engine.get_feature_overview()
    assert len(overview) == 8, f"Expected 8 features, got {len(overview)}"
    for item in overview:
        assert item["feature"] in FEATURE_COLUMNS
        assert item["variance"] > 0
        assert item["std"] > 0
        # Check Var = std^2
        assert abs(item["variance"] - (item["std"] ** 2)) < 1e-4
        print(f"  {item['feature']:<15}: Mean={item['mean']:.4f}, Std={item['std']:.4f}, "
              f"Kurtosis={item['kurtosis']:.2f}, Normality p-val={item['normality_p_value']:.2e}")
    print("[PASS] Random variable moments and variance-std identity verified.")

    # 2. Distribution Assumption Checking
    print("\n2. Testing Distribution Assumptions (Checking Normality vs Blind Assumptions)...")
    comp = engine.get_condition_comparison("rms")
    for cname in CLASS_NAMES:
        norm_res = comp["conditions"][cname]["normality_test"]
        p_val = norm_res["dagostino_pearson"]["p_value"]
        assert 0.0 <= p_val <= 1.0, f"Invalid p-value: {p_val}"
        print(f"  {cname:<18} -> D'Agostino p-value: {p_val:.2e} | "
              f"Shapiro-Wilk p-value: {norm_res['shapiro_wilk']['p_value']:.2e} | "
              f"Normality Accepted: {norm_res['overall_normality_accepted']}")
        
    # Real bearing data under outer/inner race faults exhibits heavy-tailed non-normality
    fault_norm = comp["conditions"]["Outer Race Fault"]["normality_test"]
    assert not fault_norm["overall_normality_accepted"], "Fault vibration must reject pure Gaussian normality"
    print("[PASS] Distribution assumption checks strictly validated.")

    # 3. Z-scores and SPC Limits
    print("\n3. Testing Z-Score Transformation & SPC Limits...")
    # Baseline against baseline should be in-control
    spc_healthy = engine.get_zscore_analysis("rms", "Healthy")
    print(f"  Healthy vs Baseline: Mean Z={spc_healthy['mean_z_score']:.2f}, "
          f"3-Sigma Exceedance={spc_healthy['exceed_3sigma_pct']}%, State={spc_healthy['spc_state']}")
    assert abs(spc_healthy["mean_z_score"]) < 0.2
    assert spc_healthy["exceed_3sigma_pct"] < 2.0
    assert spc_healthy["spc_state"] == "IN_CONTROL"

    # Outer Race Fault against baseline should trigger critical alarm
    spc_fault = engine.get_zscore_analysis("rms", "Outer Race Fault")
    print(f"  Outer Race Fault vs Baseline: Mean Z={spc_fault['mean_z_score']:.2f}, "
          f"3-Sigma Exceedance={spc_fault['exceed_3sigma_pct']}%, State={spc_fault['spc_state']}")
    assert spc_fault["mean_z_score"] > 5.0
    assert spc_fault["exceed_3sigma_pct"] > 80.0
    assert spc_fault["spc_state"] == "CRITICAL_OUT_OF_CONTROL"
    print("[PASS] Z-scores and SPC Shewhart rules mathematically verified.")

    # 4. Covariance & Correlation
    print("\n4. Testing Covariance & Pearson Correlation Matrices...")
    mv = engine.get_multivariate_analysis("rms", "kurtosis")
    cov_corr = mv["covariance_and_correlation"]
    cov_mat = np.array(cov_corr["covariance_matrix"])
    corr_mat = np.array(cov_corr["correlation_matrix"])
    
    # Symmetry checks
    assert np.allclose(cov_mat, cov_mat.T, atol=1e-5), "Covariance matrix must be symmetric"
    assert np.allclose(corr_mat, corr_mat.T, atol=1e-5), "Correlation matrix must be symmetric"
    # Diagonal correlation must be 1.0
    for i in range(len(FEATURE_COLUMNS)):
        assert abs(corr_mat[i, i] - 1.0) < 1e-4, f"Correlation diagonal must be 1.0, got {corr_mat[i, i]}"
    print(f"  Top correlated pair: {cov_corr['top_correlated_pairs'][0]['feature_1']} <-> "
          f"{cov_corr['top_correlated_pairs'][0]['feature_2']} (rho = {cov_corr['top_correlated_pairs'][0]['correlation']:.4f})")
    print("[PASS] Covariance and Correlation matrices verified.")

    # 5. Joint & Marginal Distributions
    print("\n5. Testing 2D Joint Distribution & Marginal Derivation...")
    joint = mv["joint_and_marginal"]
    assert abs(joint["law_of_total_probability_sum"] - 1.0) < 1e-4, f"Joint PMF must sum to 1.0, got {joint['law_of_total_probability_sum']}"
    assert abs(joint["marginal_x_sum"] - 1.0) < 1e-4, f"Marginal X must sum to 1.0, got {joint['marginal_x_sum']}"
    assert abs(joint["marginal_y_sum"] - 1.0) < 1e-4, f"Marginal Y must sum to 1.0, got {joint['marginal_y_sum']}"
    print(f"  Joint PMF sum:     {joint['law_of_total_probability_sum']:.6f}")
    print(f"  Marginal X (RMS) sum:      {joint['marginal_x_sum']:.6f}")
    print(f"  Marginal Y (Kurtosis) sum: {joint['marginal_y_sum']:.6f}")
    print("[PASS] Law of Total Probability verified on 2D joint vibration distribution.")

    # 6. Bayesian Conditional Probabilities
    print("\n6. Testing Bayesian Conditional Probabilities P(Condition | Feature > tau)...")
    bayesian = mv["bayesian_conditioning"]
    assert len(bayesian["threshold_evaluations"]) == 5
    for ev in bayesian["threshold_evaluations"]:
        posteriors = ev["posterior_P_class_given_exceed"]
        sum_post = sum(posteriors.values())
        assert abs(sum_post - 1.0) < 1e-3, f"Posteriors must sum to 1.0, got {sum_post}"
    
    first_ev = bayesian["threshold_evaluations"][0]
    last_ev = bayesian["threshold_evaluations"][-1]
    print(f"  At low threshold tau={first_ev['threshold']:.4f}: P(Healthy | RMS > tau) = {first_ev['posterior_P_class_given_exceed']['Healthy']}")
    print(f"  At high threshold tau={last_ev['threshold']:.4f}: P(Healthy | RMS > tau) = {last_ev['posterior_P_class_given_exceed']['Healthy']}, "
          f"P(Outer Race | RMS > tau) = {last_ev['posterior_P_class_given_exceed']['Outer Race Fault']}")
    assert last_ev["posterior_P_class_given_exceed"]["Healthy"] == 0.0
    print("[PASS] Bayesian conditional probabilities verified.")

    # 7. Educational Demonstrations
    print("\n7. Testing Educational Demonstrations (Binomial, Poisson, MGF, CF)...")
    demos = engine.get_educational_demos()
    
    # Binomial
    binom = demos["binomial_persistence"]
    sum_binom_healthy = sum(item["p_healthy"] for item in binom["distribution_table"])
    assert abs(sum_binom_healthy - 1.0) < 1e-4
    print(f"  Binomial trip logic: False trip drop from {binom['p_healthy_single']*100:.1f}% to {binom['prob_false_trip_healthy']*100:.3f}%")
    
    # Poisson
    poisson = demos["poisson_shock_rate"]
    sum_poisson = sum(item["prob_healthy"] for item in poisson["distribution_table"])
    assert sum_poisson > 0.99
    print(f"  Poisson shock arrival modes: Healthy lambda={poisson['mean_shocks_healthy']}, Fault lambda={poisson['mean_shocks_fault']}")
    
    # MGF
    mgf = demos["moment_generating_function"]
    # At t=0, M(0) must equal 1.0
    m0_point = [p for p in mgf["mgf_points"] if abs(p["t"]) < 1e-4][0]
    assert abs(m0_point["M_X_t"] - 1.0) < 1e-4
    print(f"  MGF at t=0: {m0_point['M_X_t']:.5f} (Identically 1.0), Derived Var={mgf['moment_derivations']['derived_variance']}")
    
    # Characteristic function
    cf = demos["characteristic_function"]
    cf0_point = [p for p in cf["cf_points"] if abs(p["t"]) < 1e-4][0]
    assert abs(cf0_point["magnitude"] - 1.0) < 1e-4
    print(f"  Characteristic function at t=0: Magnitude={cf0_point['magnitude']:.5f} (Bounded <= 1.0)")
    print("[PASS] All 4 educational demonstrations verified.")

    print("\n" + "=" * 70)
    print("STAGE 4 TEST PASSED: MATHEMATICAL ANALYSIS ENGINE FULLY OPERATIONAL")
    print("=" * 70)
    return True


if __name__ == "__main__":
    test_stage4_math_engine()
