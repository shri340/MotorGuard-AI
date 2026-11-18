import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DashboardSection from './sections/DashboardSection';
import MonitoringSection from './sections/MonitoringSection';
import StatisticsSection from './sections/StatisticsSection';
import DistributionsSection from './sections/DistributionsSection';
import PredictionsSection from './sections/PredictionsSection';
import HistorySection from './sections/HistorySection';
import MaintenanceSection from './sections/MaintenanceSection';
import AboutSection from './sections/AboutSection';
import { getHealth } from './api/client';

export default function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [activeModel, setActiveModel] = useState('rf'); // 'rf' or 'lr'
  const [backendOnline, setBackendOnline] = useState(true);

  // Periodic health check
  useEffect(() => {
    async function checkBackend() {
      try {
        await getHealth();
        setBackendOnline(true);
      } catch (err) {
        setBackendOnline(false);
      }
    }
    checkBackend();
    const interval = setInterval(checkBackend, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-industrial-950 text-slate-100 flex flex-col font-sans">
      {/* Top Industrial Navbar */}
      <Navbar
        activeSection={activeSection}
        onSelectSection={setActiveSection}
        activeModel={activeModel}
        onSelectModel={setActiveModel}
        backendOnline={backendOnline}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeSection === 'dashboard' && (
          <DashboardSection onNavigate={setActiveSection} activeModel={activeModel} />
        )}
        {activeSection === 'monitoring' && (
          <MonitoringSection activeModel={activeModel} />
        )}
        {activeSection === 'statistics' && (
          <StatisticsSection />
        )}
        {activeSection === 'distributions' && (
          <DistributionsSection />
        )}
        {activeSection === 'predictions' && (
          <PredictionsSection activeModel={activeModel} onSelectModel={setActiveModel} />
        )}
        {activeSection === 'history' && (
          <HistorySection />
        )}
        {activeSection === 'maintenance' && (
          <MaintenanceSection />
        )}
        {activeSection === 'about' && (
          <AboutSection />
        )}
      </main>

      {/* Industrial Footer */}
      <footer className="border-t border-industrial-border bg-industrial-900/60 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 font-mono gap-2">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span>MotorGuard AI &bull; Intelligent Motor Condition Monitoring & Predictive Maintenance</span>
          </div>
          <div>
            Case Western Reserve University (CWRU) 12 kHz Bearing Dataset
          </div>
        </div>
      </footer>
    </div>
  );
}
