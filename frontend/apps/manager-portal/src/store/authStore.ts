import { create } from 'zustand';
import api from '../lib/api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  restaurant: {
    id: number;
    name: string;
    slug: string;
    logo?: string;
  } | null;
  role: string;
  phone_number: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await api.post('/auth/login/', { username, password });
      const { user, tokens } = response.data;

      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);

      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      api.post('/auth/logout/', { refresh_token: refreshToken }).catch(() => {
        // Ignore errors on logout
      });
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    try {
      const response = await api.get('/auth/me/');
      set({ user: response.data, isAuthenticated: true });
    } catch (error) {
      set({ user: null, isAuthenticated: false });
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },
}));
