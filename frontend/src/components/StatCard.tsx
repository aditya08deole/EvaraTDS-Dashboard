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
  // Dynamic border for Alert / Safe State
  const borderClass = isAlert
    ? 'border-[#EF4444] border-2 animate-pulse shadow-md subtle-glow-red'
    : isSafe
      ? 'border-[#22C55E] border-2 animate-pulse shadow-md subtle-glow-green'
      : 'border-[#38BDF8]/20 border hover:border-[#38BDF8]/40';

  const colorClasses = {
    blue: 'text-[#38BDF8]',
    green: 'text-[#22C55E]',
    red: 'text-[#EF4444]',
    amber: 'text-[#F59E0B]',
    purple: 'text-[#A855F7]'
  };

  return (
    <div className={`glass-card p-3 sm:p-4 md:p-5 rounded-xl ${borderClass} flex flex-col justify-between hover:shadow-2xl hover:shadow-[#38BDF8]/5 transition-all relative overflow-hidden group h-full`}>
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#38BDF8]/0 to-[#38BDF8]/0 group-hover:from-[#38BDF8]/5 group-hover:to-transparent transition-all duration-300 pointer-events-none"></div>
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[#9CA3AF] text-xs sm:text-sm md:text-base uppercase tracking-wider font-bold">{label}</span>
          <Icon className={`w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 ${colorClasses[color]}`} />
        </div>
        <div className="flex items-end gap-1 sm:gap-2">
          <span className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black text-[#E5E7EB]">{value}</span>
          <span className="text-sm sm:text-base md:text-lg text-[#9CA3AF] mb-1 font-bold">{unit}</span>
        </div>
      </div>
    </div>
  );
};

export default StatCard;