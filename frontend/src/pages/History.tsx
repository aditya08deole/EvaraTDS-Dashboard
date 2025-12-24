import React, { useEffect, useState } from 'react';
import { getDashboardData } from '../api';
import { format } from 'date-fns';
import { Download } from 'lucide-react';

const History: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const result = await getDashboardData();
      if (result?.history) {
        setHistory(result.history);
      }
      setLoading(false);
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleExportCSV = () => {
    if (history.length === 0) return;
    
    const headers = ['Timestamp', 'TDS (PPM)', 'Temp (°C)', 'Voltage (V)', 'Status'];
    const rows = history.map(row => [
      format(new Date(row.created_at), 'yyyy-MM-dd HH:mm:ss'),
      row.tds.toFixed(0),
      row.temp.toFixed(1),
      (row.voltage || 0).toFixed(3),
      row.tds > 150 ? 'ALERT' : 'OK'
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evara-tds-logs-${format(new Date(), 'yyyy-MM-dd-HHmmss')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const sortedHistory = [...history].reverse();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-5xl font-black text-[#E5E7EB]">Data Logs</h2>
        <button 
          onClick={handleExportCSV}
          disabled={history.length === 0}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white rounded-lg text-base font-bold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed">
          <Download className="w-5 h-5" />
          Export CSV
        </button>
      </div>

      <div className="backdrop-blur-md bg-[#0F172A]/60 border border-[#1F2937]/60 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-pulse text-[#38BDF8] text-xl font-bold">Loading data...</div>
            </div>
          ) : sortedHistory.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-[#9CA3AF] text-lg">No data available yet. Waiting for sensor readings...</div>
            </div>
          ) : (
            <table className="w-full text-left text-[#E5E7EB]">
              <thead className="bg-[#161E2E]/70 text-[#E5E7EB] uppercase text-base font-bold tracking-wider border-b border-[#1F2937]">
                <tr>
                  <th className="p-5">Timestamp</th>
                  <th className="p-5">TDS (PPM)</th>
                  <th className="p-5">Temp (°C)</th>
                  <th className="p-5">Voltage (V)</th>
                  <th className="p-5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F2937]/50">
                {sortedHistory.map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#161E2E]/40 transition-colors">
                    <td className="p-5 font-mono text-[#9CA3AF] text-base">{format(new Date(row.created_at), 'yyyy-MM-dd HH:mm:ss')}</td>
                    <td className={`p-5 font-bold text-lg ${row.tds > 150 ? 'text-[#EF4444]' : 'text-[#38BDF8]'}`}>{row.tds.toFixed(0)}</td>
                    <td className="p-5 text-[#E5E7EB] text-base">{row.temp.toFixed(1)}</td>
                    <td className="p-5 text-[#E5E7EB] text-base">{(row.voltage || 0).toFixed(3)}</td>
                    <td className="p-5">{row.tds > 150 ? (<span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/40">ALERT</span>) : (<span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-[#22C55E]/20 text-[#22C55E] border border-[#22C55E]/40">OK</span>)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default History;
