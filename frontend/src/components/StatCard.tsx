import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatProps {
  label: string;
  value: string | number;
  unit: string;
  icon: LucideIcon;
  color: 'blue' | 'green' | 'red' | 'amber';
  isAlert?: boolean;
}

const StatCard: React.FC<StatProps> = ({ label, value, unit, icon: Icon, color, isAlert }) => {
  // Dynamic border for Alert State
  const borderClass = isAlert 
    ? 'border-[#EF4444] border-2 animate-pulse shadow-[0_0_30px_rgba(239,68,68,0.4)]' 
    : 'border-[#38BDF8]/20 border hover:border-[#38BDF8]/40';

  const colorClasses = {
    blue: 'text-[#38BDF8]',
    green: 'text-[#22C55E]',
    red: 'text-[#EF4444]',
    amber: 'text-[#F59E0B]'
  };

  return (
    <div className={`glass-card p-6 rounded-xl ${borderClass} flex flex-col justify-between hover:shadow-2xl hover:shadow-[#38BDF8]/5 transition-all relative overflow-hidden group`}>
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#38BDF8]/0 to-[#38BDF8]/0 group-hover:from-[#38BDF8]/5 group-hover:to-transparent transition-all duration-300 pointer-events-none"></div>
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className="text-[#9CA3AF] text-base uppercase tracking-wider font-bold">{label}</span>
          <Icon className={`w-8 h-8 ${colorClasses[color]}`} />
        </div>
        <div className="flex items-end gap-2">
          <span className="text-5xl font-black text-[#E5E7EB]">{value}</span>
          <span className="text-xl text-[#9CA3AF] mb-2 font-bold">{unit}</span>
        </div>
      </div>
    </div>
  );
};

export default StatCard;