"""
Engineering Mathematics Engine - Educational Demonstrations.
Covers theoretical foundations applied to motor condition monitoring:
  1. Binomial Distribution (Multi-window alarm persistence & false trip suppression)
  2. Poisson Distribution (Defect impact and acoustic burst arrival rates)
  3. Moment Generating Function (MGF) & moment derivation via Taylor expansion
  4. Characteristic Function (Fourier transform of PDF and independent signal superposition)
"""

from typing import Dict, Any, List
import math
import numpy as np
from scipy import stats


def demonstrate_binomial_alarm_filter(
    n_windows: int = 10,
    p_healthy_false_alarm: float = 0.05,
    p_fault_true_alarm: float = 0.90
) -> Dict[str, Any]:
    """
    Demonstrates Binomial Distribution in industrial trip logic:
      P(K = k) = C(n, k) * p^k * (1-p)^(n-k)
    Compares the probability of triggering k alarms out of n observation windows
    under Healthy operation (p=0.05) vs Fault operation (p=0.90).
    """
    k_values = list(range(n_windows + 1))
    
    pmf_healthy = [float(stats.binom.pmf(k, n_windows, p_healthy_false_alarm)) for k in k_values]
    pmf_fault = [float(stats.binom.pmf(k, n_windows, p_fault_true_alarm)) for k in k_values]
    
    # Cumulative probability of at least 3 alarms (alarm trip rule)
    threshold_k = 3
    prob_trip_healthy = float(1.0 - stats.binom.cdf(threshold_k - 1, n_windows, p_healthy_false_alarm))
    prob_trip_fault = float(1.0 - stats.binom.cdf(threshold_k - 1, n_windows, p_fault_true_alarm))
    
    data_points = [
        {
            "k_alarms": k,
            "p_healthy": round(ph, 6),
            "p_fault": round(pf, 6)
        }
        for k, ph, pf in zip(k_values, pmf_healthy, pmf_fault)
    ]
    
    return {
        "n_windows": n_windows,
        "p_healthy_single": p_healthy_false_alarm,
        "p_fault_single": p_fault_true_alarm,
        "distribution_table": data_points,
        "trip_threshold_k": threshold_k,
        "prob_false_trip_healthy": round(prob_trip_healthy, 6),
        "prob_true_trip_fault": round(prob_trip_fault, 6),
        "engineering_explanation": (
            f"If an alarm requires at least {threshold_k} out of {n_windows} consecutive windows to exceed threshold, "
            f"the false trip probability under healthy operation drops from {p_healthy_false_alarm*100:.1f}% to "
            f"{prob_trip_healthy*100:.3f}%! Meanwhile, a genuine bearing fault triggers with {prob_trip_fault*100:.2f}% "
            f"reliability. This proves how the Binomial distribution governs industrial alarm filter design."
        )
    }


def demonstrate_poisson_shock_arrivals(
    lambda_healthy: float = 0.5,
    lambda_fault: float = 8.0,
    max_k: int = 15
) -> Dict[str, Any]:
    """
    Demonstrates Poisson Distribution in vibration shock counting:
      P(X = k) = (lambda^k * e^(-lambda)) / k!
    Models the number of high-energy transient spikes per second in healthy vs defect states.
    """
    k_values = list(range(max_k + 1))
    
    pmf_healthy = [float(stats.poisson.pmf(k, lambda_healthy)) for k in k_values]
    pmf_fault = [float(stats.poisson.pmf(k, lambda_fault)) for k in k_values]
    
    data_points = [
        {
            "k_shocks": k,
            "prob_healthy": round(ph, 6),
            "prob_fault": round(pf, 6)
        }
        for k, ph, pf in zip(k_values, pmf_healthy, pmf_fault)
    ]
    
    return {
        "lambda_healthy": lambda_healthy,
        "lambda_fault": lambda_fault,
        "distribution_table": data_points,
        "mean_shocks_healthy": lambda_healthy,
        "mean_shocks_fault": lambda_fault,
        "engineering_explanation": (
            f"Under healthy conditions, transient shocks are rare background anomalies (mean rate lambda={lambda_healthy}/sec). "
            f"When a fatigue spall develops on the inner or outer raceway, ball passes strike the defect at a high deterministic "
            f"frequency (lambda={lambda_fault}/sec), shifting the Poisson mode towards high shock counts."
        )
    }


