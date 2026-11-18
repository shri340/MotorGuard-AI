import React, { useState, useEffect } from 'react';
import { 
  History, 
  Trash2, 
  Filter, 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle, 
  RefreshCw,
  Search,
  Activity
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid 
} from 'recharts';
import { getHistoryLogs, getHistoryStats, clearHistoryLogs } from '../api/client';

export default function HistorySection() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [filterCondition, setFilterCondition] = useState('');
  const [loading, setLoading] = useState(true);
  const [clearing, setClearing] = useState(false);

  async function loadData() {
    try {
      setLoading(true);
      const logRes = await getHistoryLogs(100, filterCondition || null);
      setLogs(logRes.logs || []);
      const statRes = await getHistoryStats();
      setStats(statRes);
    } catch (err) {
      console.error('Failed to load history logs:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [filterCondition]);

  const handleClear = async () => {
    if (window.confirm('Are you sure you want to clear all monitoring logs from the SQLite database?')) {
      try {
        setClearing(true);
        await clearHistoryLogs();
        await loadData();
      } catch (err) {
        console.error('Failed to clear logs:', err);
      } finally {
        setClearing(false);
      }
    }
  };

  const trendData = [...logs].reverse().map((l, i) => ({
    event: i + 1,
    rms: l.rms,
    kurtosis: l.kurtosis,
    severity: l.severity_index,
    condition: l.predicted_condition
  }));

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>HISTORICAL MONITORING TELEMETRY & EVENT LOGS</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Persisted vibration telemetry events and ML diagnostic predictions recorded in SQLite.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            className="p-2 rounded-lg bg-industrial-950 hover:bg-industrial-800 text-slate-300 border border-industrial-border transition"
            title="Refresh logs"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleClear}
            disabled={clearing || logs.length === 0}
            className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-red-950/40 hover:bg-red-900/60 text-red-400 border border-red-800/50 text-xs font-mono transition disabled:opacity-40"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>CLEAR HISTORY</span>
          </button>
        </div>
      </div>

      {/* Stats Summary Cards */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
            <span className="text-[10px] text-slate-400 font-mono block">TOTAL LOGGED EVENTS</span>
            <span className="text-2xl font-bold font-mono text-white">{stats.total_events_logged}</span>
          </div>
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
            <span className="text-[10px] text-slate-400 font-mono block">CRITICAL ALERTS</span>
            <span className="text-2xl font-bold font-mono text-red-400">{stats.critical_alerts_count}</span>
          </div>
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
            <span className="text-[10px] text-slate-400 font-mono block">AVERAGE RMS ENERGY</span>
            <span className="text-2xl font-bold font-mono text-cyan-400">{stats.average_rms.toFixed(4)} g</span>
          </div>
          <div className="bg-industrial-900 border border-industrial-border rounded-xl p-4">
            <span className="text-[10px] text-slate-400 font-mono block">AVERAGE SEVERITY INDEX</span>
            <span className="text-2xl font-bold font-mono text-amber-400">{stats.average_severity_index}</span>
          </div>
        </div>
      )}

      {/* Historical Severity & RMS Trajectory Chart */}
      {trendData.length > 0 && (
        <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-white tracking-wider font-mono">
            HISTORICAL SEVERITY & VIBRATION TRAJECTORY (CHRONOLOGICAL)
          </h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1b2333" />
                <XAxis dataKey="event" stroke="#64748b" fontSize={10} name="Event #" />
                <YAxis stroke="#64748b" fontSize={10} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#10141d', borderColor: '#222d42', fontSize: '11px' }} />
                <Area type="monotone" dataKey="severity" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} name="Severity Index (0-100)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Filter and Event Log Table */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <h3 className="text-sm font-bold text-white tracking-wider font-mono">
            PERSISTED EVENT LOG ENTRIES
          </h3>

          <div className="flex items-center space-x-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterCondition}
              onChange={(e) => setFilterCondition(e.target.value)}
              className="bg-industrial-950 border border-industrial-border rounded px-2.5 py-1 text-xs font-mono text-cyan-400"
            >
              <option value="">All Conditions</option>
              <option value="Healthy">Healthy</option>
              <option value="Inner Race Fault">Inner Race Fault</option>
              <option value="Ball Fault">Ball Fault</option>
              <option value="Outer Race Fault">Outer Race Fault</option>
            </select>
          </div>
        </div>

        {logs.length === 0 ? (
          <div className="text-center py-10 text-slate-500 font-mono text-xs">
            No events logged yet. Launch Playback in the Motor Monitoring section to stream and log events.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-industrial-950 text-slate-400 border-b border-industrial-border">
                <tr>
                  <th className="p-3">ID</th>
                  <th className="p-3">Timestamp</th>
                  <th className="p-3">Recording</th>
                  <th className="p-3">Window</th>
                  <th className="p-3">Diagnosis</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">RMS (g)</th>
                  <th className="p-3">Kurtosis</th>
                  <th className="p-3">Severity</th>
                  <th className="p-3">Model</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-industrial-border/60">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-industrial-800/40">
                    <td className="p-3 text-slate-500">#{log.id}</td>
                    <td className="p-3 text-slate-400">{log.timestamp}</td>
                    <td className="p-3 text-cyan-300 font-bold">{log.recording_id}</td>
                    <td className="p-3 text-slate-300">Win {log.window_idx + 1}</td>
                    <td className="p-3 font-semibold">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        log.predicted_condition === 'Healthy' 
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' 
                          : 'bg-red-950 text-red-300 border border-red-800/40'
                      }`}>
                        {log.predicted_condition}
                      </span>
                    </td>
                    <td className="p-3 text-slate-200">{(log.confidence * 100).toFixed(1)}%</td>
                    <td className="p-3 text-slate-200">{log.rms.toFixed(4)}</td>
                    <td className="p-3 text-slate-200">{log.kurtosis.toFixed(2)}</td>
                    <td className="p-3 font-bold text-amber-400">{log.severity_index}</td>
                    <td className="p-3 text-slate-400">{log.model_used}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
