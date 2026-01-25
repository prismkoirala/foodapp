// New API format - matches backend structure
export interface MenuItem {
  id: number;
  name: string;
  price: string;
  order: number;
  description: string;
  image: string | null;
  is_special_of_day?: boolean;
  is_available?: boolean;
}

export interface MenuCategory {
  id: number;
  name: string;
  order: number;
  items: MenuItem[];
  image: string | null;
}

export interface MenuGroup {
  id: number;
  type: string;
  order: number;
  categories: MenuCategory[];
}

export interface Restaurant {
  id: number;
  name: string;
  slug: string;
  address: string;
  phone: string;
  logo: string | null;
  menu_groups: MenuGroup[];
  csrfHeaderName?: string;
  csrfToken?: string;
}

export interface CartItem {
  menuItem: MenuItem;
  quantity: number;
  specialInstructions?: string;
}

export interface Table {
  id: number;
  restaurant: number;
  table_number: string;
  qr_code: string;
}

export interface OrderItem {
  menu_item_id: number;
  quantity: number;
  special_instructions?: string;
}

export interface OrderData {
  restaurant_slug: string;
  table_id?: number;
  items: OrderItem[];
  customer_name?: string;
  customer_phone?: string;
  special_instructions?: string;
}

export interface Order {
  id: number;
  order_number: string;
  restaurant: number;
  table: number | null;
  table_number?: string;
  status: 'PENDING' | 'CONFIRMED' | 'PREPARING' | 'READY' | 'SERVED' | 'COMPLETED' | 'CANCELLED';
  total_amount: string;
  customer_name: string;
  customer_phone: string;
  special_instructions: string;
  items: OrderItemDetail[];
  created_at: string;
  confirmed_at: string | null;
  prepared_at: string | null;
  ready_at: string | null;
  served_at: string | null;
  completed_at: string | null;
}

export interface OrderItemDetail {
  id: number;
  menu_item: number;
  menu_item_snapshot: {
    name: string;
    price: string;
    image?: string;
  };
  quantity: number;
  unit_price: string;
  subtotal: string;
  special_instructions: string;
}
