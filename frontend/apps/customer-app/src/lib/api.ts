import axios from 'axios';
import type { Restaurant, OrderData, Order } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Customer API endpoints
export const customerApi = {
  // Restaurant & Menu (new nested format)
  getRestaurant: (restaurantId: number) =>
    api.get<Restaurant>(`/restaurants/${restaurantId}/`),

  getRestaurants: () =>
    api.get<Restaurant[]>('/restaurants/'),

  // QR Code
  resolveQR: (qrCode: string) =>
    api.get<{ restaurant_id: number; table_id?: number }>(`/qr/${qrCode}/`),

  // Orders
  createOrder: (orderData: OrderData) =>
    api.post<Order>('/orders/', orderData),

  getOrderStatus: (orderNumber: string) =>
    api.get<Order>(`/orders/${orderNumber}/`),
};

export default api;