def demonstrate_mgf(mu: float = 0.0, sigma: float = 1.0) -> Dict[str, Any]:
    """
    Demonstrates the Moment Generating Function (MGF):
      M_X(t) = E[e^(tX)]
    For a Gaussian random variable: M_X(t) = exp(mu*t + 0.5*sigma^2*t^2).
    Shows how successive derivatives at t=0 generate raw moments:
      M'(0) = E[X] = mu
      M''(0) = E[X^2] = mu^2 + sigma^2
    """
    t_vals = np.linspace(-1.5, 1.5, 31)
    
    mgf_curve = []
    for t in t_vals:
        t_val = float(t)
        # Analytical MGF for Normal(mu, sigma^2)
        mgf_val = float(np.exp(mu * t_val + 0.5 * (sigma ** 2) * (t_val ** 2)))
        mgf_curve.append({
            "t": round(t_val, 3),
            "M_X_t": round(mgf_val, 5)
        })
        
    e1 = mu
    e2 = mu**2 + sigma**2
    variance = e2 - (e1**2)
    
    return {
        "mu": mu,
        "sigma": sigma,
        "mgf_points": mgf_curve,
        "moment_derivations": {
            "first_moment_E_X": round(float(e1), 5),
            "second_moment_E_X2": round(float(e2), 5),
            "derived_variance": round(float(variance), 5)
        },
        "formula": "M_X(t) = exp(mu*t + 0.5*sigma^2*t^2)",
        "engineering_explanation": (
            "The Moment Generating Function encapsulates all statistical moments of a vibration signal into a single analytical function. "
            "Evaluating derivatives at t=0 yields E[X] (mean DC vibration) and E[X^2] (mean total power), which directly provides "
            "the signal variance Var(X) = E[X^2] - (E[X])^2."
        )
    }


def demonstrate_characteristic_function(mu: float = 0.0, sigma: float = 1.0) -> Dict[str, Any]:
    """
    Demonstrates the Characteristic Function:
      phi_X(t) = E[e^(i*t*X)] = int e^(i*t*x) f(x) dx
    For Gaussian: phi_X(t) = exp(i*mu*t - 0.5*sigma^2*t^2).
    Separates into real part (cosine transform) and imaginary part (sine transform).
    """
    t_vals = np.linspace(-3.0, 3.0, 41)
    
    cf_curve = []
    for t in t_vals:
        t_val = float(t)
        # phi_X(t) = exp(-0.5*sigma^2*t^2) * [cos(mu*t) + i*sin(mu*t)]
        mag = float(np.exp(-0.5 * (sigma ** 2) * (t_val ** 2)))
        real_part = mag * float(np.cos(mu * t_val))
        imag_part = mag * float(np.sin(mu * t_val))
        
        cf_curve.append({
            "t": round(t_val, 3),
            "real": round(real_part, 5),
            "imag": round(imag_part, 5),
            "magnitude": round(mag, 5)
        })
        
    return {
        "mu": mu,
        "sigma": sigma,
        "cf_points": cf_curve,
        "formula": "phi_X(t) = exp(i*mu*t - 0.5*sigma^2*t^2)",
        "engineering_explanation": (
            "The Characteristic Function is the Fourier transform of the vibration amplitude PDF. "
            "Unlike the MGF, it is always bounded (|phi_X(t)| <= 1) and exists for all distributions. "
            "In mechanical systems, when independent vibration sources (e.g. motor unbalance + gear mesh) combine, "
            "their joint characteristic function is the simple product of individual characteristic functions: "
            "phi_(X+Y)(t) = phi_X(t) * phi_Y(t)."
        )
    }
