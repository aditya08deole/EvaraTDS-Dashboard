// Settings Store - Global Calibration Management with API Sync
import { create } from 'zustand';

interface SystemSettings {
  tdsThreshold: number;
  alertEmail: string;
  refreshInterval: number;
  lastModified: Date;
  modifiedBy: string;
}

interface SettingsStore {
  settings: SystemSettings;
  loadSettings: () => Promise<void>;
  saveSettings: (newSettings: Partial<SystemSettings>, username: string) => Promise<void>;
  resetToDefaults: () => Promise<void>;
}

const DEFAULT_SETTINGS: SystemSettings = {
  tdsThreshold: 150,
  alertEmail: '',
  refreshInterval: 3000,
  lastModified: new Date(),
  modifiedBy: 'system'
};

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const useSettingsStore = create<SettingsStore>((set, get) => ({
  settings: DEFAULT_SETTINGS,

  loadSettings: async () => {
    try {
      const response = await fetch(`${API_URL}/settings`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          const newSettings = {
            ...data.settings,
            lastModified: new Date(data.settings.lastModified)
          };
          
          // Only update if settings actually changed (prevents unnecessary re-renders)
          const current = get().settings;
          if (
            current.tdsThreshold !== newSettings.tdsThreshold ||
            current.tempThreshold !== newSettings.tempThreshold ||
            current.alertEmail !== newSettings.alertEmail ||
            current.refreshInterval !== newSettings.refreshInterval ||
            current.lastModified.getTime() !== newSettings.lastModified.getTime()
          ) {
            set({ settings: newSettings });
          }
          return;
        }
      }
    } catch (error) {
      console.error('Failed to load settings from API, using localStorage fallback:', error);
    }
    
    // Fallback to localStorage
    const savedSettings = localStorage.getItem('system_settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        set({ settings: { ...DEFAULT_SETTINGS, ...parsed } });
      } catch (error) {
        console.error('Failed to load settings from localStorage:', error);
      }
    }
  },

  saveSettings: async (newSettings: Partial<SystemSettings>, username: string) => {
    const updated = {
      ...get().settings,
      ...newSettings,
      lastModified: new Date(),
      modifiedBy: username
    };
    
    try {
      const response = await fetch(`${API_URL}/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updated),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          set({ 
            settings: {
              ...data.settings,
              lastModified: new Date(data.settings.lastModified)
            }
          });
          // Also save to localStorage as backup
          localStorage.setItem('system_settings', JSON.stringify(updated));
          return;
        }
      }
    } catch (error) {
      console.error('Failed to save settings to API, using localStorage only:', error);
    }
    
    // Fallback: save to localStorage only
    localStorage.setItem('system_settings', JSON.stringify(updated));
    set({ settings: updated });
  },

  resetToDefaults: async () => {
    try {
      const response = await fetch(`${API_URL}/settings/reset`, {
        method: 'POST',
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          set({ 
            settings: {
              ...data.settings,
              lastModified: new Date(data.settings.lastModified)
            }
          });
          localStorage.removeItem('system_settings');
          return;
        }
      }
    } catch (error) {
      console.error('Failed to reset settings via API:', error);
    }
    
    // Fallback
    localStorage.removeItem('system_settings');
    set({ settings: DEFAULT_SETTINGS });
  },
}));
