import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, Clock, ChefHat, Bell, Home } from 'lucide-react';
import { customerApi } from '../lib/api';
import { formatPrice, formatTime, getStatusText } from '../lib/utils';
import { Button } from '../components/ui/Button';
import type { Order } from '../types/index.js';

export const OrderStatusPage: React.FC = () => {
  const { orderNumber } = useParams<{ orderNumber: string }>();
  const navigate = useNavigate();

  const { data: order, isLoading } = useQuery({
    queryKey: ['order', orderNumber],
    queryFn: () => customerApi.getOrderStatus(orderNumber!).then(res => res.data),
    enabled: !!orderNumber,
    refetchInterval: 5000, // Poll every 5 seconds for updates
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading order status...</p>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">Order not found</h2>
          <p className="text-muted-foreground mb-6">The order number you entered was not found</p>
          <Button onClick={() => navigate('/')}>
            <Home className="w-4 h-4" />
            Back to Menu
          </Button>
        </div>
      </div>
    );
  }

  const getStatusStep = (status: string) => {
    const steps = ['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'SERVED'];
    return steps.indexOf(status) + 1;
  };

  const currentStep = getStatusStep(order.status);
  const isCompleted = order.status === 'COMPLETED' || order.status === 'SERVED';
  const isCancelled = order.status === 'CANCELLED';

  return (
    <div className="min-h-screen bg-background pb-12">
      {/* Success Header */}
      <div className="bg-gradient-to-br from-green-500 to-green-600 text-white py-12">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <CheckCircle className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-3xl font-bold mb-2">Order Placed Successfully!</h1>
          <p className="text-green-100 text-lg">Order #{order.order_number}</p>
          {order.table_number && (
            <p className="text-green-100 mt-2">{order.table_number}</p>
          )}
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 -mt-6">
        {/* Status Card */}
        <div className="bg-white rounded-2xl shadow-lg border border-border p-6 mb-6">
          {isCancelled ? (
            <div className="text-center py-6">
              <div className="text-red-500 text-6xl mb-4">✕</div>
              <h2 className="text-2xl font-bold text-foreground mb-2">Order Cancelled</h2>
              <p className="text-muted-foreground">This order has been cancelled</p>
            </div>
          ) : (
            <>
              <h2 className="text-xl font-bold text-foreground mb-6 text-center">
                {isCompleted ? 'Order Completed!' : 'Order Status'}
              </h2>

              {/* Status Timeline */}
              <div className="space-y-4 mb-6">
                {/* Pending */}
                <div className={`flex items-start gap-4 ${currentStep >= 1 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    currentStep >= 1 ? 'bg-green-500 text-white' : 'bg-gray-200'
                  }`}>
                    <Clock className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">Order Received</p>
                    {order.created_at && (
                      <p className="text-sm text-muted-foreground">
                        {formatTime(order.created_at)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Confirmed */}
                <div className={`flex items-start gap-4 ${currentStep >= 2 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    currentStep >= 2 ? 'bg-green-500 text-white' : 'bg-gray-200'
                  }`}>
                    <CheckCircle className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">Order Confirmed</p>
                    {order.confirmed_at && (
                      <p className="text-sm text-muted-foreground">
                        {formatTime(order.confirmed_at)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Preparing */}
                <div className={`flex items-start gap-4 ${currentStep >= 3 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    currentStep >= 3 ? 'bg-green-500 text-white' : 'bg-gray-200'
                  }`}>
                    <ChefHat className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">Being Prepared</p>
                    {order.prepared_at && (
                      <p className="text-sm text-muted-foreground">
                        {formatTime(order.prepared_at)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Ready */}
                <div className={`flex items-start gap-4 ${currentStep >= 4 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    currentStep >= 4 ? 'bg-green-500 text-white' : 'bg-gray-200'
                  }`}>
                    <Bell className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">Ready to Serve</p>
                    {order.ready_at && (
                      <p className="text-sm text-muted-foreground">
                        {formatTime(order.ready_at)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Served */}
                <div className={`flex items-start gap-4 ${currentStep >= 5 ? 'opacity-100' : 'opacity-40'}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    currentStep >= 5 ? 'bg-green-500 text-white' : 'bg-gray-200'
                  }`}>
                    <CheckCircle className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-foreground">Served</p>
                    {order.served_at && (
                      <p className="text-sm text-muted-foreground">
                        {formatTime(order.served_at)}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {!isCompleted && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                  <p className="text-blue-800 font-medium">
                    Current Status: {getStatusText(order.status)}
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    We'll update you as your order progresses
                  </p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Order Details */}
        <div className="bg-white rounded-2xl shadow-sm border border-border p-6 mb-6">
          <h2 className="text-xl font-bold text-foreground mb-4">Order Details</h2>

          <div className="space-y-3 mb-4">
            {order.items.map((item) => (
              <div key={item.id} className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="font-medium text-foreground">
                    {item.quantity}x {item.menu_item_snapshot.name}
                  </p>
                  {item.special_instructions && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Note: {item.special_instructions}
                    </p>
                  )}
                </div>
                <p className="font-semibold text-foreground ml-4">
                  {formatPrice(item.subtotal)}
                </p>
              </div>
            ))}
          </div>

          <div className="border-t border-border pt-4">
            <div className="flex justify-between items-center">
              <span className="text-lg font-bold text-foreground">Total</span>
              <span className="text-2xl font-bold text-primary">
                {formatPrice(order.total_amount)}
              </span>
            </div>
          </div>

          {order.special_instructions && (
            <div className="mt-4 pt-4 border-t border-border">
              <p className="text-sm font-medium text-foreground mb-1">Special Instructions:</p>
              <p className="text-sm text-muted-foreground">{order.special_instructions}</p>
            </div>
          )}
        </div>

        {/* Customer Info */}
        <div className="bg-white rounded-2xl shadow-sm border border-border p-6 mb-6">
          <h2 className="text-xl font-bold text-foreground mb-4">Contact Information</h2>
          <div className="space-y-2">
            <div>
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="font-medium text-foreground">{order.customer_name}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Phone</p>
              <p className="font-medium text-foreground">{order.customer_phone}</p>
            </div>
          </div>
        </div>

        {/* Back to Menu Button */}
        <Button
          variant="outline"
          size="lg"
          className="w-full"
          onClick={() => navigate('/')}
        >
          <Home className="w-5 h-5" />
          Back to Menu
        </Button>
      </div>
    </div>
  );
};
