import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Manager API
export const managerApi = {
  // Orders
  getOrders: () => api.get('/manager/orders/'),
  getOrderStats: () => api.get('/manager/orders/stats/'),
  updateOrderStatus: (orderId: number, status: string) =>
    api.patch(`/manager/orders/${orderId}/update_status/`, { status }),

  // Menu Items
  getMenuItems: () => api.get('/manager/menu-items/'),
  createMenuItem: (data: any) => api.post('/manager/menu-items/', data),
  updateMenuItem: (itemId: number, data: any) =>
    api.patch(`/manager/menu-items/${itemId}/`, data),
  deleteMenuItem: (itemId: number) =>
    api.delete(`/manager/menu-items/${itemId}/`),
  markSpecial: (itemId: number, isSpecial: boolean) =>
    api.patch(`/manager/menu-items/${itemId}/mark_special/`, { is_special: isSpecial }),
  toggleAvailability: (itemId: number, isAvailable: boolean) =>
    api.patch(`/manager/menu-items/${itemId}/toggle_availability/`, { is_available: isAvailable }),

  // Categories
  getCategories: () => api.get('/manager/categories/'),

  // Restaurant
  getRestaurant: () => api.get('/manager/restaurant/'),
  updateRestaurant: (restaurantId: number, data: any) =>
    api.patch(`/manager/restaurant/${restaurantId}/`, data),

  // Tables
  getTables: () => api.get('/manager/tables/'),
  createTable: (data: any) => api.post('/manager/tables/', data),
  updateTable: (tableId: number, data: any) =>
    api.patch(`/manager/tables/${tableId}/`, data),
  deleteTable: (tableId: number) =>
    api.delete(`/manager/tables/${tableId}/`),
  regenerateQR: (tableId: number) =>
    api.post(`/manager/tables/${tableId}/regenerate_qr/`),
  getQRCode: (tableId: number) =>
    api.get(`/manager/tables/${tableId}/qr_code_download/`),
};

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  getCurrentUser: () => api.get('/auth/me/'),
  updateProfile: (data: any) => api.patch('/auth/me/', data),
  logout: () => api.post('/auth/logout/'),
};

export default api;
