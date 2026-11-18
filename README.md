# MotorGuard AI — Intelligent Motor Condition Monitoring & Predictive Maintenance

MotorGuard AI is a university-level engineering and artificial intelligence application designed for intelligent rolling element bearing fault diagnosis, statistical vibration analysis, and condition-based predictive maintenance.

Built with experimental accelerometer recordings from the **Case Western Reserve University (CWRU) Bearing Data Center**.

---

## Technical Stack & Architecture

- **Backend**: FastAPI, Python 3.12, SQLite (`data/motorguard.db`), NumPy, SciPy, Pandas, Scikit-Learn.
- **Frontend**: React 18, Vite 6, Tailwind CSS, Recharts, Lucide Icons (Dark industrial UI).
- **Dataset**: CWRU 12 kHz Drive-End Accelerometer Recordings (Reliance Electric 2 HP motor).
- **Machine Learning**: Supervised Random Forest Classifier & Multinomial Logistic Regression trained on leakage-resistant recording holdout splits.
- **Mathematics Engine**: Univariate moments, distribution assumption tests (Shapiro-Wilk, D'Agostino-Pearson, Kolmogorov-Smirnov), standardized Z-scores with Shewhart SPC control limits, $8 \times 8$ covariance & Pearson correlation matrices, bivariate joint PMF $P(\text{RMS}, \text{Kurtosis})$, Bayesian conditional probability updates, and educational models (Binomial alarm persistence, Poisson shock arrival, MGF, Characteristic functions).

---

## The Eight Frontend Sections

1. **Dashboard**: High-level machine health status, ISO 10816 severity index gauge (0–100), key engineering KPIs (RMS, Kurtosis, Peak-to-Peak, Motor Load/RPM), and live 2048-sample waveform quick-glance.
2. **Motor Monitoring (Recorded Signal Playback)**: Stream historical experimental recordings across all 16 CWRU runs (Healthy, Inner Race Fault, Ball Fault, Outer Race Fault across 0–3 HP). Features **Start**, **Pause**, **Reset**, **Step Backward**, **Step Forward**, and timeline scrubber slider. Clearly labeled: *RECORDED EXPERIMENTAL DATA PLAYBACK - NOT LIVE HARDWARE MONITORING*.
3. **Statistical Analysis**: In-depth moment analysis table across all 8 features (Expectation $E[X]$, Variance $\text{Var}(X)$, Standard Deviation $\sigma$, Median, IQR, Skewness, Kurtosis, Percentiles p5–p99) and interactive cross-condition moments comparison bar charts.
4. **Probability Distributions**: Normality assumption testing, empirical PDF histograms with theoretical Gaussian overlays, empirical/theoretical CDFs, standardized Z-scores with Shewhart 2-sigma/3-sigma limits, Pearson correlation matrix, 2D joint density grids, Bayesian conditional probability curves, and interactive educational demonstrations (Binomial, Poisson, MGF, Characteristic function).
5. **ML Predictions**: Comparative test metrics (Random Forest vs Logistic Regression on holdout load 3 HP recordings), side-by-side row-normalized $4 \times 4$ confusion matrices, MDI feature importance rankings, and an interactive Custom Vibration Simulator.
6. **Historical Analysis**: Chronological event logs stored in SQLite, filterable by condition, severity trend area charts, summary telemetry statistics, and log clearance actions.
7. **Maintenance Recommendations**: Prescriptive Maintenance Playbook mapped to ISO 10816 standards for each defect type, and an interactive SQLite Work Order manager with creation modal and status advancement (`PENDING` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `COMPLETED`).
8. **About Project**: Academic engineering documentation, test apparatus specifications, mathematical formulation references, and official CWRU dataset attribution.

---

## How to Run

### 1. Run Comprehensive Master Integration Test Runner
To verify all 7 project stages (dataset loading, feature extraction, ML training, math engine, backend APIs, frontend build, and full end-to-end workflow simulation):

```powershell
cd C:\Users\shrih\.gemini\antigravity\scratch\motorguard-ai
python backend/app/tests/run_all_tests.py
```

### 2. Launch Full-Stack Application
To start both the FastAPI backend (port 8000) and the Vite frontend (port 5173):

```powershell
cd C:\Users\shrih\.gemini\antigravity\scratch\motorguard-ai
python run_application.py
```

- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Quality & Academic Integrity Compliance

- **No Fabricated Readings**: 3,161,187 real experimental accelerometer samples loaded via `scipy.io.loadmat`.
- **Zero Data Leakage**: Grouped train/test splitting ensures test windows originate from physically distinct, held-out motor recordings.
- **No Hardcoded Accuracy**: All metrics, confusion matrices, and feature importances are dynamically computed and verified by automated test suites.
- **Checked Distribution Assumptions**: Rejects naive normality assumptions via formal hypothesis testing ($p < 0.05$).
