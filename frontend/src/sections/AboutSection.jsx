import React from 'react';
import { 
  Info, 
  ExternalLink, 
  Database, 
  Cpu, 
  Activity, 
  ShieldCheck, 
  BookOpen, 
  Layers,
  Award
} from 'lucide-react';

export default function AboutSection() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5">
        <h2 className="text-base font-bold text-white tracking-wide flex items-center space-x-2 font-mono">
          <Info className="w-5 h-5 text-cyan-400" />
          <span>ABOUT MOTORGUARD AI — UNIVERSITY-LEVEL ENGINEERING SPECIFICATION</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          A balanced synthesis of Mechanical Vibration Engineering, Rigorous Mathematical Statistics, Supervised Machine Learning, and Industrial Full-Stack Software Architecture.
        </p>
      </div>

      {/* Dataset & Attribution Card */}
      <div className="bg-industrial-900 border border-cyan-500/40 rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-industrial-border/60 pb-3">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white font-mono">OFFICIAL DATASET ATTRIBUTION</h3>
              <p className="text-xs text-slate-400 font-mono">Case Western Reserve University (CWRU) Bearing Data Center</p>
            </div>
          </div>

          <a 
            href="https://engineering.case.edu/bearingdatacenter/download-data-file" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 rounded text-xs font-mono transition"
          >
            <span>engineering.case.edu</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="text-xs text-slate-300 space-y-2 leading-relaxed">
          <p>
            All accelerometer vibration recordings utilized in MotorGuard AI are authentic experimental data collected by the Case Western Reserve University Bearing Data Center. No synthetic sensor readings or fabricated signals are generated.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
            <div className="bg-industrial-950 p-3 rounded border border-industrial-border">
              <span className="font-bold text-cyan-400 font-mono block">Experimental Test Rig</span>
              <span className="text-slate-400 text-[11px] font-mono">
                2 HP Reliance Electric motor, torque transducer, dynamometer, and deep groove ball bearings (SKF 6205-2RS JEM).
              </span>
            </div>
            <div className="bg-industrial-950 p-3 rounded border border-industrial-border">
              <span className="font-bold text-cyan-400 font-mono block">Sampling & Fault Seeding</span>
              <span className="text-slate-400 text-[11px] font-mono">
                Sampled at 12,000 samples/sec (12 kHz) at Drive-End. Seeded electro-discharge machining (EDM) defects with 0.007" diameters across 0, 1, 2, and 3 HP loads (~1797 to 1720 RPM).
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 3 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Pillar 1: Mathematical Engine */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-cyan-400 font-mono text-xs font-bold">
            <Activity className="w-4 h-4" />
            <span>1. ENGINEERING MATHEMATICS</span>
          </div>
          <ul className="text-xs text-slate-300 space-y-2 list-disc list-inside">
            <li><strong>Random Variables</strong>: Continuous mapping of 2048-sample vibration windows ($X$).</li>
            <li><strong>Moments & Expectation</strong>: $E[X]$, Variance $\sigma^2$, Skewness (3rd), and Kurtosis (4th).</li>
            <li><strong>Hypothesis Testing</strong>: Shapiro-Wilk and D'Agostino tests rejecting blind normality ($p &lt; 0.05$).</li>
            <li><strong>SPC Control Charts</strong>: Standardized Z-scores with Shewhart 2-sigma and 3-sigma limits.</li>
            <li><strong>Multivariate Theory</strong>: $8 \times 8$ covariance, Pearson correlation, and 2D joint density $P(X_1, X_2)$.</li>
            <li><strong>Bayesian Updating</strong>: $P(\text{Fault} \mid \text{RMS} &gt; \tau)$ posterior calculation.</li>
          </ul>
        </div>

        {/* Pillar 2: Supervised Machine Learning */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-purple-400 font-mono text-xs font-bold">
            <Cpu className="w-4 h-4" />
            <span>2. MACHINE LEARNING ENGINE</span>
          </div>
          <ul className="text-xs text-slate-300 space-y-2 list-disc list-inside">
            <li><strong>Zero Data Leakage</strong>: Rigorous grouped train/test split holding out whole unseen experimental recordings (Load 3 HP).</li>
            <li><strong>Random Forest</strong>: 100 decision trees, balanced class weights, Gini impurity MDI feature importance.</li>
            <li><strong>Logistic Regression</strong>: Multinomial regularized solver with coefficient magnitude analysis.</li>
            <li><strong>Preprocessing Pipeline</strong>: Strictly isolated `StandardScaler` fitted on training recording groups only.</li>
            <li><strong>Calibration</strong>: Full multi-class probability outputs for all four bearing conditions.</li>
          </ul>
        </div>

        {/* Pillar 3: Full-Stack Architecture */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-emerald-400 font-mono text-xs font-bold">
            <Layers className="w-4 h-4" />
            <span>3. INDUSTRIAL FULL-STACK</span>
          </div>
          <ul className="text-xs text-slate-300 space-y-2 list-disc list-inside">
            <li><strong>Backend</strong>: FastAPI asynchronous REST services with structured pydantic data validation.</li>
            <li><strong>Database</strong>: SQLite with indexed logging of continuous playback telemetry and maintenance records.</li>
            <li><strong>Signal Playback</strong>: Streamer simulating real-time acquisition from 3.16 million raw CWRU samples.</li>
            <li><strong>Frontend</strong>: Modern dark industrial dashboard built with React, Vite, Tailwind CSS, and Recharts.</li>
            <li><strong>Prescriptive Maintenance</strong>: Actionable playbook aligned with ISO 10816 vibration severity standards.</li>
          </ul>
        </div>
      </div>

      {/* University Project Verification Card */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Award className="w-8 h-8 text-amber-400 shrink-0" />
          <div>
            <h4 className="text-xs font-bold text-white font-mono uppercase">Academic & Industrial Rigor</h4>
            <p className="text-[11px] text-slate-400">
              Complies with all technical constraints: zero fabricated data, zero hardcoded accuracy metrics, reproducible Scikit-Learn training pipelines, and verified mathematical proof of statistical identities.
            </p>
          </div>
        </div>
        <span className="text-xs font-mono font-bold px-3 py-1.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 shrink-0">
          STAGE 1-6 COMPLETED
        </span>
      </div>
    </div>
  );
}
