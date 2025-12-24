import { create } from 'zustand';
import AuthService, { User } from '../services/AuthService';

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,

  initialize: () => {
    const user = AuthService.getCurrentUser();
    set({ user, isAuthenticated: !!user });
  },

  login: async (username: string, password: string) => {
    const user = await AuthService.login(username, password);
    if (user) {
      set({ user, isAuthenticated: true });
      return true;
    }
    return false;
  },

  logout: () => {
    AuthService.logout();
    set({ user: null, isAuthenticated: false });
  },
}));
