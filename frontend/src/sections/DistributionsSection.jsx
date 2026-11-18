import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  HelpCircle, 
  CheckCircle, 
  AlertTriangle, 
  Layers, 
  Sliders, 
  Zap,
  BookOpen,
  GitBranch,
  ShieldAlert
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend, 
  AreaChart, 
  Area,
  ScatterChart,
  Scatter
} from 'recharts';
import { 
  getFeatureDistribution, 
  getZScoreAnalysis, 
  getMultivariateAnalytics, 
  getEducationalDemos 
} from '../api/client';

export default function DistributionsSection() {
  const [activeTab, setActiveTab] = useState('normality'); // 'normality', 'zscore', 'multivariate', 'bayesian', 'educational'
  const [selectedFeature, setSelectedFeature] = useState('rms');
  const [selectedCondition, setSelectedCondition] = useState('Outer Race Fault');
  const [distData, setDistData] = useState(null);
  const [zscoreData, setZscoreData] = useState(null);
  const [multiData, setMultiData] = useState(null);
  const [eduData, setEduData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTabContent() {
      try {
        setLoading(true);
        if (activeTab === 'normality') {
          const res = await getFeatureDistribution(selectedFeature);
          setDistData(res);
        } else if (activeTab === 'zscore') {
          const res = await getZScoreAnalysis(selectedFeature, selectedCondition);
          setZscoreData(res);
        } else if (activeTab === 'multivariate' || activeTab === 'bayesian') {
          const res = await getMultivariateAnalytics('rms', 'kurtosis');
          setMultiData(res);
        } else if (activeTab === 'educational') {
          const res = await getEducationalDemos();
          setEduData(res);
        }
      } catch (err) {
        console.error('Failed to load distribution analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadTabContent();
  }, [activeTab, selectedFeature, selectedCondition]);

  return (
    <div className="space-y-6">
      {/* Header and Sub-tab Navigation */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
              <span>PROBABILITY DISTRIBUTIONS & STATISTICAL INFERENCE</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Rigorous empirical distributions, normality assumption checks, Z-scores, bivariate joint PMF, and Bayesian diagnostic updates.
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-2 border-t border-industrial-border/60 pt-3 overflow-x-auto no-scrollbar">
          {[
            { id: 'normality', label: 'Empirical vs Normal PDF' },
            { id: 'zscore', label: 'Z-Scores & SPC Limits' },
            { id: 'multivariate', label: 'Covariance & 2D Joint PMF' },
            { id: 'bayesian', label: 'Bayesian Condition Probabilities' },
            { id: 'educational', label: 'Educational Demos (Binomial / Poisson / MGF)' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono whitespace-nowrap transition ${
                activeTab === tab.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                  : 'text-slate-400 hover:text-white hover:bg-industrial-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* TAB 1: NORMALITY ASSUMPTION & EMPIRICAL PDF/CDF */}
          {activeTab === 'normality' && distData && (
            <div className="space-y-6">
              {/* Hypothesis Testing Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
                  <div className="flex justify-between text-xs text-slate-400 font-mono">
                    <span>SHAPIRO-WILK TEST</span>
                    <span className="text-red-400 font-bold">REJECTED</span>
                  </div>
                  <div className="text-xl font-bold font-mono text-white">
                    W = {distData.normality_testing.shapiro_wilk.statistic_W.toFixed(4)}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">
                    p-value: {distData.normality_testing.shapiro_wilk.p_value.toExponential(3)} (alpha=0.05)
                  </p>
                </div>

                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
                  <div className="flex justify-between text-xs text-slate-400 font-mono">
                    <span>D'AGOSTINO-PEARSON (K^2)</span>
                    <span className="text-red-400 font-bold">REJECTED</span>
                  </div>
                  <div className="text-xl font-bold font-mono text-white">
                    K^2 = {distData.normality_testing.dagostino_pearson.statistic_K2.toFixed(2)}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">
                    p-value: {distData.normality_testing.dagostino_pearson.p_value.toExponential(3)} (alpha=0.05)
                  </p>
                </div>

                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
                  <div className="flex justify-between text-xs text-slate-400 font-mono">
                    <span>KOLMOGOROV-SMIRNOV</span>
                    <span className="text-red-400 font-bold">REJECTED</span>
                  </div>
                  <div className="text-xl font-bold font-mono text-white">
                    D = {distData.normality_testing.kolmogorov_smirnov.statistic_D.toFixed(4)}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">
                    p-value: {distData.normality_testing.kolmogorov_smirnov.p_value.toExponential(3)}
                  </p>
                </div>
              </div>

              {/* Explanatory banner */}
              <div className="bg-industrial-900/60 border border-amber-500/30 rounded-xl p-4 text-xs text-slate-300">
                <span className="font-bold text-amber-400 font-mono block mb-1">
                  CRITICAL ENGINEERING INSIGHT: WHY BEARING VIBRATION REJECTS NORMALITY
                </span>
                {distData.normality_testing.engineering_interpretation}
              </div>

              {/* PDF Chart: Empirical Histogram vs Theoretical Gaussian */}
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-white tracking-wider font-mono">
                    EMPIRICAL DENSITY HISTOGRAM VS THEORETICAL GAUSSIAN OVERLAY: {selectedFeature.toUpperCase()}
                  </h3>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono text-slate-400">Feature:</span>
                    <select
                      value={selectedFeature}
                      onChange={(e) => setSelectedFeature(e.target.value)}
                      className="bg-industrial-950 border border-industrial-border rounded px-2 py-1 text-xs font-mono text-cyan-300"
                    >
                      <option value="rms">RMS</option>
                      <option value="kurtosis">KURTOSIS</option>
                      <option value="variance">VARIANCE</option>
                      <option value="peak_to_peak">PEAK-TO-PEAK</option>
                    </select>
                  </div>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distData.distribution_curves.histogram_points}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                      <XAxis dataKey="bin_center" stroke="#64748b" fontSize={10} tickFormatter={(v) => v.toFixed(3)} />
                      <YAxis stroke="#64748b" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Bar dataKey="empirical_density" fill="#38bdf8" name="Actual Empirical Density" radius={[3, 3, 0, 0]} />
                      <Line type="monotone" dataKey="theoretical_density" stroke="#f43f5e" strokeWidth={2} dot={false} name="Theoretical Normal N(mu, sigma^2)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Cumulative Distribution Function (CDF) */}
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
                <h3 className="text-xs font-bold text-white tracking-wider font-mono">
                  CUMULATIVE DISTRIBUTION FUNCTION F(x) = P(X &le; x)
                </h3>
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={distData.distribution_curves.cdf_points}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                      <XAxis dataKey="x" stroke="#64748b" fontSize={10} tickFormatter={(v) => v.toFixed(3)} />
                      <YAxis stroke="#64748b" fontSize={10} domain={[0, 1]} />
                      <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Line type="monotone" dataKey="empirical_cdf" stroke="#38bdf8" strokeWidth={2} dot={false} name="Empirical CDF" />
                      <Line type="monotone" dataKey="theoretical_cdf" stroke="#a855f7" strokeDasharray="4 4" strokeWidth={2} dot={false} name="Theoretical Gaussian CDF" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Z-SCORES & STATISTICAL PROCESS CONTROL */}
          {activeTab === 'zscore' && zscoreData && (
            <div className="space-y-6">
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                    STANDARDIZED Z-SCORE STATISTICAL PROCESS CONTROL (SPC)
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Z = (X - mu_baseline) / sigma_baseline against Healthy Baseline (Load 0-3 HP)
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-mono text-slate-400">Evaluate:</span>
                  <select
                    value={selectedCondition}
                    onChange={(e) => setSelectedCondition(e.target.value)}
                    className="bg-industrial-950 border border-industrial-border rounded px-3 py-1.5 text-xs font-mono text-cyan-400"
                  >
                    <option value="Healthy">Healthy (Baseline)</option>
                    <option value="Inner Race Fault">Inner Race Fault</option>
                    <option value="Ball Fault">Ball Fault</option>
                    <option value="Outer Race Fault">Outer Race Fault</option>
                  </select>
                </div>
              </div>

              {/* Z-score SPC Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 font-mono block">SPC CONTROL STATE</span>
                  <span className={`text-base font-bold font-mono ${
                    zscoreData.spc_state === 'IN_CONTROL' ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {zscoreData.spc_state}
                  </span>
                </div>
                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 font-mono block">MEAN Z-SCORE</span>
                  <span className="text-xl font-bold font-mono text-white">{zscoreData.mean_z_score.toFixed(2)} sigma</span>
                </div>
                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 font-mono block">2-SIGMA WARNING EXCEEDANCE</span>
                  <span className="text-xl font-bold font-mono text-amber-400">{zscoreData.exceed_2sigma_pct}%</span>
                </div>
                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
                  <span className="text-[10px] text-slate-400 font-mono block">3-SIGMA CRITICAL ALARMS</span>
                  <span className="text-xl font-bold font-mono text-red-400">{zscoreData.exceed_3sigma_pct}%</span>
                </div>
              </div>

              {/* Engineering note */}
              <div className="bg-industrial-900/60 border border-industrial-border rounded-xl p-4 text-xs text-slate-300">
                <span className="font-bold text-cyan-400 font-mono block mb-1">SHEWHART CONTROL LIMIT RULES</span>
                {zscoreData.engineering_significance}
              </div>
            </div>
          )}

          {/* TAB 3: COVARIANCE & 2D JOINT PROBABILITY DISTRIBUTION */}
          {activeTab === 'multivariate' && multiData && (
            <div className="space-y-6">
              {/* 2D Joint PMF Grid */}
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                      2D BIVARIATE JOINT PROBABILITY DISTRIBUTION P(RMS, KURTOSIS)
                    </h3>
                    <p className="text-xs text-slate-400">
                      Law of Total Probability: sum_x sum_y P(X=x, Y=y) = {multiData.joint_and_marginal.law_of_total_probability_sum.toFixed(4)}
                    </p>
                  </div>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 10, left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                      <XAxis type="number" dataKey="x" name="RMS" stroke="#64748b" fontSize={10} unit=" g" />
                      <YAxis type="number" dataKey="y" name="Kurtosis" stroke="#64748b" fontSize={10} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }}
                        formatter={(val, name) => [val, name]}
                      />
                      <Scatter 
                        name="Joint State Probability" 
                        data={multiData.joint_and_marginal.joint_grid} 
                        fill="#38bdf8" 
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Correlation Matrix Table */}
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
                <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                  8x8 PEARSON CORRELATION MATRIX (rho_xy)
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-center text-[10px] font-mono">
                    <thead className="bg-industrial-950 text-slate-400 border-b border-industrial-border">
                      <tr>
                        <th className="p-2 text-left">Feature</th>
                        {multiData.covariance_and_correlation.features.map(f => (
                          <th key={f} className="p-2 uppercase">{f}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-industrial-border/40">
                      {multiData.covariance_and_correlation.correlation_matrix.map((row, i) => (
                        <tr key={i}>
                          <td className="p-2 text-left font-bold text-cyan-300 uppercase">
                            {multiData.covariance_and_correlation.features[i]}
                          </td>
                          {row.map((val, j) => {
                            const isDiag = i === j;
                            const isHigh = Math.abs(val) > 0.8 && !isDiag;
                            return (
                              <td 
                                key={j} 
                                className={`p-2 ${
                                  isDiag ? 'bg-cyan-950/40 text-cyan-400 font-bold' : 
                                  isHigh ? 'bg-amber-950/30 text-amber-300 font-bold' : 'text-slate-300'
                                }`}
                              >
                                {val.toFixed(2)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: BAYESIAN CONDITIONAL PROBABILITY */}
          {activeTab === 'bayesian' && multiData && (
            <div className="space-y-6">
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
                <div>
                  <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                    BAYESIAN DIAGNOSTIC UPDATE: P(FAULT_MODE | RMS &gt; THRESHOLD)
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Formal application of Bayes' rule in condition-based maintenance
                  </p>
                </div>

                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={multiData.bayesian_conditioning.threshold_evaluations}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                      <XAxis dataKey="threshold" stroke="#64748b" fontSize={10} unit=" g" />
                      <YAxis stroke="#64748b" fontSize={10} domain={[0, 1]} />
                      <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Line type="monotone" dataKey="posterior_P_class_given_exceed.Healthy" stroke="#10b981" strokeWidth={2} name="P(Healthy | RMS > tau)" />
                      <Line type="monotone" dataKey="posterior_P_class_given_exceed.Inner Race Fault" stroke="#f59e0b" strokeWidth={2} name="P(Inner Race | RMS > tau)" />
                      <Line type="monotone" dataKey="posterior_P_class_given_exceed.Ball Fault" stroke="#8b5cf6" strokeWidth={2} name="P(Ball Fault | RMS > tau)" />
                      <Line type="monotone" dataKey="posterior_P_class_given_exceed.Outer Race Fault" stroke="#ef4444" strokeWidth={2} name="P(Outer Race | RMS > tau)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-industrial-950 p-4 rounded-lg border border-industrial-border text-xs text-slate-300">
                  <span className="font-bold text-cyan-400 font-mono block mb-1">BAYES' THEOREM INTERPRETATION</span>
                  {multiData.bayesian_conditioning.engineering_significance}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: EDUCATIONAL DEMONSTRATIONS (Binomial, Poisson, MGF, CF) */}
          {activeTab === 'educational' && eduData && (
            <div className="space-y-6">
              {/* Binomial Demo */}
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                      1. BINOMIAL DISTRIBUTION: MULTI-WINDOW PERSISTENCE ALARM FILTER
                    </h3>
                    <p className="text-xs text-slate-400">
                      P(K = k) = C(10, k) * p^k * (1-p)^(10-k) comparing Healthy (p=0.05) vs Fault (p=0.90)
                    </p>
                  </div>
                </div>

                <div className="h-52 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={eduData.binomial_persistence.distribution_table}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                      <XAxis dataKey="k_alarms" stroke="#64748b" fontSize={10} name="Exceedance Windows k" />
                      <YAxis stroke="#64748b" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Bar dataKey="p_healthy" fill="#10b981" name="Healthy (p=0.05)" />
                      <Bar dataKey="p_fault" fill="#ef4444" name="Fault State (p=0.90)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-slate-300 bg-industrial-950 p-3 rounded border border-industrial-border">
                  {eduData.binomial_persistence.engineering_explanation}
                </p>
              </div>

              {/* Poisson Demo */}
              <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                      2. POISSON DISTRIBUTION: SHOCK IMPULSE ARRIVAL RATES
                    </h3>
                    <p className="text-xs text-slate-400">
                      Arrival rate of defect strikes per unit time: lambda_healthy=0.5/s vs lambda_fault=8.0/s
                    </p>
                  </div>
                </div>

                <div className="h-52 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={eduData.poisson_shock_rate.distribution_table}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                      <XAxis dataKey="k_shocks" stroke="#64748b" fontSize={10} />
                      <YAxis stroke="#64748b" fontSize={10} />
                      <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px' }} />
                      <Bar dataKey="prob_healthy" fill="#10b981" name="Healthy (lambda = 0.5)" />
                      <Bar dataKey="prob_fault" fill="#a855f7" name="Defect Spall (lambda = 8.0)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-xs text-slate-300 bg-industrial-950 p-3 rounded border border-industrial-border">
                  {eduData.poisson_shock_rate.engineering_explanation}
                </p>
              </div>

              {/* MGF & Characteristic Function Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                    3. MOMENT GENERATING FUNCTION (MGF)
                  </h3>
                  <code className="text-xs text-cyan-400 font-mono block bg-industrial-950 p-2 rounded">
                    M_X(t) = E[e^(tX)] = exp(mu*t + 0.5*sigma^2*t^2)
                  </code>
                  <p className="text-xs text-slate-300">
                    Evaluating derivatives at t=0 recovers all physical moments: M'(0) = E[X] (Mean DC), M''(0) = E[X^2] (Power).
                  </p>
                </div>

                <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
                  <h3 className="text-sm font-bold text-white tracking-wider font-mono">
                    4. CHARACTERISTIC FUNCTION
                  </h3>
                  <code className="text-xs text-purple-400 font-mono block bg-industrial-950 p-2 rounded">
                    phi_X(t) = E[e^(i*t*X)] (Fourier Transform of PDF)
                  </code>
                  <p className="text-xs text-slate-300">
                    Bounded (|phi(t)| &le; 1). Enables direct spectral addition: the characteristic function of combined independent vibration sources is the product of their individual functions.
                  </p>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
