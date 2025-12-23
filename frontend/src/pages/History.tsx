import React from 'react';
import { useSensorStore } from '../store/useSensorStore';
import { format } from 'date-fns';
import { Download } from 'lucide-react';

const History: React.FC = () => {
  const { history } = useSensorStore();
  const sortedHistory = [...history].reverse();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-5xl font-black text-[#E5E7EB]">Data Logs</h2>
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white rounded-lg text-base font-bold shadow-lg hover:shadow-xl transition-all">
          <Download className="w-5 h-5" />
          Export CSV
        </button>
      </div>

      <div className="glass-card rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[#E5E7EB]">
            <thead className="bg-[#161E2E] text-[#E5E7EB] uppercase text-base font-bold tracking-wider border-b border-[#1F2937]">
              <tr>
                <th className="p-5">Timestamp</th>
                <th className="p-5">TDS (PPM)</th>
                <th className="p-5">Temp (°C)</th>
                <th className="p-5">Voltage (V)</th>
                <th className="p-5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F2937]">
              {sortedHistory.map((row, idx) => (
                <tr key={idx} className="hover:bg-[#161E2E] transition-colors">
                  <td className="p-5 font-mono text-[#9CA3AF] text-base">{format(new Date(row.created_at), 'yyyy-MM-dd HH:mm:ss')}</td>
                  <td className={`p-5 font-bold text-lg ${row.tds > 150 ? 'text-[#EF4444]' : 'text-[#38BDF8]'}`}>{row.tds.toFixed(0)}</td>
                  <td className="p-5 text-[#E5E7EB] text-base">{row.temp.toFixed(1)}</td>
                  <td className="p-5 text-[#E5E7EB] text-base">{row.voltage.toFixed(3)}</td>
                  <td className="p-5">{row.tds > 150 ? (<span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/40">ALERT</span>) : (<span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-[#22C55E]/20 text-[#22C55E] border border-[#22C55E]/40">OK</span>)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default History;
