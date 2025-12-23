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

  // Format history for charts
  const chartData = data?.history.map((item: any) => ({
    time: format(new Date(item.created_at), 'HH:mm'),
    tds: item.tds,
    temp: item.temp
  })) || [];

  return (
    <div className="p-4 lg:p-6 w-full h-screen flex flex-col space-y-3 overflow-hidden bg-gradient-to-br from-[#0B0F1A]/50 via-transparent to-[#161E2E]/30">
      
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl lg:text-5xl font-black bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] bg-clip-text text-transparent mb-2 leading-tight">EvaraTDS Dashboard</h1>
          <p className="text-[#E5E7EB] text-base lg:text-lg font-semibold">System ID: {data?.channel_info?.name || 'ESP32-NODE-01'}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="flex items-center gap-3">
            <img src="/EvaraTech.png" alt="EvaraTech" className="h-12 lg:h-14 w-auto object-contain" />
            <img src="/IIITH.png" alt="IIITH" className="h-12 lg:h-14 w-auto object-contain" />
          </div>
          <div className="flex items-center gap-2 text-[#9CA3AF] font-medium text-sm">
            <RefreshCw className="w-4 h-4 animate-spin-slow text-[#38BDF8]" />
            <span>Updated: {format(lastUpdated, 'HH:mm:ss')}</span>
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {isCritical && (
        <div className="neon-alert p-3 rounded-xl flex items-center gap-3 shadow-xl">
          <AlertTriangle className="w-6 h-6 text-[#EF4444] flex-shrink-0" />
          <span className="font-black text-base text-[#E5E7EB]">CRITICAL ALERT: High TDS Detected ({latest.tds} PPM). Inspect filtration immediately.</span>
        </div>
      )}

      {/* Stat Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-[#38BDF8]/5 via-transparent to-[#0EA5E9]/5 rounded-2xl blur-xl -z-10"></div>
        <StatCard 
          label="TDS" 
          value={latest.tds.toFixed(0)} 
          unit="PPM" 
          icon={Droplets} 
          color={isCritical ? "red" : "blue"}
          isAlert={isCritical}
        />
        <StatCard 
          label="Temperature" 
          value={latest.temp.toFixed(1)} 
          unit="°C" 
          icon={Thermometer} 
          color="amber" 
        />
        <StatCard 
          label="Sensor Signal" 
          value={latest.voltage.toFixed(3)} 
          unit="V" 
          icon={Zap} 
          color="green" 
        />
      </div>

      {/* Charts Area - Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 flex-1 overflow-hidden relative">
        <div className="absolute -top-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#38BDF8]/30 to-transparent"></div>

        {/* Left: TDS Chart */}
        <div className="glass-card p-4 lg:p-6 rounded-xl flex flex-col">
          <h3 className="text-[#E5E7EB] font-black text-xl lg:text-2xl mb-3 flex items-center gap-3">
            <Activity className="w-6 h-6 lg:w-7 lg:h-7 text-[#38BDF8]"/> TDS Trends (Last Hour)
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
                  <XAxis dataKey="time" stroke="#E5E7EB" fontSize={16} tickLine={false} axisLine={false} fontWeight={700} />
                  <YAxis stroke="#E5E7EB" fontSize={16} tickLine={false} axisLine={false} fontWeight={700} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161E2E', border: '2px solid #38BDF8', borderRadius: '12px', color: '#E5E7EB', boxShadow: '0 4px 16px rgba(0,0,0,0.5)', fontSize: '18px', fontWeight: 700, padding: '12px 16px' }}
                  />
                  <Area type="monotone" dataKey="tds" stroke="#38BDF8" strokeWidth={4} fillOpacity={1} fill="url(#colorTds)" />
                  <Line type="monotone" dataKey={() => 150} stroke="#ef4444" strokeDasharray="5 5" strokeWidth={3} dot={false} isAnimationActive={false}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

        {/* Right: Temperature Chart */}
        <div className="glass-card p-4 lg:p-6 rounded-xl flex flex-col">
          <h3 className="text-[#E5E7EB] font-black text-xl lg:text-2xl mb-3 flex items-center gap-3">
            <Thermometer className="w-6 h-6 lg:w-7 lg:h-7 text-[#38BDF8]"/> Temperature Trends (Last Hour)
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
                  <XAxis dataKey="time" stroke="#E5E7EB" fontSize={16} tickLine={false} axisLine={false} fontWeight={700} />
                  <YAxis stroke="#E5E7EB" fontSize={16} tickLine={false} axisLine={false} fontWeight={700} />
                  <Tooltip contentStyle={{ backgroundColor: '#161E2E', border: '2px solid #F59E0B', borderRadius: '10px', color: '#E5E7EB', fontSize: '18px', fontWeight: 700, boxShadow: '0 4px 16px rgba(0,0,0,0.5)', padding: '12px 16px' }} />
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