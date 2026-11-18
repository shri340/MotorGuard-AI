import React from 'react';
import { 
  Activity, 
  Gauge, 
  BarChart3, 
  TrendingUp, 
  Cpu, 
  History, 
  Wrench, 
  Info,
  Server,
  Database
} from 'lucide-react';

export const SECTIONS = [
  { id: 'dashboard', label: 'Dashboard', icon: Gauge },
  { id: 'monitoring', label: 'Motor Monitoring', icon: Activity },
  { id: 'statistics', label: 'Statistical Analysis', icon: BarChart3 },
  { id: 'distributions', label: 'Probability Distributions', icon: TrendingUp },
  { id: 'predictions', label: 'ML Predictions', icon: Cpu },
  { id: 'history', label: 'Historical Analysis', icon: History },
  { id: 'maintenance', label: 'Maintenance Recommendations', icon: Wrench },
  { id: 'about', label: 'About Project', icon: Info },
];

export default function Navbar({ activeSection, onSelectSection, activeModel, onSelectModel, backendOnline }) {
  return (
    <header className="sticky top-0 z-50 bg-industrial-900/90 backdrop-blur border-b border-industrial-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & System Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectSection('dashboard')}>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Activity className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-wider font-mono">MOTORGUARD</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">AI</span>
              </div>
              <p className="text-[10px] text-slate-400 tracking-tight">CWRU Bearing Diagnostics Engine</p>
            </div>
          </div>

          {/* Quick Model Selector & System Telemetry Status */}
          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex items-center space-x-2 bg-industrial-950 border border-industrial-border px-3 py-1.5 rounded-lg text-xs font-mono">
              <span className="text-slate-400">Model:</span>
              <button
                onClick={() => onSelectModel('rf')}
                className={`px-2 py-0.5 rounded transition ${
                  activeModel === 'rf' 
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 font-semibold' 
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Random Forest
              </button>
              <button
                onClick={() => onSelectModel('lr')}
                className={`px-2 py-0.5 rounded transition ${
                  activeModel === 'lr' 
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40 font-semibold' 
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Logistic Regr
              </button>
            </div>

            <div className="flex items-center space-x-2 bg-industrial-950 border border-industrial-border px-3 py-1.5 rounded-lg text-xs font-mono">
              <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-ping' : 'bg-red-500'}`} />
              <span className="text-slate-300">{backendOnline ? 'BACKEND ONLINE' : 'DISCONNECTED'}</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs Bar */}
        <nav className="flex space-x-1 overflow-x-auto py-2 no-scrollbar border-t border-industrial-border/50">
          {SECTIONS.map((sec) => {
            const Icon = sec.icon;
            const isActive = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => onSelectSection(sec.id)}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-industrial-800/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{sec.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
