import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  CheckCircle, 
  Layers, 
  Sliders, 
  BarChart2, 
  Sparkles, 
  AlertTriangle,
  RotateCcw,
  Zap
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { getModelMetrics, getFeatureImportance, predictFeatures } from '../api/client';

export default function PredictionsSection({ activeModel, onSelectModel }) {
  const [metricsData, setMetricsData] = useState(null);
  const [featureRankings, setFeatureRankings] = useState([]);
  const [loading, setLoading] = useState(true);

  // Custom Simulator state
  const [simFeatures, setSimFeatures] = useState({
    mean: 0.01,
    variance: 0.08,
    std: 0.28,
    rms: 0.28,
    skewness: 0.15,
    kurtosis: 4.5,
    peak_to_peak: 2.1,
    crest_factor: 3.8
  });
  const [simPrediction, setSimPrediction] = useState(null);
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const m = await getModelMetrics();
        setMetricsData(m);
        const fi = await getFeatureImportance();
        setFeatureRankings(fi.features_ranked || []);
        
        // Initial simulation prediction
        const pred = await predictFeatures(simFeatures, activeModel);
        setSimPrediction(pred);
      } catch (err) {
        console.error('Failed to load ML metrics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [activeModel]);

  const handleSimulate = async () => {
    try {
      setSimulating(true);
      const res = await predictFeatures(simFeatures, activeModel);
      setSimPrediction(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handlePreset = (type) => {
    let preset = {};
    if (type === 'healthy') {
      preset = { mean: 0.01, variance: 0.005, std: 0.07, rms: 0.07, skewness: -0.05, kurtosis: 3.1, peak_to_peak: 0.55, crest_factor: 3.9 };
    } else if (type === 'inner') {
      preset = { mean: 0.01, variance: 0.09, std: 0.30, rms: 0.30, skewness: 0.25, kurtosis: 5.5, peak_to_peak: 2.8, crest_factor: 4.6 };
    } else if (type === 'ball') {
      preset = { mean: 0.01, variance: 0.02, std: 0.14, rms: 0.14, skewness: 0.08, kurtosis: 3.8, peak_to_peak: 1.2, crest_factor: 4.2 };
    } else {
      preset = { mean: 0.01, variance: 0.36, std: 0.60, rms: 0.60, skewness: 0.10, kurtosis: 4.8, peak_to_peak: 4.8, crest_factor: 4.0 };
    }
    setSimFeatures(preset);
  };

  if (loading || !metricsData) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
      </div>
    );
  }

  const { metrics, split_info } = metricsData;
  const rf = metrics.models.RandomForest;
  const lr = metrics.models.LogisticRegression;

  return (
    <div className="space-y-6">
      {/* Header & Leakage Prevention Notice */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>SUPERVISED MACHINE LEARNING & MODEL BENCHMARKING</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Evaluated on unseen experimental recordings (Load 3 HP holdout) with zero window or recording leakage.
          </p>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="text-slate-400">Train: {split_info.train_samples} win (12 recs)</span>
          <span className="text-slate-600">|</span>
          <span className="text-cyan-400">Test: {split_info.test_samples} win (4 recs)</span>
        </div>
      </div>

      {/* Model Comparison Table */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-white tracking-wider font-mono">
          UNSEEN TEST RECORDINGS COMPARATIVE METRICS (LOAD 3 HP HOLDOUT)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-industrial-950 text-slate-400 border-b border-industrial-border">
              <tr>
                <th className="p-3">Classifier Model</th>
                <th className="p-3">Train Acc</th>
                <th className="p-3">Test Acc</th>
                <th className="p-3">Macro Precision</th>
                <th className="p-3">Macro Recall</th>
                <th className="p-3">Macro F1-Score</th>
                <th className="p-3">Weighted F1</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-industrial-border/60">
              <tr className="hover:bg-industrial-800/40">
                <td className="p-3 font-bold text-cyan-400 flex items-center space-x-2">
                  <span>Random Forest (100 Trees)</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300">Default</span>
                </td>
                <td className="p-3 text-slate-200">{(rf.train_accuracy * 100).toFixed(2)}%</td>
                <td className="p-3 font-bold text-emerald-400">{(rf.test_accuracy * 100).toFixed(2)}%</td>
                <td className="p-3 text-slate-200">{(rf.precision_macro * 100).toFixed(2)}%</td>
                <td className="p-3 text-slate-200">{(rf.recall_macro * 100).toFixed(2)}%</td>
                <td className="p-3 font-bold text-cyan-300">{rf.f1_macro.toFixed(4)}</td>
                <td className="p-3 text-slate-200">{rf.f1_weighted.toFixed(4)}</td>
              </tr>
              <tr className="hover:bg-industrial-800/40">
                <td className="p-3 font-bold text-purple-400">Logistic Regression (L2 Multinomial)</td>
                <td className="p-3 text-slate-200">{(lr.train_accuracy * 100).toFixed(2)}%</td>
                <td className="p-3 font-bold text-emerald-400">{(lr.test_accuracy * 100).toFixed(2)}%</td>
                <td className="p-3 text-slate-200">{(lr.precision_macro * 100).toFixed(2)}%</td>
                <td className="p-3 text-slate-200">{(lr.recall_macro * 100).toFixed(2)}%</td>
                <td className="p-3 font-bold text-purple-300">{lr.f1_macro.toFixed(4)}</td>
                <td className="p-3 text-slate-200">{lr.f1_weighted.toFixed(4)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* 4x4 Confusion Matrices Side-by-Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Random Forest CM */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
          <div className="flex justify-between items-center">
            <h4 className="text-xs font-bold font-mono text-cyan-400 uppercase">
              Random Forest — 4x4 Confusion Matrix
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">Row-Normalized %</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs font-mono">
              <thead className="bg-industrial-950 text-slate-400">
                <tr>
                  <th className="p-2 text-left">Actual \ Pred</th>
                  <th className="p-2">Healthy</th>
                  <th className="p-2">Inner</th>
                  <th className="p-2">Ball</th>
                  <th className="p-2">Outer</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-industrial-border/60">
                {rf.confusion_matrix_normalized.map((row, rIdx) => (
                  <tr key={rIdx}>
                    <td className="p-2 text-left font-bold text-slate-300">
                      {['Healthy', 'Inner', 'Ball', 'Outer'][rIdx]}
                    </td>
                    {row.map((val, cIdx) => {
                      const isCorrect = rIdx === cIdx;
                      return (
                        <td 
                          key={cIdx} 
                          className={`p-2 font-bold ${
                            isCorrect 
                              ? (val > 0.95 ? 'bg-emerald-950/60 text-emerald-300' : 'bg-cyan-950/40 text-cyan-300') 
                              : (val > 0.05 ? 'bg-red-950/40 text-red-400' : 'text-slate-600')
                          }`}
                        >
                          {(val * 100).toFixed(1)}%
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Logistic Regression CM */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
          <div className="flex justify-between items-center">
            <h4 className="text-xs font-bold font-mono text-purple-400 uppercase">
              Logistic Regression — 4x4 Confusion Matrix
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">Row-Normalized %</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs font-mono">
              <thead className="bg-industrial-950 text-slate-400">
                <tr>
                  <th className="p-2 text-left">Actual \ Pred</th>
                  <th className="p-2">Healthy</th>
                  <th className="p-2">Inner</th>
                  <th className="p-2">Ball</th>
                  <th className="p-2">Outer</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-industrial-border/60">
                {lr.confusion_matrix_normalized.map((row, rIdx) => (
                  <tr key={rIdx}>
                    <td className="p-2 text-left font-bold text-slate-300">
                      {['Healthy', 'Inner', 'Ball', 'Outer'][rIdx]}
                    </td>
                    {row.map((val, cIdx) => {
                      const isCorrect = rIdx === cIdx;
                      return (
                        <td 
                          key={cIdx} 
                          className={`p-2 font-bold ${
                            isCorrect 
                              ? (val > 0.95 ? 'bg-emerald-950/60 text-emerald-300' : 'bg-cyan-950/40 text-cyan-300') 
                              : (val > 0.05 ? 'bg-red-950/40 text-red-400' : 'text-slate-600')
                          }`}
                        >
                          {(val * 100).toFixed(1)}%
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

      {/* Feature Importance Rankings Chart */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-white tracking-wider font-mono">
          FEATURE IMPORTANCE RANKINGS (MEAN DECREASE IN IMPURITY - MDI)
        </h3>
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={featureRankings} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
              <XAxis type="number" stroke="#64748b" fontSize={10} domain={[0, 0.3]} />
              <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={10} />
              <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
              <Bar dataKey="random_forest_importance" fill="#38bdf8" name="Random Forest Importance" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Interactive Custom Vibration Simulator */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-industrial-border/60 pb-3">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wider font-mono flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>INTERACTIVE CUSTOM VIBRATION INFERENCE SIMULATOR</span>
            </h3>
            <p className="text-xs text-slate-400">
              Tune arbitrary 8-feature values and evaluate real-time class probability outputs.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-slate-400">Presets:</span>
            <button onClick={() => handlePreset('healthy')} className="px-2 py-1 rounded bg-industrial-950 hover:bg-industrial-800 text-xs font-mono text-emerald-400 border border-industrial-border">Healthy</button>
            <button onClick={() => handlePreset('inner')} className="px-2 py-1 rounded bg-industrial-950 hover:bg-industrial-800 text-xs font-mono text-amber-400 border border-industrial-border">Inner</button>
            <button onClick={() => handlePreset('ball')} className="px-2 py-1 rounded bg-industrial-950 hover:bg-industrial-800 text-xs font-mono text-purple-400 border border-industrial-border">Ball</button>
            <button onClick={() => handlePreset('outer')} className="px-2 py-1 rounded bg-industrial-950 hover:bg-industrial-800 text-xs font-mono text-red-400 border border-industrial-border">Outer</button>
          </div>
        </div>

        {/* Sliders & Prediction Result */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sliders Column */}
          <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.keys(simFeatures).map((feat) => (
              <div key={feat} className="bg-industrial-950 p-3 rounded-lg border border-industrial-border space-y-1.5">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400 uppercase">{feat}:</span>
                  <span className="font-bold text-cyan-400">{simFeatures[feat]}</span>
                </div>
                <input
                  type="number"
                  step="0.01"
                  value={simFeatures[feat]}
                  onChange={(e) => setSimFeatures({ ...simFeatures, [feat]: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-industrial-900 border border-industrial-border rounded px-2 py-1 text-xs font-mono text-white"
                />
              </div>
            ))}
            <div className="sm:col-span-2">
              <button
                onClick={handleSimulate}
                disabled={simulating}
                className="w-full py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition shadow-md shadow-cyan-600/20"
              >
                {simulating ? 'RUNNING INFERENCE...' : 'RUN REAL-TIME INFERENCE'}
              </button>
            </div>
          </div>

          {/* Real-time Result Column */}
          {simPrediction && (
            <div className="bg-industrial-950 border border-industrial-border rounded-xl p-5 space-y-4 flex flex-col justify-between">
              <div>
                <span className="text-[10px] text-slate-400 font-mono block">SIMULATED DIAGNOSIS</span>
                <span className="text-xl font-bold font-mono text-cyan-400 block mt-1">
                  {simPrediction.predicted_condition}
                </span>
                <div className="flex justify-between text-xs font-mono text-slate-300 mt-2">
                  <span>Confidence:</span>
                  <span className="font-bold text-emerald-400">{(simPrediction.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-xs font-mono text-slate-300 mt-1">
                  <span>Severity Index:</span>
                  <span className="font-bold text-amber-400">{simPrediction.severity_index} / 100</span>
                </div>
              </div>

              {/* Probabilities list */}
              <div className="space-y-2 border-t border-industrial-border/60 pt-3">
                <span className="text-[10px] text-slate-400 font-mono block">Class Probabilities:</span>
                {Object.entries(simPrediction.probabilities).map(([cond, prob]) => (
                  <div key={cond} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-300">{cond}</span>
                      <span className="text-white font-bold">{(prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-industrial-900 h-1.5 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-cyan-400" 
                        style={{ width: `${Math.max(2, prob * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
