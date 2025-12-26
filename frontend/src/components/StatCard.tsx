import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatProps {
  label: string;
  value: string | number;
  unit: string;
  icon: LucideIcon;
  color: 'blue' | 'green' | 'red' | 'amber' | 'purple';
  isAlert?: boolean;
  isSafe?: boolean;
}

const StatCard: React.FC<StatProps> = ({ label, value, unit, icon: Icon, color, isAlert, isSafe }) => {
  // Dynamic border and glow for Alert / Safe State
  const borderClass = isAlert
    ? 'border-[#EF4444] border-2 animate-pulse shadow-[0_0_30px_rgba(239,68,68,0.4)]'
    : isSafe
      ? 'border-[#22C55E] border-2 animate-pulse shadow-[0_0_30px_rgba(34,197,94,0.4)]'
      : 'border-[#38BDF8]/20 border hover:border-[#38BDF8]/50 hover:shadow-[0_0_40px_rgba(56,189,248,0.2)]';

  const colorClasses = {
    blue: 'text-[#38BDF8] drop-shadow-[0_0_8px_rgba(56,189,248,0.6)]',
    green: 'text-[#22C55E] drop-shadow-[0_0_8px_rgba(34,197,94,0.6)]',
    red: 'text-[#EF4444] drop-shadow-[0_0_8px_rgba(239,68,68,0.6)]',
    amber: 'text-[#F59E0B] drop-shadow-[0_0_8px_rgba(245,158,11,0.6)]',
    purple: 'text-[#A855F7] drop-shadow-[0_0_8px_rgba(168,85,247,0.6)]'
  };

  const valueGlow = isAlert
    ? 'drop-shadow-[0_0_10px_rgba(239,68,68,0.5)]'
    : isSafe
      ? 'drop-shadow-[0_0_10px_rgba(34,197,94,0.5)]'
      : 'drop-shadow-[0_0_10px_rgba(56,189,248,0.3)]';

  return (
    <div className={`glass-card p-3 sm:p-4 md:p-5 rounded-xl ${borderClass} flex flex-col justify-between hover:shadow-2xl transition-all duration-300 relative overflow-hidden group h-full`}>
      {/* Premium gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#38BDF8]/0 to-[#38BDF8]/0 group-hover:from-[#38BDF8]/10 group-hover:to-transparent transition-all duration-500 pointer-events-none"></div>
      <div className="absolute inset-0 animate-shimmer opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[#9CA3AF] text-xs sm:text-sm md:text-base uppercase tracking-wider font-bold drop-shadow-[0_2px_4px_rgba(0,0,0,0.5)]">{label}</span>
          <Icon className={`w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 ${colorClasses[color]} transition-transform duration-300 group-hover:scale-110`} />
        </div>
        <div className="flex items-end gap-1 sm:gap-2">
          <span className={`text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black text-[#E5E7EB] ${valueGlow} transition-all duration-300`}>{value}</span>
          <span className="text-sm sm:text-base md:text-lg text-[#9CA3AF] mb-1 font-bold">{unit}</span>
        </div>
      </div>
    </div>
  );
};

export default StatCard;