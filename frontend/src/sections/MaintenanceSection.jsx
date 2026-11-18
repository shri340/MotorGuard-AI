import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  CheckCircle, 
  AlertTriangle, 
  ShieldAlert, 
  Clock, 
  Plus, 
  Check, 
  PlayCircle,
  FileText
} from 'lucide-react';
import { 
  getMaintenancePlaybook, 
  getMaintenanceRecords, 
  createMaintenanceRecord, 
  updateMaintenanceStatus 
} from '../api/client';

export default function MaintenanceSection() {
  const [playbook, setPlaybook] = useState(null);
  const [records, setRecords] = useState([]);
  const [selectedCondition, setSelectedCondition] = useState('Outer Race Fault');
  const [loading, setLoading] = useState(true);

  // New Work Order Form State
  const [showNewModal, setShowNewModal] = useState(false);
  const [formData, setFormData] = useState({
    bearing_condition: 'Outer Race Fault',
    severity_level: 'CRITICAL',
    component: 'Drive-End Bearing (SKF 6205)',
    action_required: 'Emergency Bearing Replacement',
    recommended_procedure: 'Lockout/tagout motor, decouple load, remove damaged outer ring, install new bearing with induction heater.',
    urgency: 'IMMEDIATE',
    estimated_hours: 5.0
  });

  async function loadData() {
    try {
      setLoading(true);
      const pb = await getMaintenancePlaybook();
      setPlaybook(pb.playbook || {});
      const rec = await getMaintenanceRecords();
      setRecords(rec.records || []);
    } catch (err) {
      console.error('Failed to load maintenance data:', err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const handleStatusUpdate = async (recordId, newStatus) => {
    try {
      await updateMaintenanceStatus(recordId, newStatus);
      await loadData();
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const handleCreateRecord = async (e) => {
    e.preventDefault();
    try {
      await createMaintenanceRecord(formData);
      setShowNewModal(false);
      await loadData();
    } catch (err) {
      console.error('Failed to create work order:', err);
    }
  };

  if (loading || !playbook) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
      </div>
    );
  }

  const activeGuide = playbook[selectedCondition] || playbook['Healthy'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-wide flex items-center space-x-2">
            <Wrench className="w-5 h-5 text-cyan-400" />
            <span>PRESCRIPTIVE MAINTENANCE & WORK ORDER MANAGEMENT</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Condition-based maintenance (CBM) procedures aligned with ISO 10816-3 industrial vibration standards.
          </p>
        </div>

        <button
          onClick={() => setShowNewModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-mono font-bold transition shadow-md shadow-cyan-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>CREATE WORK ORDER</span>
        </button>
      </div>

      {/* Prescriptive Engineering Playbook Cards */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-6 space-y-5">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-industrial-border/60 pb-4">
          <div>
            <h3 className="text-sm font-bold text-white tracking-wider font-mono">
              PRESCRIPTIVE ACTION PLAYBOOK
            </h3>
            <p className="text-xs text-slate-400">Select fault mode to inspect verified mechanical mitigation steps:</p>
          </div>

          <div className="flex space-x-2 overflow-x-auto no-scrollbar">
            {Object.keys(playbook).map((cond) => (
              <button
                key={cond}
                onClick={() => setSelectedCondition(cond)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition ${
                  selectedCondition === cond
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 font-bold'
                    : 'text-slate-400 hover:text-white bg-industrial-950 border border-industrial-border'
                }`}
              >
                {cond}
              </button>
            ))}
          </div>
        </div>

        {/* Selected Condition Playbook Card */}
        <div className="bg-industrial-950 border border-industrial-border rounded-xl p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-industrial-border/60 pb-3">
            <div>
              <span className="text-base font-bold text-white font-mono">{activeGuide.action}</span>
              <p className="text-xs text-slate-400 font-mono mt-0.5">Component: {activeGuide.component}</p>
            </div>
            <div className="flex items-center space-x-2 font-mono text-xs">
              <span className="px-2.5 py-1 rounded bg-industrial-900 text-slate-300 border border-industrial-border">
                Est: {activeGuide.estimated_hours} hrs
              </span>
              <span className={`px-2.5 py-1 rounded font-bold ${
                activeGuide.urgency === 'IMMEDIATE' ? 'bg-red-950 text-red-400 border border-red-800' :
                activeGuide.urgency === 'HIGH' ? 'bg-orange-950 text-orange-400 border border-orange-800' :
                activeGuide.urgency === 'MEDIUM' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                'bg-emerald-950 text-emerald-400 border border-emerald-800'
              }`}>
                {activeGuide.urgency} URGENCY
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-xs font-mono font-bold text-cyan-400">Prescriptive Analysis:</span>
            <p className="text-xs text-slate-300 leading-relaxed">
              {activeGuide.recommendation}
            </p>
          </div>

          <div className="space-y-2 pt-2 border-t border-industrial-border/60">
            <span className="text-xs font-mono font-bold text-slate-300">Standard Operating Procedure (SOP):</span>
            <div className="bg-industrial-900/80 p-3 rounded-lg border border-industrial-border font-mono text-xs text-slate-300 leading-relaxed">
              {activeGuide.procedure}
            </div>
          </div>
        </div>
      </div>

      {/* Active Work Orders Database Table */}
      <div className="bg-industrial-900 border border-industrial-border rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white tracking-wider font-mono flex items-center space-x-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>ACTIVE & PAST MAINTENANCE WORK ORDERS (SQLITE)</span>
          </h3>
          <span className="text-xs font-mono text-slate-400">{records.length} Work Orders</span>
        </div>

        {records.length === 0 ? (
          <div className="text-center py-8 text-slate-500 font-mono text-xs">
            No active maintenance records. Click "Create Work Order" to schedule maintenance.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-industrial-950 text-slate-400 border-b border-industrial-border">
                <tr>
                  <th className="p-3">Order #</th>
                  <th className="p-3">Component</th>
                  <th className="p-3">Fault Condition</th>
                  <th className="p-3">Action Required</th>
                  <th className="p-3">Urgency</th>
                  <th className="p-3">Labor</th>
                  <th className="p-3">Status</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-industrial-border/60">
                {records.map((r) => (
                  <tr key={r.id} className="hover:bg-industrial-800/40">
                    <td className="p-3 text-cyan-400 font-bold">WO-{r.id}</td>
                    <td className="p-3 text-slate-300">{r.component}</td>
                    <td className="p-3 font-semibold text-white">{r.bearing_condition}</td>
                    <td className="p-3 text-slate-300">{r.action_required}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.urgency === 'IMMEDIATE' ? 'bg-red-950 text-red-400 border border-red-800/50' :
                        r.urgency === 'HIGH' ? 'bg-orange-950 text-orange-400 border border-orange-800/50' :
                        'bg-amber-950 text-amber-400 border border-amber-800/50'
                      }`}>
                        {r.urgency}
                      </span>
                    </td>
                    <td className="p-3 text-slate-400">{r.estimated_hours} hrs</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.status === 'COMPLETED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/50' :
                        r.status === 'IN_PROGRESS' ? 'bg-cyan-950 text-cyan-400 border border-cyan-800/50' :
                        'bg-slate-800 text-slate-300'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="p-3 text-right space-x-2">
                      {r.status === 'PENDING' && (
                        <button
                          onClick={() => handleStatusUpdate(r.id, 'IN_PROGRESS')}
                          className="px-2 py-1 rounded bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-800 text-[10px] transition"
                        >
                          Start Work
                        </button>
                      )}
                      {r.status === 'IN_PROGRESS' && (
                        <button
                          onClick={() => handleStatusUpdate(r.id, 'COMPLETED')}
                          className="px-2 py-1 rounded bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800 text-[10px] transition"
                        >
                          Mark Complete
                        </button>
                      )}
                      {r.status === 'COMPLETED' && (
                        <span className="text-slate-500 text-[10px]">Archived</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal for Creating a Work Order */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-industrial-900 border border-industrial-border rounded-xl max-w-lg w-full p-6 space-y-4">
            <h3 className="text-base font-bold text-white font-mono">Create Maintenance Work Order</h3>
            <form onSubmit={handleCreateRecord} className="space-y-3 text-xs font-mono">
              <div>
                <label className="text-slate-400 block mb-1">Target Component:</label>
                <input
                  type="text"
                  value={formData.component}
                  onChange={(e) => setFormData({ ...formData, component: e.target.value })}
                  className="w-full bg-industrial-950 border border-industrial-border rounded p-2 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Bearing Condition:</label>
                  <select
                    value={formData.bearing_condition}
                    onChange={(e) => setFormData({ ...formData, bearing_condition: e.target.value })}
                    className="w-full bg-industrial-950 border border-industrial-border rounded p-2 text-white"
                  >
                    <option value="Healthy">Healthy</option>
                    <option value="Inner Race Fault">Inner Race Fault</option>
                    <option value="Ball Fault">Ball Fault</option>
                    <option value="Outer Race Fault">Outer Race Fault</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Urgency:</label>
                  <select
                    value={formData.urgency}
                    onChange={(e) => setFormData({ ...formData, urgency: e.target.value })}
                    className="w-full bg-industrial-950 border border-industrial-border rounded p-2 text-white"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="IMMEDIATE">IMMEDIATE</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Action Required:</label>
                <input
                  type="text"
                  value={formData.action_required}
                  onChange={(e) => setFormData({ ...formData, action_required: e.target.value })}
                  className="w-full bg-industrial-950 border border-industrial-border rounded p-2 text-white"
                  required
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Recommended Procedure:</label>
                <textarea
                  value={formData.recommended_procedure}
                  onChange={(e) => setFormData({ ...formData, recommended_procedure: e.target.value })}
                  rows={3}
                  className="w-full bg-industrial-950 border border-industrial-border rounded p-2 text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-3 pt-3 border-t border-industrial-border/60">
                <button
                  type="button"
                  onClick={() => setShowNewModal(false)}
                  className="px-4 py-2 rounded bg-industrial-800 hover:bg-industrial-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold"
                >
                  Save Work Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
