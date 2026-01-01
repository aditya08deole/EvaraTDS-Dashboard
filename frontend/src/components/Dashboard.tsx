import { useEffect, useState } from 'react';
import { getDashboardData } from '../api';
import StatCard from './StatCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Activity, Droplets, Thermometer, Zap, AlertTriangle, RefreshCw, Sun, Moon } from 'lucide-react';
import { format } from 'date-fns';
import { useSettingsStore } from '../store/useSettingsStore';
import { useThemeStore } from '../store/useThemeStore';
import axios from 'axios';

const Dashboard = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const { settings, loadSettings } = useSettingsStore();
  const { theme, toggleTheme } = useThemeStore();

  const fetchData = async () => {
    const result = await getDashboardData();
    if (result) {
      setData(result);
      setLastUpdated(new Date());
    }
    setLoading(false);
  };

  // Check for alerts and trigger emails if needed
  const checkAlerts = async () => {
    try {
      await axios.post('/api/v1/check-alerts');
    } catch (error) {
      console.error('Alert check failed:', error);
    }
  };

  useEffect(() => {
    fetchData(); // Initial load
    loadSettings(); // Load settings initially
    checkAlerts(); // Initial alert check
    
    const dataInterval = setInterval(fetchData, 1000); // Ultra-fast 1-second data updates
    const settingsInterval = setInterval(loadSettings, 1000); // Ultra-fast 1-second settings sync
    const alertInterval = setInterval(checkAlerts, 60000); // Check alerts every 60 seconds
    
    return () => {
      clearInterval(dataInterval);
      clearInterval(settingsInterval);
      clearInterval(alertInterval);
    };
  }, [loadSettings]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse text-[#38BDF8] text-2xl sm:text-3xl font-bold mb-4">Loading Dashboard...</div>
          <div className="text-[#9CA3AF] text-sm">Connecting to ThingSpeak</div>
        </div>
      </div>
    );
  }

  const latest = data?.latest || { tds: 0, temp: 0, voltage: 0 };
  const isCritical = latest.tds > settings.tdsThreshold; // Use settings threshold
  const isSafe = latest.tds <= settings.tdsThreshold;

  // Format history for charts - Filter out invalid data (TDS <= 20 ppm)
  // This removes false readings, sensor errors, and zero values from visualization
  const chartData = data?.history
    .filter((item: any) => item.tds > 20) // Professional filtering: exclude unreliable low readings
    .slice(-40) // Limit to last 40 data points for better performance and readability
    .map((item: any) => ({
      time: format(new Date(item.created_at), 'HH:mm'),
      tds: item.tds,
      temp: item.temp,
      tdsThreshold: settings.tdsThreshold // Add threshold value to each data point
    })) || [];

  return (
    <div className={`p-3 sm:p-4 lg:p-6 w-full min-h-screen flex flex-col space-y-3 sm:space-y-4 overflow-x-hidden transition-colors duration-300 ${
      theme === 'dark' 
        ? 'bg-gradient-to-br from-[#0B0F1A]/50 via-transparent to-[#161E2E]/30' 
        : 'bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20'
    }`}>
      
      {/* Theme Toggle Button */}
      <button
        onClick={toggleTheme}
        className={`fixed top-4 right-4 z-50 p-3 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 ${
          theme === 'dark'
            ? 'bg-gradient-to-br from-purple-600 to-blue-600 text-white hover:shadow-purple-500/50'
            : 'bg-gradient-to-br from-amber-400 to-orange-500 text-white hover:shadow-amber-500/50'
        }`}
        aria-label="Toggle theme"
      >
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse" />
        ) : (
          <Moon className="w-5 h-5 sm:w-6 sm:h-6" />
        )}
      </button>
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start space-y-4 sm:space-y-0">
        <div className="flex-1">
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] bg-clip-text text-transparent mb-1 sm:mb-2 leading-tight text-center sm:text-left">EvaraTDS Dashboard</h1>
          <p className={`text-xs sm:text-sm lg:text-base font-semibold text-center sm:text-left ${theme === 'dark' ? 'text-[#E5E7EB]' : 'text-gray-700'}`}>System ID: {data?.channel_info?.name || 'ESP32-NODE-01'}</p>
        </div>
        <div className="flex flex-col sm:items-end gap-2 sm:gap-3">
          <div className="flex items-center gap-2 sm:gap-3 justify-center sm:justify-end">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-[44px] sm:h-[52px] lg:h-[64px] w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-[44px] sm:h-[52px] lg:h-[64px] w-auto object-contain" />
          </div>
          <div className="flex flex-col items-center sm:items-end gap-1">
            <div className={`flex items-center gap-1 sm:gap-2 font-medium text-xs justify-center sm:justify-end ${theme === 'dark' ? 'text-[#9CA3AF]' : 'text-gray-600'}`}>
              <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4 animate-spin-slow text-[#38BDF8]" />
              <span>Updated: {format(lastUpdated, 'HH:mm:ss')}</span>
            </div>
            <div className={`text-xs font-medium text-center sm:text-right ${theme === 'dark' ? 'text-[#6B7280]' : 'text-gray-500'}`}>
              <span>Firmware: v2.1.3 | Status: Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {isCritical ? (
        <div className={`p-3 sm:p-4 md:p-5 rounded-xl flex items-center gap-2 sm:gap-3 shadow-xl w-full md:w-4/5 lg:w-3/5 min-h-[60px] ${
          theme === 'dark' ? 'neon-alert' : 'bg-red-100 border-2 border-red-400'
        }`}>
          <AlertTriangle className="w-6 h-6 sm:w-7 sm:h-7 text-[#EF4444] flex-shrink-0" />
          <span className={`font-black text-base sm:text-lg md:text-xl leading-tight ${
            theme === 'dark' ? 'text-[#E5E7EB]' : 'text-red-900'
          }`}>CRITICAL ALERT: High TDS Detected ({latest.tds} PPM). Inspect filtration immediately.</span>
        </div>
      ) : isSafe ? (
        <div className={`p-3 sm:p-4 md:p-5 rounded-xl flex items-center gap-2 sm:gap-3 shadow-lg border-2 border-[#22C55E] w-full md:w-4/5 lg:w-3/5 min-h-[60px] ${
          theme === 'dark' ? 'glass-card bg-gradient-to-r from-[#22C55E]/10 to-[#22C55E]/5 neon-glow-green' : 'bg-green-100'
        }`}>
          <Droplets className="w-6 h-6 sm:w-7 sm:h-7 text-[#22C55E] flex-shrink-0" />
          <span className={`font-black text-base sm:text-lg md:text-xl leading-tight ${
            theme === 'dark' ? 'text-[#E5E7EB]' : 'text-green-900'
          }`}>SAFE: TDS within acceptable range ({latest.tds} PPM).</span>
        </div>
      ) : null}

      {/* Stat Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 relative items-stretch">
        <div className="absolute inset-0 bg-gradient-to-r from-[#38BDF8]/5 via-transparent to-[#0EA5E9]/5 rounded-2xl blur-xl -z-10"></div>
        <div className="h-28 sm:h-32 lg:h-36 sm:col-span-2 lg:col-span-1"><StatCard 
          label="TDS" 
          value={latest.tds.toFixed(0)} 
          unit="PPM" 
          icon={Droplets} 
          color={isCritical ? "red" : isSafe ? "green" : "blue"}
          isAlert={isCritical}
          isSafe={isSafe}
        /></div>
        <div className="h-28 sm:h-32 lg:h-36"><StatCard 
          label="Temperature" 
          value={latest.temp.toFixed(1)} 
          unit="°C" 
          icon={Thermometer} 
          color="purple" 
        /></div>
        <div className="h-28 sm:h-32 lg:h-36"><StatCard 
          label="Sensor Signal" 
          value={latest.voltage.toFixed(3)} 
          unit="V" 
          icon={Zap} 
          color="green" 
        /></div>
      </div>

      {/* Charts Area - Responsive with better mobile sizing */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-4 overflow-visible relative">
        <div className="absolute -top-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#38BDF8]/30 to-transparent"></div>

        {/* Left: TDS Chart */}
        <div className={`p-3 sm:p-4 lg:p-5 rounded-xl flex flex-col relative overflow-hidden min-h-[380px] sm:min-h-[420px] transition-colors duration-300 ${
          theme === 'dark' ? 'glass-card' : 'bg-white shadow-lg border border-gray-200'
        }`}>
          <div className={`absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl ${theme === 'dark' ? 'bg-[#38BDF8]/5' : 'bg-blue-200/30'}`}></div>
          <h3 className={`font-black text-lg sm:text-xl lg:text-2xl mb-2 sm:mb-3 flex items-center gap-2 sm:gap-3 relative z-10 ${
            theme === 'dark' ? 'text-[#E5E7EB]' : 'text-gray-800'
          }`}>
            <Activity className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-[#38BDF8]"/> 
            <span className="hidden sm:inline">TDS Trends (Last Hour)</span>
            <span className="sm:hidden">TDS Trends</span>
            <span className={`ml-auto text-sm font-bold text-[#38BDF8] px-3 py-1 rounded-lg border border-[#38BDF8]/30 ${
              theme === 'dark' ? 'bg-[#38BDF8]/10' : 'bg-blue-100'
            }`}>
              {latest.tds.toFixed(0)} PPM
            </span>
          </h3>
          <div className="w-full flex-1 relative z-10" style={{ minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <defs>
                    {/* Neon glow gradient for TDS line */}
                    <linearGradient id="colorTdsStroke" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#38BDF8"/>
                      <stop offset="50%" stopColor="#0EA5E9"/>
                      <stop offset="100%" stopColor="#06B6D4"/>
                    </linearGradient>
                    {/* Glow filter for 3D neon effect */}
                    <filter id="glowTds" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={theme === 'dark' ? '#1F2937' : '#E5E7EB'} vertical={false} opacity={0.3} />
                  <XAxis 
                    dataKey="time" 
                    stroke={theme === 'dark' ? '#9CA3AF' : '#6B7280'} 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={{ stroke: theme === 'dark' ? '#1F2937' : '#D1D5DB', strokeWidth: 2 }} 
                    fontWeight={600}
                    dy={5}
                  />
                  <YAxis 
                    stroke={theme === 'dark' ? '#9CA3AF' : '#6B7280'} 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={{ stroke: theme === 'dark' ? '#1F2937' : '#D1D5DB', strokeWidth: 2 }} 
                    fontWeight={600}
                    dx={-5}
                    label={{ value: 'PPM', angle: -90, position: 'insideLeft', style: { fill: theme === 'dark' ? '#9CA3AF' : '#6B7280', fontWeight: 700 } }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: theme === 'dark' ? 'rgba(11, 15, 26, 0.98)' : 'rgba(255, 255, 255, 0.98)', 
                      border: `2px solid #38BDF8`, 
                      borderRadius: '16px', 
                      color: theme === 'dark' ? '#E5E7EB' : '#1F2937', 
                      boxShadow: theme === 'dark' ? '0 20px 60px rgba(56, 189, 248, 0.5), 0 0 0 1px rgba(56, 189, 248, 0.3) inset' : '0 10px 30px rgba(0, 0, 0, 0.15)', 
                      fontSize: '14px', 
                      fontWeight: 700, 
                      padding: '16px 20px',
                      backdropFilter: 'blur(24px)'
                    }}
                    labelStyle={{ color: '#38BDF8', fontSize: '13px', marginBottom: '8px', fontWeight: 800 }}
                    formatter={(value: any, name: any) => [
                      <span style={{ color: '#E5E7EB', fontSize: '18px', fontWeight: 900 }}>
                        {Number(value).toFixed(1)} PPM
                      </span>, 
                      <span style={{ color: '#9CA3AF' }}>TDS Level</span>
                    ]}
                    cursor={{ stroke: '#38BDF8', strokeWidth: 2, strokeDasharray: '5 5' }}
                  />
                  {/* Neon TDS Line with glow effect */}
                  <Line 
                    type="monotone" 
                    dataKey="tds" 
                    stroke="#38BDF8" 
                    strokeWidth={3} 
                    dot={{ r: 2.5, fill: '#0EA5E9', stroke: '#06B6D4', strokeWidth: 1.5 }} 
                    activeDot={{ 
                      r: 6, 
                      fill: '#38BDF8', 
                      stroke: '#fff', 
                      strokeWidth: 2,
                      filter: 'drop-shadow(0 0 6px #38BDF8)'
                    }}
                    animationDuration={300}
                    animationEasing="ease-out"
                    isAnimationActive={true}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeOpacity={0.9}
                  />
                  {/* Threshold Limit Line - Highly Visible */}
                  <Line 
                    type="monotone" 
                    dataKey="tdsThreshold"
                    stroke="#FF0000" 
                    strokeDasharray="10 5" 
                    strokeWidth={3} 
                    dot={false} 
                    isAnimationActive={false}
                    strokeOpacity={0.85}
                    name={`Limit: ${settings.tdsThreshold} PPM`}
                    filter="drop-shadow(0 0 6px #FF0000)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

        {/* Right: Temperature Chart */}
        <div className={`p-3 sm:p-4 lg:p-5 rounded-xl flex flex-col relative overflow-hidden min-h-[350px] sm:min-h-[400px] transition-colors duration-300 ${
          theme === 'dark' ? 'glass-card' : 'bg-white shadow-lg border border-gray-200'
        }`}>
          <div className={`absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl ${theme === 'dark' ? 'bg-[#A855F7]/5' : 'bg-purple-200/30'}`}></div>
          <h3 className={`font-black text-lg sm:text-xl lg:text-2xl mb-2 sm:mb-3 flex items-center gap-2 sm:gap-3 relative z-10 ${
            theme === 'dark' ? 'text-[#E5E7EB]' : 'text-gray-800'
          }`}>
            <Thermometer className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-[#A855F7]"/> 
            <span className="hidden sm:inline">Temperature Trends (Last Hour)</span>
            <span className="sm:hidden">Temperature</span>
            <span className={`ml-auto text-sm font-bold text-[#A855F7] px-3 py-1 rounded-lg border border-[#A855F7]/30 ${
              theme === 'dark' ? 'bg-[#A855F7]/10' : 'bg-purple-100'
            }`}>
              {latest.temp.toFixed(1)} °C
            </span>
          </h3>
          <div className="w-full flex-1 relative z-10" style={{ minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <defs>
                    {/* Neon glow gradient for Temperature line */}
                    <linearGradient id="colorTempStroke" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#A855F7"/>
                      <stop offset="50%" stopColor="#9333EA"/>
                      <stop offset="100%" stopColor="#7C3AED"/>
                    </linearGradient>
                    {/* Glow filter for 3D neon effect */}
                    <filter id="glowTemp" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                      </feMerge>
                    </filter>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} opacity={0.3} />
                  <XAxis 
                    dataKey="time" 
                    stroke="#9CA3AF" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={{ stroke: '#1F2937', strokeWidth: 2 }} 
                    fontWeight={600}
                    dy={5}
                  />
                  <YAxis 
                    stroke="#9CA3AF" 
                    fontSize={10} 
                    tickLine={false} 
                    axisLine={{ stroke: '#1F2937', strokeWidth: 2 }} 
                    fontWeight={600}
                    dx={-5}
                    label={{ value: '°C', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF', fontWeight: 700 } }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(11, 15, 26, 0.98)', 
                      border: '2px solid #A855F7', 
                      borderRadius: '16px', 
                      color: '#E5E7EB', 
                      boxShadow: '0 20px 60px rgba(168, 85, 247, 0.5), 0 0 0 1px rgba(168, 85, 247, 0.3) inset', 
                      fontSize: '14px', 
                      fontWeight: 700, 
                      padding: '16px 20px',
                      backdropFilter: 'blur(24px)'
                    }}
                    labelStyle={{ color: '#A855F7', fontSize: '13px', marginBottom: '8px', fontWeight: 800 }}
                    formatter={(value: any, name: any) => [
                      <span style={{ color: '#E5E7EB', fontSize: '18px', fontWeight: 900 }}>
                        {Number(value).toFixed(2)} °C
                      </span>, 
                      <span style={{ color: '#9CA3AF' }}>Temperature</span>
                    ]}
                    cursor={{ stroke: '#A855F7', strokeWidth: 2, strokeDasharray: '5 5' }}
                  />
                  {/* Neon Temperature Line with glow effect */}
                  <Line 
                    type="monotone" 
                    dataKey="temp" 
                    stroke="#A855F7" 
                    strokeWidth={3} 
                    dot={{ r: 2.5, fill: '#9333EA', stroke: '#7C3AED', strokeWidth: 1.5 }} 
                    activeDot={{ 
                      r: 6, 
                      fill: '#A855F7', 
                      stroke: '#fff', 
                      strokeWidth: 2,
                      filter: 'drop-shadow(0 0 6px #A855F7)'
                    }}
                    animationDuration={300}
                    animationEasing="ease-out"
                    isAnimationActive={true}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeOpacity={0.9}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

      </div>
    </div>
  );
};

export default Dashboard;