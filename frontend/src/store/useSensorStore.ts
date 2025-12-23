import { create } from 'zustand';
import axios from 'axios';

interface SensorReading {
  tds: number;
  temp: number;
  voltage: number;
  created_at: string;
}

interface SensorState {
  latest: SensorReading | null;
  history: SensorReading[];
  status: 'NORMAL' | 'WARNING' | 'CRITICAL';
  isLoading: boolean;
  lastFetch: Date | null;
  fetchData: () => Promise<void>;
}

export const useSensorStore = create<SensorState>((set) => ({
  latest: null,
  history: [],
  status: 'NORMAL',
  isLoading: false,
  lastFetch: null,

  fetchData: async () => {
    set({ isLoading: true });
    try {
      const response = await axios.get('http://localhost:8000/api/v1/dashboard');
      set({
        latest: response.data.latest,
        history: response.data.history,
        status: response.data.system_status,
        lastFetch: new Date(),
        isLoading: false
      });
    } catch (error) {
      console.error('Fetch Failed:', error);
      set({ isLoading: false, status: 'WARNING' });
    }
  }
}));
