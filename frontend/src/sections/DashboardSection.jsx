import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  ShieldAlert, 
  Cpu, 
  ArrowRight, 
  Gauge, 
  Radio, 
  RotateCcw,
  Zap
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import { getPlaybackWindow, getHistoryStats } from '../api/client';

export default function DashboardSection({ onNavigate, activeModel }) {
  const [currentStep, setCurrentStep] = useState(null);
  const [historyStats, setHistoryStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadInitial() {
      try {
        setLoading(true);
        // Load default healthy window for baseline dashboard view
        const step = await getPlaybackWindow(97, 0, activeModel, false, 128);
        setCurrentStep(step);
        const stats = await getHistoryStats();
        setHistoryStats(stats);
      } catch (err) {
        console.error('Failed to load dashboard telemetry:', err);
      } finally {
        setLoading(false);
      }
    }
    loadInitial();
  }, [activeModel]);

  if (loading || !currentStep) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto" />
          <p className="text-sm font-mono text-slate-400">Loading MotorGuard AI System Telemetry...</p>
        </div>
      </div>
    );
  }

  const { features, prediction, ground_truth_condition, motor_rpm, ground_truth_load_hp, waveform } = currentStep;
  const isHealthy = prediction.predicted_condition === 'Healthy';
  const severity = prediction.severity_index || 15.0;

  const getStatusBadge = (status) => {
    switch (status) {
      case 'OPTIMAL':
        return <span className="px-2.5 py-1 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold flex items-center space-x-1.5"><CheckCircle className="w-3.5 h-3.5" /><span>OPTIMAL (CLASS A)</span></span>;
      case 'CAUTION':
        return <span className="px-2.5 py-1 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30 text-xs font-mono font-bold flex items-center space-x-1.5"><AlertTriangle className="w-3.5 h-3.5" /><span>CAUTION (CLASS B)</span></span>;
      case 'WARNING':
        return <span className="px-2.5 py-1 rounded bg-orange-500/15 text-orange-400 border border-orange-500/30 text-xs font-mono font-bold flex items-center space-x-1.5"><AlertTriangle className="w-3.5 h-3.5" /><span>WARNING (CLASS C)</span></span>;
      default:
        return <span className="px-2.5 py-1 rounded bg-red-500/15 text-red-400 border border-red-500/30 text-xs font-mono font-bold flex items-center space-x-1.5"><ShieldAlert className="w-3.5 h-3.5" /><span>CRITICAL (CLASS D)</span></span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Notice */}
      <div className="bg-industrial-900 border border-cyan-500/30 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-lg shadow-cyan-950/20">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white tracking-wide">CWRU Experimental Drive-End Motor Test Rig</h2>
              <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700/50 font-mono">12 kHz Sampling</span>
            </div>
            <p className="text-xs text-slate-400">
              Recorded experimental vibration signals from Case Western Reserve University Bearing Data Center (Reliance Electric 2 HP motor).
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => onNavigate('monitoring')}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold font-mono transition shadow-md shadow-cyan-500/20"
          >
            <span>LAUNCH PLAYBACK</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: RMS */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>RMS VIBRATION ENERGY</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-white">{features.rms.toFixed(4)}</span>
            <span className="text-xs text-slate-400">g RMS</span>
          </div>
          <div className="w-full bg-industrial-950 h-1.5 rounded-full overflow-hidden">
            <div 
              className={`h-full ${features.rms > 0.25 ? 'bg-red-500' : features.rms > 0.12 ? 'bg-amber-400' : 'bg-emerald-400'}`} 
              style={{ width: `${Math.min(100, (features.rms / 0.8) * 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>Baseline: &lt; 0.10 g</span>
            <span>Alarm: &gt; 0.25 g</span>
          </div>
        </div>

        {/* Metric 2: Kurtosis */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>PEARSON KURTOSIS</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-white">{features.kurtosis.toFixed(2)}</span>
            <span className="text-xs text-slate-400">Normal = 3.0</span>
          </div>
          <div className="w-full bg-industrial-950 h-1.5 rounded-full overflow-hidden">
            <div 
              className={`h-full ${features.kurtosis > 5.0 ? 'bg-red-500' : features.kurtosis > 3.8 ? 'bg-amber-400' : 'bg-emerald-400'}`} 
              style={{ width: `${Math.min(100, (features.kurtosis / 10.0) * 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>Excess: {(features.kurtosis - 3.0).toFixed(2)}</span>
            <span>{features.kurtosis > 4.5 ? 'Heavy Impulse Spikes' : 'Mesokurtic'}</span>
          </div>
        </div>

        {/* Metric 3: Peak-to-Peak */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>PEAK-TO-PEAK SPAN</span>
            <Gauge className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-white">{features.peak_to_peak.toFixed(3)}</span>
            <span className="text-xs text-slate-400">g dynamic</span>
          </div>
          <div className="w-full bg-industrial-950 h-1.5 rounded-full overflow-hidden">
            <div 
              className="h-full bg-cyan-400" 
              style={{ width: `${Math.min(100, (features.peak_to_peak / 6.0) * 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>Crest Factor: {features.crest_factor.toFixed(2)}</span>
            <span>Variance: {features.variance.toFixed(4)}</span>
          </div>
        </div>

        {/* Metric 4: Motor Speed & Load */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>OPERATING MOTOR LOAD</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-white">{motor_rpm.toFixed(0)}</span>
            <span className="text-xs text-slate-400">RPM</span>
          </div>
          <div className="flex items-center justify-between pt-1">
            <span className="text-xs px-2 py-0.5 rounded bg-industrial-800 text-slate-300 font-mono">Load: {ground_truth_load_hp} HP</span>
            <span className="text-xs text-slate-400 font-mono">{(motor_rpm / 60).toFixed(1)} Hz shaft</span>
          </div>
        </div>
      </div>

      {/* Main Condition Diagnostic & Severity Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Health Severity & Status Card */}
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-6 flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white tracking-wider font-mono">MACHINE HEALTH RATING</h3>
            {getStatusBadge(prediction.health_status)}
          </div>

          <div className="space-y-3">
            <div className="flex items-baseline justify-between">
              <span className="text-xs text-slate-400 font-mono">ISO 10816 Severity Index:</span>
              <span className="text-3xl font-extrabold font-mono text-white">{severity.toFixed(1)}<span className="text-sm text-slate-400 font-normal"> / 100</span></span>
            </div>
            <div className="w-full bg-industrial-950 h-3 rounded-full overflow-hidden p-0.5 border border-industrial-border">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  severity > 75 ? 'bg-gradient-to-r from-orange-500 to-red-500' :
                  severity > 45 ? 'bg-gradient-to-r from-amber-400 to-orange-500' :
                  'bg-gradient-to-r from-emerald-500 to-cyan-500'
                }`}
                style={{ width: `${Math.max(5, Math.min(100, severity))}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span className="text-emerald-400">Zone A (Good)</span>
              <span className="text-amber-400">Zone B/C (Wear)</span>
              <span className="text-red-400">Zone D (Unacceptable)</span>
            </div>
          </div>

          <div className="bg-industrial-950 border border-industrial-border/60 rounded-lg p-3 space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Predicted Condition:</span>
              <span className="font-bold text-cyan-400 font-mono">{prediction.predicted_condition}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Model Confidence:</span>
              <span className="font-bold text-white font-mono">{(prediction.confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Diagnostic Model:</span>
              <span className="text-slate-300 font-mono">{prediction.model_used}</span>
            </div>
          </div>

          <button
            onClick={() => onNavigate('maintenance')}
            className="w-full py-2.5 rounded-lg bg-industrial-800 hover:bg-industrial-700 text-slate-200 text-xs font-mono font-semibold transition border border-industrial-border flex items-center justify-center space-x-2"
          >
            <span>VIEW PRESCRIPTIVE ACTIONS</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Real-time Waveform Preview Chart */}
        <div className="lg:col-span-2 bg-industrial-900 border border-industrial-border rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-white tracking-wider font-mono">DRIVE-END ACCELEROMETER TIME SERIES</h3>
              <p className="text-xs text-slate-400">2048-Sample Continuous Window (170.7 ms duration at 12 kHz)</p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded bg-industrial-950 text-cyan-400 border border-industrial-border font-mono">
              Recording {currentStep.recording_id}
            </span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={waveform}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                <XAxis 
                  dataKey="time_ms" 
                  stroke="#64748b" 
                  fontSize={10} 
                  unit=" ms"
                  tickCount={6}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={10} 
                  unit=" g" 
                  domain={['auto', 'auto']}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }}
                  formatter={(val) => [`${Number(val).toFixed(4)} g`, 'Amplitude']}
                  labelFormatter={(lbl) => `Time: ${lbl} ms`}
                />
                <Line 
                  type="monotone" 
                  dataKey="amplitude_g" 
                  stroke="#38bdf8" 
                  strokeWidth={1.5} 
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Probabilities Mini Breakdown */}
          <div className="grid grid-cols-4 gap-2 pt-2 border-t border-industrial-border/60">
            {Object.entries(prediction.probabilities).map(([cond, prob]) => (
              <div key={cond} className="bg-industrial-950 p-2 rounded border border-industrial-border/40 text-center">
                <span className="text-[10px] text-slate-400 block truncate">{cond}</span>
                <span className="text-xs font-mono font-bold text-white">{(prob * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
