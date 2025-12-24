// Settings Store - Persistent Calibration Management
import { create } from 'zustand';

interface SystemSettings {
  tdsThreshold: number;
  tempThreshold: number;
  alertEmail: string;
  refreshInterval: number;
  lastModified: Date;
  modifiedBy: string;
}

interface SettingsStore {
  settings: SystemSettings;
  loadSettings: () => void;
  saveSettings: (newSettings: Partial<SystemSettings>, username: string) => void;
  resetToDefaults: () => void;
}

const DEFAULT_SETTINGS: SystemSettings = {
  tdsThreshold: 150,
  tempThreshold: 35,
  alertEmail: '',
  refreshInterval: 3000,
  lastModified: new Date(),
  modifiedBy: 'system'
};

export const useSettingsStore = create<SettingsStore>((set, get) => ({
  settings: DEFAULT_SETTINGS,

  loadSettings: () => {
    const savedSettings = localStorage.getItem('system_settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        set({ settings: { ...DEFAULT_SETTINGS, ...parsed } });
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    }
  },

  saveSettings: (newSettings: Partial<SystemSettings>, username: string) => {
    const updated = {
      ...get().settings,
      ...newSettings,
      lastModified: new Date(),
      modifiedBy: username
    };
    
    localStorage.setItem('system_settings', JSON.stringify(updated));
    set({ settings: updated });
  },

  resetToDefaults: () => {
    localStorage.removeItem('system_settings');
    set({ settings: DEFAULT_SETTINGS });
  },
}));
