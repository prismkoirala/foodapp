export interface User {
  id: number;
  username: string;
  email: string;
  role: 'SUPER_ADMIN' | 'RESTAURANT_MANAGER' | 'KITCHEN_STAFF';
  restaurant: {
    id: number;
    name: string;
    slug: string;
  } | null;
}

export interface OrderItem {
  id: number;
  menu_item: number;
  menu_item_snapshot: {
    name: string;
    price: string;
    preparation_time: number;
  };
  quantity: number;
  unit_price: string;
  subtotal: string;
  special_instructions: string;
}

export interface Order {
  id: number;
  order_number: string;
  restaurant: number;
  table: number | null;
  table_number: string;
  status: 'PENDING' | 'CONFIRMED' | 'PREPARING' | 'READY' | 'SERVED' | 'COMPLETED' | 'CANCELLED';
  total_amount: string;
  customer_name: string;
  customer_phone: string;
  special_instructions: string;
  items: OrderItem[];
  created_at: string;
  confirmed_at: string | null;
  prepared_at: string | null;
  ready_at: string | null;
  served_at: string | null;
  completed_at: string | null;
}

export interface OrdersByStatus {
  PENDING: Order[];
  CONFIRMED: Order[];
  PREPARING: Order[];
  READY: Order[];
}
