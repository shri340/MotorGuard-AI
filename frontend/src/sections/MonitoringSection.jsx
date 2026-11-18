import React, { useState, useEffect, useRef } from 'react';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  ChevronRight, 
  ChevronLeft, 
  Radio, 
  Activity, 
  Cpu, 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle,
  Zap,
  BarChart2,
  Clock,
  Layers
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  AreaChart, 
  Area 
} from 'recharts';
import { getPlaybackOptions, getPlaybackWindow } from '../api/client';

export default function MonitoringSection({ activeModel }) {
  const [options, setOptions] = useState([]);
  const [selectedFileId, setSelectedFileId] = useState(97); // Default: Healthy 0 HP
  const [windowIdx, setWindowIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeedMs, setPlaybackSpeedMs] = useState(300);
  const [currentStep, setCurrentStep] = useState(null);
  const [loading, setLoading] = useState(true);
  const [featureHistory, setFeatureHistory] = useState([]);

  const timerRef = useRef(null);

  // Load available recordings catalog
  useEffect(() => {
    async function loadOptions() {
      try {
        const res = await getPlaybackOptions();
        setOptions(res.available_recordings || []);
      } catch (err) {
        console.error('Failed to load playback options:', err);
      }
    }
    loadOptions();
  }, []);

  // Fetch window data whenever file or window index changes
  useEffect(() => {
    let isCancelled = false;
    async function fetchWindow() {
      try {
        const data = await getPlaybackWindow(selectedFileId, windowIdx, activeModel, true, 256);
        if (!isCancelled) {
          setCurrentStep(data);
          setLoading(false);
          // Keep a short rolling history of features for sparkline trend (last 20 windows)
          setFeatureHistory(prev => {
            const next = [...prev, { idx: windowIdx, rms: data.features.rms, kurtosis: data.features.kurtosis }];
            return next.slice(-25);
          });
        }
      } catch (err) {
        console.error('Playback step error:', err);
      }
    }
    fetchWindow();
    return () => { isCancelled = true; };
  }, [selectedFileId, windowIdx, activeModel]);

  // Handle Playback Interval Timer
  useEffect(() => {
    if (isPlaying && currentStep) {
      timerRef.current = setInterval(() => {
        setWindowIdx(prev => {
          if (prev + 1 < currentStep.total_windows) {
            return prev + 1;
          } else {
            setIsPlaying(false);
            return prev;
          }
        });
      }, playbackSpeedMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, playbackSpeedMs, currentStep]);

  const handleStart = () => setIsPlaying(true);
  const handlePause = () => setIsPlaying(false);
  const handleReset = () => {
    setIsPlaying(false);
    setWindowIdx(0);
    setFeatureHistory([]);
  };
  const handleStepForward = () => {
    if (currentStep && windowIdx + 1 < currentStep.total_windows) {
      setWindowIdx(windowIdx + 1);
    }
  };
  const handleStepBackward = () => {
    if (windowIdx > 0) {
      setWindowIdx(windowIdx - 1);
    }
  };

  if (loading && !currentStep) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin mx-auto" />
          <p className="text-xs font-mono text-slate-400">Loading vibration recording...</p>
        </div>
      </div>
    );
  }

  const { features, prediction, ground_truth_condition, motor_rpm, ground_truth_load_hp, waveform, total_windows, progress_percent } = currentStep;

  return (
    <div className="space-y-6">
      {/* Explicit Disclaimer Notice Required by Quality Specifications */}
      <div className="bg-amber-950/30 border border-amber-500/40 rounded-xl p-4 flex items-center justify-between text-amber-200 text-xs font-mono">
        <div className="flex items-center space-x-3">
          <Radio className="w-5 h-5 text-amber-400 animate-pulse shrink-0" />
          <div>
            <span className="font-bold text-amber-300">RECORDED SIGNAL PLAYBACK SYSTEM</span>
            <p className="text-[11px] text-amber-200/80">
              Streaming original experimental CWRU 12 kHz accelerometer recordings. This is historical experimental data playback, NOT live hardware instrumentation.
            </p>
          </div>
        </div>
        <span className="hidden md:inline-block px-2.5 py-1 rounded bg-amber-900/50 border border-amber-700/60 text-[10px]">
          50% Window Overlap (Step 1024)
        </span>
      </div>

      {/* Control Console Bar */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4 shadow-lg">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
          {/* Recording Selector */}
          <div className="flex-1 flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
            <label className="text-xs font-mono text-slate-400 whitespace-nowrap">Target Recording:</label>
            <select
              value={selectedFileId}
              onChange={(e) => {
                setSelectedFileId(Number(e.target.value));
                setWindowIdx(0);
                setIsPlaying(false);
              }}
              className="w-full sm:w-auto bg-industrial-950 border border-industrial-border rounded-lg px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
            >
              {options.map((opt) => (
                <option key={opt.file_id} value={opt.file_id}>
                  {opt.recording_id} — {opt.condition} (Load: {opt.load_hp} HP, ~{opt.approx_rpm} RPM)
                </option>
              ))}
            </select>
          </div>

          {/* Playback Transport Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleStepBackward}
              disabled={windowIdx === 0}
              className="p-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 disabled:opacity-30 disabled:cursor-not-allowed border border-industrial-border text-slate-300 transition"
              title="Step Backward (Previous Window)"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            {isPlaying ? (
              <button
                onClick={handlePause}
                className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-mono text-xs font-bold transition shadow-md shadow-amber-600/20"
              >
                <Pause className="w-4 h-4" />
                <span>PAUSE</span>
              </button>
            ) : (
              <button
                onClick={handleStart}
                className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition shadow-md shadow-cyan-600/20"
              >
                <Play className="w-4 h-4" />
                <span>START</span>
              </button>
            )}

            <button
              onClick={handleStepForward}
              disabled={windowIdx + 1 >= total_windows}
              className="p-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 disabled:opacity-30 disabled:cursor-not-allowed border border-industrial-border text-slate-300 transition"
              title="Step Forward (Next Window)"
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            <button
              onClick={handleReset}
              className="p-2 rounded-lg bg-industrial-800 hover:bg-industrial-700 border border-industrial-border text-slate-300 transition"
              title="Reset to Window 0"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Speed Selector */}
          <div className="flex items-center space-x-2">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs font-mono text-slate-400">Rate:</span>
            <select
              value={playbackSpeedMs}
              onChange={(e) => setPlaybackSpeedMs(Number(e.target.value))}
              className="bg-industrial-950 border border-industrial-border rounded px-2 py-1 text-xs font-mono text-slate-200"
            >
              <option value={100}>10x (100 ms)</option>
              <option value={250}>4x (250 ms)</option>
              <option value={500}>2x (500 ms)</option>
              <option value={1000}>1x (1000 ms)</option>
            </select>
          </div>
        </div>

        {/* Timeline Scrubbing Slider */}
        <div className="space-y-2 pt-2 border-t border-industrial-border/60">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">
              Window <span className="text-cyan-400 font-bold">{windowIdx + 1}</span> of {total_windows}
            </span>
            <span className="text-slate-400">
              Sample Range: [{currentStep.sample_range.start.toLocaleString()} : {currentStep.sample_range.end.toLocaleString()}] ({progress_percent}%)
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={total_windows - 1}
            value={windowIdx}
            onChange={(e) => {
              setIsPlaying(false);
              setWindowIdx(Number(e.target.value));
            }}
            className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-industrial-950 rounded-lg appearance-none"
          />
        </div>
      </div>

      {/* Main Signal Waveform & Diagnostics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Waveform & Rolling History */}
        <div className="lg:col-span-2 space-y-6">
          {/* Main 2048-Sample Waveform */}
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white tracking-wider font-mono">INSTANTANEOUS VIBRATION TIME-SERIES</h3>
                <p className="text-xs text-slate-400">12 kHz Drive-End Accelerometer (Window #{windowIdx + 1})</p>
              </div>
              <span className="text-xs font-mono px-2 py-1 rounded bg-industrial-950 text-slate-300 border border-industrial-border">
                {currentStep.window_duration_ms} ms span
              </span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={waveform}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                  <XAxis 
                    dataKey="time_ms" 
                    stroke="#64748b" 
                    fontSize={10} 
                    unit=" ms"
                    tickCount={7}
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
          </div>

          {/* Rolling RMS & Kurtosis Trend Chart */}
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-white tracking-wider font-mono">FEATURE DYNAMICS ACROSS PLAYBACK WINDOWS</h3>
                <p className="text-[11px] text-slate-400">Trailing Window Trajectory (Energy vs Impulse Spikes)</p>
              </div>
              <span className="text-[10px] font-mono text-cyan-400">Rolling 25 Windows</span>
            </div>

            <div className="h-36 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={featureHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                  <XAxis dataKey="idx" stroke="#64748b" fontSize={9} />
                  <YAxis stroke="#64748b" fontSize={9} />
                  <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                  <Area type="monotone" dataKey="rms" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.2} name="RMS (g)" />
                  <Area type="monotone" dataKey="kurtosis" stroke="#a855f7" fill="#a855f7" fillOpacity={0.1} name="Kurtosis" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right Col: Live Updating ML Predictions & Feature Vector */}
        <div className="space-y-6">
          {/* Real-time ML Prediction Card */}
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white tracking-wider font-mono flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>INFERENCE DIAGNOSIS</span>
              </h3>
              <span className="text-[10px] font-mono text-slate-400">{prediction.model_used}</span>
            </div>

            <div className="bg-industrial-950 border border-industrial-border rounded-lg p-4 space-y-3">
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-slate-400">State:</span>
                <span className="text-base font-bold text-cyan-300 font-mono">{prediction.predicted_condition}</span>
              </div>
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-slate-400">Ground Truth:</span>
                <span className="text-xs font-mono text-slate-300">{ground_truth_condition}</span>
              </div>
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-slate-400">Confidence:</span>
                <span className="text-xs font-mono font-bold text-emerald-400">{(prediction.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-baseline">
                <span className="text-xs text-slate-400">Severity Index:</span>
                <span className="text-xs font-mono font-bold text-amber-400">{prediction.severity_index} / 100</span>
              </div>
            </div>

            {/* Probability Bars */}
            <div className="space-y-2.5">
              <span className="text-[11px] font-mono text-slate-400 block">Class Probabilities:</span>
              {Object.entries(prediction.probabilities).map(([cond, prob]) => {
                const isWinner = cond === prediction.predicted_condition;
                return (
                  <div key={cond} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className={isWinner ? 'text-white font-bold' : 'text-slate-400'}>{cond}</span>
                      <span className={isWinner ? 'text-cyan-400 font-bold' : 'text-slate-400'}>{(prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-industrial-950 h-2 rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-300 ${
                          isWinner ? (cond === 'Healthy' ? 'bg-emerald-400' : 'bg-cyan-400') : 'bg-slate-700'
                        }`}
                        style={{ width: `${Math.max(2, prob * 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Real-time 8 Statistical Features Grid */}
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-white tracking-wider font-mono flex items-center space-x-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <span>LIVE EXTRACTED FEATURES</span>
            </h3>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Mean (DC):</span>
                <span className="font-bold text-white">{features.mean.toFixed(5)}</span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Variance (Power):</span>
                <span className="font-bold text-white">{features.variance.toFixed(5)}</span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Std Dev:</span>
                <span className="font-bold text-cyan-400">{features.std.toFixed(4)}</span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">RMS:</span>
                <span className="font-bold text-cyan-400">{features.rms.toFixed(4)}</span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Skewness:</span>
                <span className="font-bold text-white">{features.skewness.toFixed(3)}</span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Kurtosis (P):</span>
                <span className={`font-bold ${features.kurtosis > 4.5 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {features.kurtosis.toFixed(2)}
                </span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Peak-to-Peak:</span>
                <span className="font-bold text-white">{features.peak_to_peak.toFixed(3)}</span>
              </div>
              <div className="bg-industrial-950 p-2.5 rounded border border-industrial-border/60">
                <span className="text-[10px] text-slate-400 block">Crest Factor:</span>
                <span className="font-bold text-amber-400">{features.crest_factor.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
