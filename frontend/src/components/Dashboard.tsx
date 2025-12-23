import { useEffect, useState } from 'react';
import { getDashboardData } from '../api';
import StatCard from './StatCard';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Activity, Droplets, Thermometer, Zap, AlertTriangle, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';

const Dashboard = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

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
    const interval = setInterval(fetchData, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="min-h-screen flex items-center justify-center text-[#38BDF8] text-3xl font-bold">Initializing EvaraTDS...</div>;

  const latest = data?.latest || { tds: 0, temp: 0, voltage: 0 };
  const isCritical = latest.tds > 150;
  const isSafe = latest.tds <= 150;

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
        <div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] bg-clip-text text-transparent mb-1 sm:mb-2 leading-tight">EvaraTDS Dashboard</h1>
          <p className="text-[#E5E7EB] text-xs sm:text-sm lg:text-base font-semibold">System ID: {data?.channel_info?.name || 'ESP32-NODE-01'}</p>
        </div>
        <div className="flex flex-col sm:items-end gap-2 sm:gap-3">
          <div className="flex items-center gap-2 sm:gap-3 justify-center sm:justify-end">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-[40px] sm:h-[48px] lg:h-[60px] w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-[40px] sm:h-[48px] lg:h-[60px] w-auto object-contain" />
          </div>
          <div className="flex items-center gap-1 sm:gap-2 text-[#9CA3AF] font-medium text-xs justify-center sm:justify-end mt-2 sm:mt-4">
            <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4 animate-spin-slow text-[#38BDF8]" />
            <span>Updated: {format(lastUpdated, 'HH:mm:ss')}</span>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {isCritical ? (
        <div className="neon-alert p-3 sm:p-4 rounded-xl flex items-center gap-2 sm:gap-3 shadow-xl w-full md:w-3/4 lg:w-1/2">
          <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-[#EF4444] flex-shrink-0" />
          <span className="font-black text-sm sm:text-base text-[#E5E7EB] leading-tight">CRITICAL ALERT: High TDS Detected ({latest.tds} PPM). Inspect filtration immediately.</span>
        </div>
      ) : isSafe ? (
        <div className="neon-alert p-3 sm:p-4 rounded-xl flex items-center gap-2 sm:gap-3 shadow-lg border border-[#22C55E]/20 animate-pulse shadow-[0_0_20px_rgba(34,197,94,0.45)] w-full md:w-3/4 lg:w-1/2">
          <Droplets className="w-5 h-5 sm:w-6 sm:h-6 text-[#22C55E] flex-shrink-0" />
          <span className="font-black text-sm sm:text-base text-[#E5E7EB] leading-tight">SAFE: TDS within acceptable range ({latest.tds} PPM).</span>
        </div>
      ) : null}

      {/* Stat Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-6 relative items-stretch">
        <div className="absolute inset-0 bg-gradient-to-r from-[#38BDF8]/5 via-transparent to-[#0EA5E9]/5 rounded-2xl blur-xl -z-10"></div>
        <div className="h-36 sm:h-40 lg:h-44 xl:h-48 sm:col-span-2 lg:col-span-1"><StatCard 
          label="TDS" 
          value={latest.tds.toFixed(0)} 
          unit="PPM" 
          icon={Droplets} 
          color={isCritical ? "red" : isSafe ? "green" : "blue"}
          isAlert={isCritical}
          isSafe={isSafe}
        /></div>
        <div className="h-36 sm:h-40 lg:h-44 xl:h-48"><StatCard 
          label="Temperature" 
          value={latest.temp.toFixed(1)} 
          unit="°C" 
          icon={Thermometer} 
          color="amber" 
        /></div>
        <div className="h-36 sm:h-40 lg:h-44 xl:h-48"><StatCard 
          label="Sensor Signal" 
          value={latest.voltage.toFixed(3)} 
          unit="V" 
          icon={Zap} 
          color="green" 
        /></div>
      </div>

      {/* Charts Area - Responsive */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 h-64 sm:h-80 md:h-96 lg:h-96 xl:h-[420px] overflow-hidden relative">
        <div className="absolute -top-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#38BDF8]/30 to-transparent"></div>

        {/* Left: TDS Chart */}
        <div className="glass-card p-2 sm:p-4 lg:p-5 rounded-xl flex flex-col">
          <h3 className="text-[#E5E7EB] font-black text-lg sm:text-xl lg:text-2xl mb-2 sm:mb-3 flex items-center gap-2 sm:gap-3">
            <Activity className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-[#38BDF8]"/> 
            <span className="hidden sm:inline">TDS Trends (Last Hour)</span>
            <span className="sm:hidden">TDS Trends</span>
          </h3>
          <div className="w-full flex-1" style={{ minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorTds" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.7}/>
                      <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                  <XAxis dataKey="time" stroke="#E5E7EB" fontSize={10} sm:fontSize={12} tickLine={false} axisLine={false} fontWeight={700} />
                  <YAxis stroke="#E5E7EB" fontSize={10} sm:fontSize={12} tickLine={false} axisLine={false} fontWeight={700} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161E2E', border: '2px solid #38BDF8', borderRadius: '12px', color: '#E5E7EB', boxShadow: '0 4px 16px rgba(0,0,0,0.5)', fontSize: '10px sm:fontSize: 12px', fontWeight: 700, padding: '4px 8px sm:padding: 6px 10px' }}
                  />
                  <Area type="monotone" dataKey="tds" stroke="#38BDF8" strokeWidth={4} fillOpacity={1} fill="url(#colorTds)" />
                  <Line type="monotone" dataKey={() => 150} stroke="#ef4444" strokeDasharray="5 5" strokeWidth={3} dot={false} isAnimationActive={false}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

        {/* Right: Temperature Chart */}
        <div className="glass-card p-2 sm:p-4 lg:p-5 rounded-xl flex flex-col">
          <h3 className="text-[#E5E7EB] font-black text-lg sm:text-xl lg:text-2xl mb-2 sm:mb-3 flex items-center gap-2 sm:gap-3">
            <Thermometer className="w-5 h-5 sm:w-6 sm:h-6 lg:w-7 lg:h-7 text-[#38BDF8]"/> 
            <span className="hidden sm:inline">Temperature Trends (Last Hour)</span>
            <span className="sm:hidden">Temperature</span>
          </h3>
          <div className="w-full flex-1" style={{ minHeight: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.7}/>
                      <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                  <XAxis dataKey="time" stroke="#E5E7EB" fontSize={10} sm:fontSize={12} tickLine={false} axisLine={false} fontWeight={700} />
                  <YAxis stroke="#E5E7EB" fontSize={10} sm:fontSize={12} tickLine={false} axisLine={false} fontWeight={700} />
                  <Tooltip contentStyle={{ backgroundColor: '#161E2E', border: '2px solid #F59E0B', borderRadius: '10px', color: '#E5E7EB', fontSize: '10px sm:fontSize: 12px', fontWeight: 700, boxShadow: '0 4px 16px rgba(0,0,0,0.5)', padding: '4px 8px sm:padding: 6px 10px' }} />
                  <Area type="monotone" dataKey="temp" stroke="#F59E0B" strokeWidth={4} fillOpacity={1} fill="url(#colorTemp)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

      </div>
    </div>
  );
};

export default Dashboard;