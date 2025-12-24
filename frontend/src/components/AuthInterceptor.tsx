import { useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { setupAuthInterceptor } from '../lib/apiClient';

/**
 * Component to configure axios interceptor with Clerk auth token
 * Mount this once in your app root (App.tsx)
 */
export const AuthInterceptor: React.FC = () => {
  const { getToken } = useAuth();

  useEffect(() => {
    setupAuthInterceptor(() => getToken());
  }, [getToken]);

  return null;
};
