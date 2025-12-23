import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface ChartProps {
  data: any[];
}

const LiveTrendChart: React.FC<ChartProps> = ({ data }) => {
  const formattedData = data.map(item => ({
    time: format(new Date(item.created_at), 'HH:mm'),
    raw_time: item.created_at,
    tds: item.tds
  }));

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="colorTds" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />

          <XAxis dataKey="time" stroke="#475569" fontSize={12} tickLine={false} axisLine={false} minTickGap={30} />

          <YAxis stroke="#475569" fontSize={12} tickLine={false} axisLine={false} domain={[0, 'auto']} />

          <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', color: '#f1f5f9' }} labelStyle={{ color: '#94a3b8' }} />

          <Area type="monotone" dataKey="tds" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorTds)" animationDuration={1500} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LiveTrendChart;
