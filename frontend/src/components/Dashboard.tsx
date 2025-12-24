import { useEffect, useState } from 'react';
import { getDashboardData } from '../api';
import StatCard from './StatCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Activity, Droplets, Thermometer, Zap, AlertTriangle, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';
import { useSettingsStore } from '../store/useSettingsStore';

const Dashboard = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const { settings } = useSettingsStore();

  const fetchData = async () => {
    const result = await getDashboardData();
    if (result) {
      setData(result);
      setLastUpdated(new Date());
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData(); // Initial load
    const interval = setInterval(fetchData, settings.refreshInterval); // Use settings refresh interval
    return () => clearInterval(interval);
  }, [settings.refreshInterval]);

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

  // Format history for charts
  const chartData = data?.history.map((item: any) => ({
    time: format(new Date(item.created_at), 'HH:mm'),
    tds: item.tds,
    temp: item.temp
  })) || [];

  return (
    <div className="p-2 sm:p-4 lg:p-6 w-full min-h-screen flex flex-col space-y-2 sm:space-y-4 overflow-hidden bg-gradient-to-br from-[#0B0F1A]/50 via-transparent to-[#161E2E]/30">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start space-y-4 sm:space-y-0">
        <div className="flex-1">
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] bg-clip-text text-transparent mb-1 sm:mb-2 leading-tight text-center sm:text-left">EvaraTDS Dashboard</h1>
          <p className="text-[#E5E7EB] text-xs sm:text-sm lg:text-base font-semibold text-center sm:text-left">System ID: {data?.channel_info?.name || 'ESP32-NODE-01'}</p>
        </div>
        <div className="flex flex-col sm:items-end gap-2 sm:gap-3">
          <div className="flex items-center gap-2 sm:gap-3 justify-center sm:justify-end">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-[44px] sm:h-[52px] lg:h-[64px] w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-[44px] sm:h-[52px] lg:h-[64px] w-auto object-contain" />
          </div>
          <div className="flex flex-col items-center sm:items-end gap-1">
            <div className="flex items-center gap-1 sm:gap-2 text-[#9CA3AF] font-medium text-xs justify-center sm:justify-end">
              <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4 animate-spin-slow text-[#38BDF8]" />
              <span>Updated: {format(lastUpdated, 'HH:mm:ss')}</span>
            </div>
            <div className="text-[#6B7280] text-xs font-medium text-center sm:text-right">
              <span>Firmware: v2.1.3 | Status: Online</span>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {isCritical ? (
        <div className="neon-alert p-3 sm:p-4 md:p-5 rounded-xl flex items-center gap-2 sm:gap-3 shadow-xl w-full md:w-4/5 lg:w-3/5 min-h-[60px]">
          <AlertTriangle className="w-6 h-6 sm:w-7 sm:h-7 text-[#EF4444] flex-shrink-0" />
          <span className="font-black text-base sm:text-lg md:text-xl text-[#E5E7EB] leading-tight">CRITICAL ALERT: High TDS Detected ({latest.tds} PPM). Inspect filtration immediately.</span>
        </div>
      ) : isSafe ? (
        <div className="glass-card p-3 sm:p-4 md:p-5 rounded-xl flex items-center gap-2 sm:gap-3 shadow-lg border-2 border-[#22C55E] bg-gradient-to-r from-[#22C55E]/10 to-[#22C55E]/5 neon-glow-green w-full md:w-4/5 lg:w-3/5 min-h-[60px]">
          <Droplets className="w-6 h-6 sm:w-7 sm:h-7 text-[#22C55E] flex-shrink-0" />
          <span className="font-black text-base sm:text-lg md:text-xl text-[#E5E7EB] leading-tight">SAFE: TDS within acceptable range ({latest.tds} PPM).</span>
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

      {/* Charts Area - Responsive */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 h-56 sm:h-64 md:h-72 lg:h-80 xl:h-[340px] overflow-hidden relative">
        <div className="absolute -top-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#38BDF8]/30 to-transparent"></div>

        {/* Left: TDS Chart */}
        <div className="glass-card p-2 sm:p-3 lg:p-4 rounded-xl flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#38BDF8]/5 rounded-full blur-3xl"></div>
          <h3 className="text-[#E5E7EB] font-black text-base sm:text-lg lg:text-xl mb-2 flex items-center gap-2 relative z-10">
            <Activity className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-[#38BDF8]"/> 
            <span className="hidden sm:inline">TDS Trends (Last Hour)</span>
            <span className="sm:hidden">TDS Trends</span>
            <span className="ml-auto text-xs font-bold text-[#38BDF8] bg-[#38BDF8]/10 px-2 py-1 rounded-lg border border-[#38BDF8]/30">
              {latest.tds.toFixed(0)} PPM
            </span>
          </h3>
          <div className="w-full flex-1 relative z-10" style={{ minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorTds" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.8}/>
                      <stop offset="50%" stopColor="#0EA5E9" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0.1}/>
                    </linearGradient>
                    <linearGradient id="colorTdsStroke" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#38BDF8"/>
                      <stop offset="100%" stopColor="#0EA5E9"/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} opacity={0.5} />
                  <XAxis 
                    dataKey="time" 
                    stroke="#9CA3AF" 
                    fontSize={9} 
                    tickLine={false} 
                    axisLine={{ stroke: '#1F2937', strokeWidth: 2 }} 
                    fontWeight={600}
                    dy={5}
                  />
                  <YAxis 
                    stroke="#9CA3AF" 
                    fontSize={9} 
                    tickLine={false} 
                    axisLine={{ stroke: '#1F2937', strokeWidth: 2 }} 
                    fontWeight={600}
                    dx={-5}
                    label={{ value: 'PPM', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF', fontWeight: 600, fontSize: 10 } }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(11, 15, 26, 0.98)', 
                      border: '2px solid #38BDF8', 
                      borderRadius: '12px', 
                      color: '#E5E7EB', 
                      boxShadow: '0 20px 60px rgba(56, 189, 248, 0.3), 0 0 0 1px rgba(56, 189, 248, 0.2) inset', 
                      fontSize: '12px', 
                      fontWeight: 700, 
                      padding: '12px 16px',
                      backdropFilter: 'blur(24px)'
                    }}
                    labelStyle={{ color: '#38BDF8', fontSize: '11px', marginBottom: '6px', fontWeight: 800 }}
                    formatter={(value: any, name: any) => [
                      <span style={{ color: '#E5E7EB', fontSize: '15px', fontWeight: 900 }}>
                        {Number(value).toFixed(1)} PPM
                      </span>, 
                      <span style={{ color: '#9CA3AF' }}>TDS Level</span>
                    ]}
                    cursor={{ stroke: '#38BDF8', strokeWidth: 2, strokeDasharray: '5 5' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="tds" 
                    stroke="url(#colorTdsStroke)" 
                    strokeWidth={2.5} 
                    fillOpacity={1} 
                    fill="url(#colorTds)"
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

        {/* Right: Temperature Chart */}
        <div className="glass-card p-2 sm:p-3 lg:p-4 rounded-xl flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#A855F7]/5 rounded-full blur-3xl"></div>
          <h3 className="text-[#E5E7EB] font-black text-base sm:text-lg lg:text-xl mb-2 flex items-center gap-2 relative z-10">
            <Thermometer className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-[#A855F7]"/> 
            <span className="hidden sm:inline">Temperature Trends (Last Hour)</span>
            <span className="sm:hidden">Temperature</span>
            <span className="ml-auto text-xs font-bold text-[#A855F7] bg-[#A855F7]/10 px-2 py-1 rounded-lg border border-[#A855F7]/30">
              {latest.temp.toFixed(1)} °C
            </span>
          </h3>
          <div className="w-full flex-1 relative z-10" style={{ minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#A855F7" stopOpacity={0.8}/>
                      <stop offset="50%" stopColor="#9333EA" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#9333EA" stopOpacity={0.1}/>
                    </linearGradient>
                    <linearGradient id="colorTempStroke" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#A855F7"/>
                      <stop offset="100%" stopColor="#9333EA"/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} opacity={0.5} />
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
                    fontSize={9} 
                    tickLine={false} 
                    axisLine={{ stroke: '#1F2937', strokeWidth: 2 }} 
                    fontWeight={600}
                    dx={-5}
                    label={{ value: '°C', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF', fontWeight: 600, fontSize: 10 } }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'rgba(11, 15, 26, 0.98)', 
                      border: '2px solid #A855F7', 
                      borderRadius: '12px', 
                      color: '#E5E7EB', 
                      boxShadow: '0 20px 60px rgba(168, 85, 247, 0.3), 0 0 0 1px rgba(168, 85, 247, 0.2) inset', 
                      fontSize: '12px', 
                      fontWeight: 700, 
                      padding: '12px 16px',
                      backdropFilter: 'blur(24px)'
                    }}
                    labelStyle={{ color: '#A855F7', fontSize: '11px', marginBottom: '6px', fontWeight: 800 }}
                    formatter={(value: any, name: any) => [
                      <span style={{ color: '#E5E7EB', fontSize: '15px', fontWeight: 900 }}>
                        {Number(value).toFixed(2)} °C
                      </span>, 
                      <span style={{ color: '#9CA3AF' }}>Temperature</span>
                    ]}
                    cursor={{ stroke: '#A855F7', strokeWidth: 2, strokeDasharray: '5 5' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="temp" 
                    stroke="url(#colorTempStroke)" 
                    strokeWidth={2.5} 
                    fillOpacity={1} 
                    fill="url(#colorTemp)"
                    animationDuration={1500}
                    animationEasing="ease-in-out"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

      </div>
    </div>
  );
};

export default Dashboard;