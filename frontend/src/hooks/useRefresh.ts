import { useEffect } from 'react';
import { useSensorStore } from '../store/useSensorStore';

export const useRefresh = (intervalMs: number = 15000) => {
  const fetchData = useSensorStore((state) => state.fetchData);

  useEffect(() => {
    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, intervalMs);

    return () => clearInterval(interval);
  }, [fetchData, intervalMs]);
};
