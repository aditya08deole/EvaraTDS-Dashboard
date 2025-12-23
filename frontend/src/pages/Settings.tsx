import React from 'react';

const Settings: React.FC = () => {
  return (
    <div className="max-w-4xl lg:max-w-5xl space-y-8">
      <h2 className="text-3xl lg:text-4xl font-bold text-[#E5E7EB] text-center">System Calibration</h2>
      
      <div className="glass-card p-8 lg:p-12 rounded-xl space-y-8">
        <div className="space-y-4">
          <label className="text-lg lg:text-xl font-medium text-[#9CA3AF]">TDS Threshold (Alert Trigger)</label>
          <div className="flex gap-6">
            <input 
              type="number" 
              defaultValue={150} 
              className="bg-[#161E2E] border-2 border-[#1F2937] text-[#E5E7EB] rounded-lg px-6 py-4 w-full focus:ring-2 focus:ring-[#38BDF8] outline-none font-medium text-lg" 
            />
            <span className="flex items-center text-[#9CA3AF] text-lg font-medium">PPM</span>
          </div>
          <p className="text-sm lg:text-base text-[#6B7280]">Alerts will trigger in the dashboard if sensor exceeds this value.</p>
        </div>

        <div className="pt-6 border-t border-[#1F2937]">
           <button className="w-full bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-semibold py-4 lg:py-5 text-lg lg:text-xl rounded-lg transition-all shadow-md">
             Save Configuration
           </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
