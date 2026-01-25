import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CartItem, MenuItem } from '../types/index.js';

interface CartStore {
  items: CartItem[];
  restaurantSlug: string | null;
  tableId: number | null;

  addItem: (menuItem: MenuItem, quantity?: number) => void;
  removeItem: (menuItemId: number) => void;
  updateQuantity: (menuItemId: number, quantity: number) => void;
  updateSpecialInstructions: (menuItemId: number, instructions: string) => void;
  clearCart: () => void;
  setRestaurant: (slug: string) => void;
  setTable: (tableId: number) => void;

  // Computed values
  getTotalItems: () => number;
  getTotalPrice: () => number;
  getItem: (menuItemId: number) => CartItem | undefined;
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],
      restaurantSlug: null,
      tableId: null,

      addItem: (menuItem: MenuItem, quantity = 1) => {
        const existingItem = get().items.find(
          item => item.menuItem.id === menuItem.id
        );

        if (existingItem) {
          set(state => ({
            items: state.items.map(item =>
              item.menuItem.id === menuItem.id
                ? { ...item, quantity: item.quantity + quantity }
                : item
            ),
          }));
        } else {
          set(state => ({
            items: [...state.items, { menuItem, quantity, specialInstructions: '' }],
          }));
        }
      },

      removeItem: (menuItemId: number) => {
        set(state => ({
          items: state.items.filter(item => item.menuItem.id !== menuItemId),
        }));
      },

      updateQuantity: (menuItemId: number, quantity: number) => {
        if (quantity <= 0) {
          get().removeItem(menuItemId);
          return;
        }

        set(state => ({
          items: state.items.map(item =>
            item.menuItem.id === menuItemId
              ? { ...item, quantity }
              : item
          ),
        }));
      },

      updateSpecialInstructions: (menuItemId: number, instructions: string) => {
        set(state => ({
          items: state.items.map(item =>
            item.menuItem.id === menuItemId
              ? { ...item, specialInstructions: instructions }
              : item
          ),
        }));
      },

      clearCart: () => {
        set({ items: [], restaurantSlug: null, tableId: null });
      },

      setRestaurant: (slug: string) => {
        set({ restaurantSlug: slug });
      },

      setTable: (tableId: number) => {
        set({ tableId });
      },

      getTotalItems: () => {
        return get().items.reduce((total, item) => total + item.quantity, 0);
      },

      getTotalPrice: () => {
        return get().items.reduce(
          (total, item) =>
            total + parseFloat(item.menuItem.price) * item.quantity,
          0
        );
      },

      getItem: (menuItemId: number) => {
        return get().items.find(item => item.menuItem.id === menuItemId);
      },
    }),
    {
      name: 'customer-cart-storage',
    }
  )
);
