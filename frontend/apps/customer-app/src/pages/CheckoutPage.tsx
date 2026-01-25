import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { ArrowLeft, CheckCircle } from 'lucide-react';
import { customerApi } from '../lib/api';
import { useCartStore } from '../store/cartStore';
import { formatPrice } from '../lib/utils';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import type { OrderData } from '../types/index.js';

export const CheckoutPage: React.FC = () => {
  const navigate = useNavigate();
  const { items, restaurantSlug, tableId, getTotalPrice, clearCart } = useCartStore();

  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [specialInstructions, setSpecialInstructions] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const createOrderMutation = useMutation({
    mutationFn: (orderData: OrderData) => customerApi.createOrder(orderData),
    onSuccess: (response) => {
      clearCart();
      navigate(`/order/${response.data.order_number}`);
    },
    onError: (error: any) => {
      console.error('Order creation failed:', error);
      if (error.response?.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Failed to create order. Please try again.' });
      }
    },
  });

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!customerName.trim()) {
      newErrors.customerName = 'Name is required';
    }

    if (!customerPhone.trim()) {
      newErrors.customerPhone = 'Phone number is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (items.length === 0) {
      setErrors({ general: 'Your cart is empty' });
      return;
    }

    if (!restaurantSlug) {
      setErrors({ general: 'Restaurant information is missing' });
      return;
    }

    const orderData: OrderData = {
      restaurant: restaurantSlug,
      table_id: tableId || undefined,
      items: items.map((item) => ({
        menu_item_id: item.menuItem.id,
        quantity: item.quantity,
        special_instructions: item.specialInstructions,
      })),
      customer_name: customerName,
      customer_phone: customerPhone,
      special_instructions: specialInstructions,
    };

    createOrderMutation.mutate(orderData);
  };

  if (items.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">Your cart is empty</h2>
          <p className="text-muted-foreground mb-6">Add items to your cart to place an order</p>
          <Button onClick={() => navigate(-1)}>
            <ArrowLeft className="w-4 h-4" />
            Back to Menu
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-12">
      {/* Header */}
      <div className="bg-white border-b border-border sticky top-0 z-30 shadow-sm">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-secondary rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-2xl font-bold text-foreground">Checkout</h1>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Order Summary */}
        <div className="bg-white rounded-2xl shadow-sm border border-border p-6 mb-6">
          <h2 className="text-xl font-bold text-foreground mb-4">Order Summary</h2>

          <div className="space-y-4 mb-6">
            {items.map((item) => (
              <div key={item.menuItem.id} className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="font-medium text-foreground">
                    {item.quantity}x {item.menuItem.name}
                  </p>
                  {item.specialInstructions && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Note: {item.specialInstructions}
                    </p>
                  )}
                </div>
                <p className="font-semibold text-foreground ml-4">
                  {formatPrice(parseFloat(item.menuItem.price) * item.quantity)}
                </p>
              </div>
            ))}
          </div>

          <div className="border-t border-border pt-4">
            <div className="flex justify-between items-center">
              <span className="text-lg font-bold text-foreground">Total</span>
              <span className="text-2xl font-bold text-primary">
                {formatPrice(getTotalPrice())}
              </span>
            </div>
          </div>
        </div>

        {/* Customer Information Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-border p-6">
          <h2 className="text-xl font-bold text-foreground mb-6">Your Information</h2>

          {errors.general && (
            <div className="bg-red-50 border border-error rounded-lg p-4 mb-6">
              <p className="text-error text-sm">{errors.general}</p>
            </div>
          )}

          <div className="space-y-4 mb-6">
            <Input
              label="Name"
              type="text"
              placeholder="Enter your name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              error={errors.customerName}
              required
            />

            <Input
              label="Phone Number"
              type="tel"
              placeholder="Enter your phone number"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              error={errors.customerPhone}
              required
            />

            <Textarea
              label="Special Instructions (Optional)"
              placeholder="Any special requests or dietary restrictions?"
              value={specialInstructions}
              onChange={(e) => setSpecialInstructions(e.target.value)}
              rows={3}
            />
          </div>

          <Button
            type="submit"
            size="lg"
            className="w-full"
            isLoading={createOrderMutation.isPending}
            icon={<CheckCircle className="w-5 h-5" />}
          >
            {createOrderMutation.isPending ? 'Placing Order...' : 'Place Order'}
          </Button>

          <p className="text-sm text-muted-foreground text-center mt-4">
            By placing this order, you confirm that the information provided is accurate.
          </p>
        </form>
      </div>
    </div>
  );
};
