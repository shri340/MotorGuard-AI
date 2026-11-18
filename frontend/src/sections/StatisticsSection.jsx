import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Layers, 
  HelpCircle, 
  TrendingUp, 
  Activity, 
  Sliders,
  CheckCircle,
  FileSpreadsheet
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
import { getMathOverview, getConditionComparison } from '../api/client';

export default function StatisticsSection() {
  const [overview, setOverview] = useState([]);
  const [selectedFeature, setSelectedFeature] = useState('rms');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const overData = await getMathOverview();
        setOverview(overData.features || []);
        const compData = await getConditionComparison(selectedFeature);
        setComparison(compData);
      } catch (err) {
        console.error('Failed to load statistical overview:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [selectedFeature]);

  const FEATURE_DESCRIPTIONS = {
    mean: {
      formula: 'E[X] = (1/N) * sum(x_i)',
      desc: 'Reflects steady-state DC drift, sensor orientation offset, or asymmetric shaft displacement under load.'
    },
    variance: {
      formula: 'Var(X) = (1/(N-1)) * sum((x_i - mu)^2)',
      desc: 'Total AC signal power fluctuating about the mean; scales with kinetic vibration energy.'
    },
    std: {
      formula: 'sigma = sqrt(Var(X))',
      desc: 'Amplitude dispersion in acceleration units (g). Directly measures dynamic oscillatory severity.'
    },
    rms: {
      formula: 'RMS = sqrt((1/N) * sum(x_i^2))',
      desc: 'ISO 10816 root mean square energy standard; reliable indicator of continuous destructive wear.'
    },
    skewness: {
      formula: 'S = E[(X - mu)^3] / sigma^3',
      desc: 'Measures probability density asymmetry. Healthy bearings show S ~ 0; single-sided impacts induce skew.'
    },
    kurtosis: {
      formula: 'K = E[(X - mu)^4] / sigma^4',
      desc: 'Pearson 4th moment (Normal=3.0). Localized fatigue spalls produce sharp spikes, causing K >> 4.'
    },
    peak_to_peak: {
      formula: 'P2P = max(X) - min(X)',
      desc: 'Total instantaneous dynamic envelope span; highly sensitive to extreme transient shocks.'
    },
    crest_factor: {
      formula: 'CF = max(|X|) / RMS',
      desc: 'Impulsiveness ratio. Early stage spalls exhibit high crest factor before overall RMS energy elevates.'
    }
  };

  if (loading && !comparison) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto" />
          <p className="text-xs font-mono text-slate-400">Loading statistical moments...</p>
        </div>
      </div>
    );
  }

  // Build chart data comparing the selected feature across the 4 conditions
  const chartData = comparison ? Object.entries(comparison.conditions).map(([cond, data]) => ({
    condition: cond,
    mean: Number(data.moments.expectation_E_X.toFixed(4)),
    std: Number(data.moments.standard_deviation_sigma.toFixed(4)),
    median: Number(data.moments.median.toFixed(4)),
    kurtosis: Number(data.moments.pearson_kurtosis.toFixed(2))
  })) : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            <span>ENGINEERING STATISTICAL ANALYSIS ENGINE</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Exact time-domain moments computed across 3,064 experimental CWRU 2048-sample windows.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono text-slate-400">Focus Feature:</span>
          <select
            value={selectedFeature}
            onChange={(e) => setSelectedFeature(e.target.value)}
            className="bg-industrial-950 border border-industrial-border rounded-lg px-3 py-1.5 text-xs font-mono text-cyan-400 focus:outline-none focus:border-cyan-500"
          >
            {Object.keys(FEATURE_DESCRIPTIONS).map((feat) => (
              <option key={feat} value={feat}>{feat.toUpperCase()}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Feature Formula & Physics Context Card */}
      <div className="bg-industrial-900/60 border border-cyan-500/30 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold font-mono text-cyan-400 uppercase">{selectedFeature}</span>
            <code className="text-[11px] px-2 py-0.5 rounded bg-industrial-950 text-slate-300 font-mono border border-industrial-border">
              {FEATURE_DESCRIPTIONS[selectedFeature]?.formula}
            </code>
          </div>
          <p className="text-xs text-slate-300">
            {FEATURE_DESCRIPTIONS[selectedFeature]?.desc}
          </p>
        </div>
      </div>

      {/* Cross-Condition Comparison Chart */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wider font-mono">
              CONDITION-SEPARATED MOMENTS COMPARISON: {selectedFeature.toUpperCase()}
            </h3>
            <p className="text-xs text-slate-400">Expectation (Mean) vs Dispersion (Std Dev) across bearing states</p>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
              <XAxis dataKey="condition" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Bar dataKey="mean" name="Expectation E[X]" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="std" name="Std Dev (Dispersion)" fill="#818cf8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="median" name="Median (50th %)" fill="#34d399" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Complete 8-Feature Master Table */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white tracking-wider font-mono flex items-center space-x-2">
            <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
            <span>FULL EXPERIMENTAL DATASET MOMENTS SUMMARY (N = 3,064)</span>
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">D'Agostino-Pearson Hypothesis Testing</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-industrial-950 text-slate-400 border-b border-industrial-border">
              <tr>
                <th className="p-3">Feature Name</th>
                <th className="p-3">Expectation E[X]</th>
                <th className="p-3">Std Dev (sigma)</th>
                <th className="p-3">Variance Var(X)</th>
                <th className="p-3">Skewness (3rd)</th>
                <th className="p-3">Pearson Kurtosis</th>
                <th className="p-3">Normality p-value</th>
                <th className="p-3">Gaussian Assumption</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-industrial-border/60">
              {overview.map((f) => (
                <tr 
                  key={f.feature} 
                  className={`hover:bg-industrial-800/40 transition cursor-pointer ${
                    selectedFeature === f.feature ? 'bg-cyan-500/10' : ''
                  }`}
                  onClick={() => setSelectedFeature(f.feature)}
                >
                  <td className="p-3 font-bold text-cyan-300 uppercase">{f.feature}</td>
                  <td className="p-3 text-slate-200">{f.mean.toFixed(5)}</td>
                  <td className="p-3 text-slate-200">{f.std.toFixed(5)}</td>
                  <td className="p-3 text-slate-200">{f.variance.toFixed(6)}</td>
                  <td className="p-3 text-slate-200">{f.skewness.toFixed(3)}</td>
                  <td className={`p-3 font-semibold ${f.kurtosis > 4.0 ? 'text-amber-400' : 'text-slate-200'}`}>
                    {f.kurtosis.toFixed(2)}
                  </td>
                  <td className="p-3 text-slate-400">{f.normality_p_value.toExponential(2)}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950/60 text-red-400 border border-red-800/50">
                      REJECTED (p &lt; 0.05)
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
