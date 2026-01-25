import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh
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
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Kitchen Display API
export const kitchenApi = {
  // Get all active orders
  getActiveOrders: () => api.get('/kitchen/orders/'),

  // Get orders by status (Kanban view)
  getOrdersByStatus: () => api.get('/kitchen/orders/by_status/'),

  // Update order status
  updateOrderStatus: (orderId: number, status: string) =>
    api.patch(`/kitchen/orders/${orderId}/update_status/`, { status }),

  // Get order details
  getOrderDetail: (orderId: number) =>
    api.get(`/kitchen/orders/${orderId}/`),
};

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),

  getCurrentUser: () => api.get('/auth/me/'),
};
