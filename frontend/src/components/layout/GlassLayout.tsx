import React, { ReactNode } from 'react';
import { Activity, Settings as SettingsIcon, Database } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

const GlassLayout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0B0F1A] via-[#0E1627] to-[#111827] text-[#E5E7EB] font-sans selection:bg-[#38BDF8] selection:text-[#0B0F1A] relative z-10">
      {/* Ambient light effects for depth */}
      <div className="fixed top-0 left-0 w-[600px] h-[600px] bg-gradient-radial from-[#38BDF8]/8 to-transparent rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2 pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-[600px] h-[600px] bg-gradient-radial from-[#0EA5E9]/6 to-transparent rounded-full blur-[120px] translate-x-1/2 translate-y-1/2 pointer-events-none" />
      <div className="fixed top-1/2 right-1/4 w-[400px] h-[400px] bg-gradient-radial from-[#38BDF8]/4 to-transparent rounded-full blur-[100px] pointer-events-none" />

      <div className="relative flex min-h-screen">
        <aside className="w-72 border-r border-[#1F2937] bg-gradient-to-b from-[#0F172A]/90 via-[#0F172A]/80 to-[#0B0F1A]/70 backdrop-blur-xl hidden lg:flex flex-col p-6 z-10 shadow-2xl">
          <div className="flex items-center gap-4 mb-12">
            <div className="w-14 h-14 bg-gradient-to-br from-[#38BDF8] to-[#0EA5E9] rounded-xl flex items-center justify-center shadow-lg shadow-[#38BDF8]/30">
              <Activity className="text-white w-8 h-8" />
            </div>
            <div>
              <div className="font-extrabold text-3xl tracking-tight text-[#E5E7EB] leading-tight">EvaraTDS</div>
              <div className="text-sm text-[#9CA3AF]">TDS Monitoring</div>
            </div>
          </div>

          <nav className="space-y-2 flex-1">
            <NavItem to="/dashboard" icon={Activity} label="Live Monitor" />
            <NavItem to="/history" icon={Database} label="Data Logs" />
            <NavItem to="/settings" icon={SettingsIcon} label="Calibration" />
          </nav>

          <div className="text-xs text-[#6B7280] mt-auto pt-6 border-t border-[#1F2937]">
            <div>Firmware: v1.2.4</div>
            <div>Status: <span className="text-[#22C55E] font-semibold">Online</span></div>
          </div>
        </aside>

        <main className="flex-1 p-4 lg:p-8 overflow-y-auto z-10">
          {children}
        </main>
      </div>
    </div>
  );
};

const NavItem = ({ icon: Icon, label, to }: any) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} className={`w-full flex items-center gap-4 px-5 py-4 rounded-xl transition-all ${
      isActive
        ? 'bg-[#38BDF8]/15 text-[#38BDF8] border border-[#38BDF8]/40 shadow-lg shadow-[#38BDF8]/10 font-black'
        : 'hover:bg-[#161E2E] text-[#9CA3AF] hover:text-[#E5E7EB] font-bold'
    }`}>
      <Icon className="w-6 h-6" />
      <span className="text-base">{label}</span>
    </Link>
  );
};

export default GlassLayout;
