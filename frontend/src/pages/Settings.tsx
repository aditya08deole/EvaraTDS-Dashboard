import React from 'react';

const Settings: React.FC = () => {
  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-bold text-[#E5E7EB]">System Calibration</h2>
      
      <div className="glass-card p-6 rounded-xl space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-medium text-[#9CA3AF]">TDS Threshold (Alert Trigger)</label>
          <div className="flex gap-4">
            <input 
              type="number" 
              defaultValue={150} 
              className="bg-[#161E2E] border-2 border-[#1F2937] text-[#E5E7EB] rounded-lg px-4 py-2 w-full focus:ring-2 focus:ring-[#38BDF8] outline-none font-medium" 
            />
            <span className="flex items-center text-[#9CA3AF]">PPM</span>
          </div>
          <p className="text-xs text-[#6B7280]">Alerts will trigger in the dashboard if sensor exceeds this value.</p>
        </div>

        <div className="pt-4 border-t border-[#1F2937]">
           <button className="w-full bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-semibold py-2 rounded-lg transition-all shadow-md">
             Save Configuration
           </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
