import React, { useState, useEffect } from 'react';
import { useSettingsStore } from '../store/useSettingsStore';
import { useAuthStore } from '../store/useAuthStore';
import { Save, RotateCcw, Shield, AlertCircle, CheckCircle2 } from 'lucide-react';

const Settings: React.FC = () => {
  const { settings, saveSettings, resetToDefaults, loadSettings } = useSettingsStore();
  const { user } = useAuthStore();
  const [tdsThreshold, setTdsThreshold] = useState(settings.tdsThreshold);
  const [tempThreshold, setTempThreshold] = useState(settings.tempThreshold);
  const [alertEmail, setAlertEmail] = useState(settings.alertEmail);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [isEditing, setIsEditing] = useState(false);

  // Load settings on mount only
  useEffect(() => {
    const initSettings = async () => {
      await loadSettings();
    };
    initSettings();
  }, [loadSettings]);

  // Update local state when settings change ONLY if not currently editing
  useEffect(() => {
    if (!isEditing) {
      setTdsThreshold(settings.tdsThreshold);
      setTempThreshold(settings.tempThreshold);
      setAlertEmail(settings.alertEmail);
    }
  }, [settings, isEditing]);

  // Admin-only check
  const isAdmin = user?.role === 'admin';

  const handleSave = async () => {
    if (!isAdmin) return;
    
    setSaveStatus('saving');
    
    try {
      await saveSettings({
        tdsThreshold,
        tempThreshold,
        alertEmail
      }, user?.username || 'unknown');
      
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const handleReset = async () => {
    if (!isAdmin) return;
    
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      try {
        await resetToDefaults();
        setSaveStatus('success');
        setTimeout(() => setSaveStatus('idle'), 3000);
      } catch (error) {
        console.error('Failed to reset settings:', error);
        setSaveStatus('error');
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    }
  };

  // Viewer access denied
  if (!isAdmin) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="glass-card p-12 rounded-xl border border-[#F59E0B]/30 bg-[#F59E0B]/5 text-center">
          <Shield className="w-16 h-16 text-[#F59E0B] mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-[#E5E7EB] mb-4">Access Restricted</h2>
          <p className="text-[#9CA3AF] text-lg mb-2">
            This page requires administrator privileges.
          </p>
          <p className="text-[#6B7280] text-sm">
            You are logged in as <span className="text-[#22C55E] font-semibold">{user?.username}</span> (Viewer Role)
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl lg:max-w-5xl space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl lg:text-4xl font-bold text-[#E5E7EB]">System Calibration</h2>
          <p className="text-[#9CA3AF] mt-2">Configure thresholds and alert settings (Global - synced across all devices)</p>
        </div>
        {saveStatus === 'success' && (
          <div className="flex items-center gap-2 bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] px-4 py-2 rounded-lg">
            <CheckCircle2 className="w-5 h-5" />
            <span className="font-semibold">Saved globally!</span>
          </div>
        )}
        {saveStatus === 'error' && (
          <div className="flex items-center gap-2 bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] px-4 py-2 rounded-lg">
            <AlertCircle className="w-5 h-5" />
            <span className="font-semibold">Failed to save</span>
          </div>
        )}
      </div>
      
      <div className="glass-card p-8 lg:p-12 rounded-xl space-y-8">
        {/* TDS Threshold */}
        <div className="space-y-4">
          <label className="text-lg lg:text-xl font-bold text-[#E5E7EB] flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-[#38BDF8]" />
            TDS Alert Threshold
          </label>
          <div className="flex gap-6 items-center">
            <input 
              type="number" 
              value={tdsThreshold}
              onChange={(e) => {
                setTdsThreshold(Number(e.target.value));
                setIsEditing(true);
              }}
              onBlur={() => setTimeout(() => setIsEditing(false), 500)}
              className="bg-[#161E2E] border-2 border-[#1F2937] text-[#E5E7EB] rounded-lg px-6 py-4 w-full focus:ring-2 focus:ring-[#38BDF8] outline-none font-bold text-xl" 
            />
            <span className="flex items-center text-[#9CA3AF] text-lg font-bold whitespace-nowrap">PPM</span>
          </div>
          <p className="text-sm lg:text-base text-[#6B7280]">
            Critical alerts will trigger when TDS exceeds this value. Current: <span className="text-[#38BDF8] font-bold">{tdsThreshold} PPM</span>
          </p>
        </div>

        {/* Temperature Threshold */}
        <div className="space-y-4">
          <label className="text-lg lg:text-xl font-bold text-[#E5E7EB] flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-[#F59E0B]" />
            Temperature Alert Threshold
          </label>
          <div className="flex gap-6 items-center">
            <input 
              type="number" 
              value={tempThreshold}
              onChange={(e) => {
                setTempThreshold(Number(e.target.value));
                setIsEditing(true);
              }}
              onBlur={() => setTimeout(() => setIsEditing(false), 500)}
              className="bg-[#161E2E] border-2 border-[#1F2937] text-[#E5E7EB] rounded-lg px-6 py-4 w-full focus:ring-2 focus:ring-[#F59E0B] outline-none font-bold text-xl" 
            />
            <span className="flex items-center text-[#9CA3AF] text-lg font-bold whitespace-nowrap">°C</span>
          </div>
          <p className="text-sm lg:text-base text-[#6B7280]">
            Warning alerts when temperature exceeds this value. Current: <span className="text-[#F59E0B] font-bold">{tempThreshold}°C</span>
          </p>
        </div>

        {/* Alert Email */}
        <div className="space-y-4">
          <label className="text-lg lg:text-xl font-bold text-[#E5E7EB]">Alert Email Address</label>
          <input 
            type="email" 
            value={alertEmail}
            onChange={(e) => {
              setAlertEmail(e.target.value);
              setIsEditing(true);
            }}
            onBlur={() => setTimeout(() => setIsEditing(false), 500)}
            placeholder="admin@evaratds.com"
            className="bg-[#161E2E] border-2 border-[#1F2937] text-[#E5E7EB] rounded-lg px-6 py-4 w-full focus:ring-2 focus:ring-[#38BDF8] outline-none font-medium text-lg" 
          />
          <p className="text-sm lg:text-base text-[#6B7280]">
            Receive email notifications when critical alerts are triggered (feature coming soon)
          </p>
        </div>

        {/* Last Modified Info */}
        {settings.lastModified && (
          <div className="pt-6 border-t border-[#1F2937]">
            <p className="text-sm text-[#6B7280]">
              Last modified by <span className="text-[#38BDF8] font-semibold">{settings.modifiedBy}</span> on{' '}
              {new Date(settings.lastModified).toLocaleString()}
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="pt-6 border-t border-[#1F2937] flex gap-4">
           <button 
             onClick={handleSave}
             disabled={saveStatus === 'saving'}
             className="flex-1 flex items-center justify-center gap-3 bg-gradient-to-r from-[#38BDF8] to-[#0EA5E9] hover:from-[#0EA5E9] hover:to-[#38BDF8] text-white font-bold py-4 lg:py-5 text-lg lg:text-xl rounded-lg transition-all shadow-lg hover:shadow-xl disabled:opacity-50"
           >
             <Save className="w-6 h-6" />
             {saveStatus === 'saving' ? 'Saving...' : 'Save Configuration'}
           </button>
           
           <button 
             onClick={handleReset}
             className="px-8 flex items-center gap-3 bg-[#EF4444]/10 hover:bg-[#EF4444]/20 border-2 border-[#EF4444]/30 text-[#EF4444] font-bold py-4 lg:py-5 text-lg rounded-lg transition-all"
           >
             <RotateCcw className="w-5 h-5" />
             Reset
           </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
