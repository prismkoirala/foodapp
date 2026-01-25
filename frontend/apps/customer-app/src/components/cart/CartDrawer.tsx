import React from 'react';
import { X, Plus, Minus, Trash2, ShoppingCart } from 'lucide-react';
import { useCartStore } from '../../store/cartStore';
import { formatPrice } from '../../lib/utils';
import { Button } from '../ui/Button';
import { useNavigate } from 'react-router-dom';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CartDrawer: React.FC<CartDrawerProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { items, getTotalPrice, getTotalItems, updateQuantity, removeItem } = useCartStore();

  const handleCheckout = () => {
    onClose();
    navigate('/checkout');
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold text-foreground">
              Your Cart ({getTotalItems()})
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-secondary rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Cart Items */}
        <div className="flex-1 overflow-y-auto p-4">
          {items.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingCart className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground text-lg">Your cart is empty</p>
              <p className="text-sm text-muted-foreground mt-2">
                Add items from the menu to get started
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item) => (
                <div
                  key={item.menuItem.id}
                  className="bg-secondary rounded-xl p-4"
                >
                  <div className="flex gap-3">
                    {/* Image */}
                    {item.menuItem.image && (
                      <img
                        src={item.menuItem.image}
                        alt={item.menuItem.name}
                        className="w-20 h-20 rounded-lg object-cover"
                      />
                    )}

                    {/* Details */}
                    <div className="flex-1">
                      <h4 className="font-semibold text-foreground">
                        {item.menuItem.name}
                      </h4>
                      <p className="text-sm text-primary font-semibold mt-1">
                        {formatPrice(item.menuItem.price)}
                      </p>

                      {/* Quantity Controls */}
                      <div className="flex items-center gap-3 mt-3">
                        <button
                          onClick={() => updateQuantity(item.menuItem.id, item.quantity - 1)}
                          className="w-8 h-8 rounded-lg bg-white hover:bg-gray-100 flex items-center justify-center transition-colors"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="font-semibold text-foreground min-w-[2rem] text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.menuItem.id, item.quantity + 1)}
                          className="w-8 h-8 rounded-lg bg-white hover:bg-gray-100 flex items-center justify-center transition-colors"
                        >
                          <Plus className="w-4 h-4" />
                        </button>

                        {/* Remove Button */}
                        <button
                          onClick={() => removeItem(item.menuItem.id)}
                          className="ml-auto text-error hover:bg-red-50 p-2 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Subtotal */}
                      <p className="text-sm text-muted-foreground mt-2">
                        Subtotal: {formatPrice(parseFloat(item.menuItem.price) * item.quantity)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="border-t border-border p-4 bg-white">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg font-semibold text-foreground">Total</span>
              <span className="text-2xl font-bold text-primary">
                {formatPrice(getTotalPrice())}
              </span>
            </div>
            <Button
              size="lg"
              className="w-full"
              onClick={handleCheckout}
            >
              Proceed to Checkout
            </Button>
          </div>
        )}
      </div>
    </>
  );
};
