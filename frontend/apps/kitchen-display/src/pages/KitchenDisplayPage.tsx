import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChefHat, RefreshCw, Bell, BellOff } from 'lucide-react';
import { kitchenApi } from '../lib/api';
import { KanbanColumn } from '../components/orders/KanbanColumn';
import { Button } from '../components/ui/Button';
import type { OrdersByStatus } from '../types/index.js';
import { playNotificationSound } from '../lib/utils';

export const KitchenDisplayPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [updatingOrderId, setUpdatingOrderId] = useState<number | null>(null);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [previousOrderCount, setPreviousOrderCount] = useState(0);

  // Fetch orders by status
  const { data: ordersByStatus, isLoading } = useQuery({
    queryKey: ['kitchen-orders'],
    queryFn: () => kitchenApi.getOrdersByStatus().then(res => res.data),
    refetchInterval: 3000, // Refresh every 3 seconds
  });

  // Play sound on new orders
  useEffect(() => {
    if (ordersByStatus) {
      const currentCount = ordersByStatus.PENDING?.length || 0;

      if (currentCount > previousOrderCount && previousOrderCount > 0 && soundEnabled) {
        playNotificationSound();
      }

      setPreviousOrderCount(currentCount);
    }
  }, [ordersByStatus, previousOrderCount, soundEnabled]);

  // Update order status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }: { orderId: number; status: string }) =>
      kitchenApi.updateOrderStatus(orderId, status),
    onMutate: ({ orderId }) => {
      setUpdatingOrderId(orderId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kitchen-orders'] });
    },
    onSettled: () => {
      setUpdatingOrderId(null);
    },
  });

  const handleStatusUpdate = (orderId: number, newStatus: string) => {
    updateStatusMutation.mutate({ orderId, status: newStatus });
  };

  const handleManualRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['kitchen-orders'] });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground text-lg">Loading orders...</p>
        </div>
      </div>
    );
  }

  const orders: OrdersByStatus = ordersByStatus || {
    PENDING: [],
    CONFIRMED: [],
    PREPARING: [],
    READY: [],
  };

  const totalOrders = Object.values(orders).reduce((sum, arr) => sum + arr.length, 0);

  return (
    <div className="h-screen flex flex-col bg-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="bg-orange-500 p-3 rounded-xl shadow-md">
              <ChefHat className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Kitchen Display</h1>
              <p className="text-gray-600 text-sm">
                {totalOrders} active {totalOrders === 1 ? 'order' : 'orders'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Sound Toggle */}
            <Button
              variant="ghost"
              size="md"
              onClick={() => setSoundEnabled(!soundEnabled)}
              icon={soundEnabled ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
            >
              {soundEnabled ? 'Sound On' : 'Sound Off'}
            </Button>

            {/* Manual Refresh */}
            <Button
              variant="secondary"
              size="md"
              onClick={handleManualRefresh}
              icon={<RefreshCw className="w-5 h-5" />}
            >
              Refresh
            </Button>

            {/* Auto-refresh indicator */}
            <div className="flex items-center gap-2 text-sm text-gray-600 bg-green-50 px-3 py-1.5 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium">Live</span>
            </div>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-hidden p-4">
        <div className="grid grid-cols-4 gap-4 h-full">
          <KanbanColumn
            status="PENDING"
            orders={orders.PENDING}
            onStatusUpdate={handleStatusUpdate}
            updatingOrderId={updatingOrderId}
          />
          <KanbanColumn
            status="CONFIRMED"
            orders={orders.CONFIRMED}
            onStatusUpdate={handleStatusUpdate}
            updatingOrderId={updatingOrderId}
          />
          <KanbanColumn
            status="PREPARING"
            orders={orders.PREPARING}
            onStatusUpdate={handleStatusUpdate}
            updatingOrderId={updatingOrderId}
          />
          <KanbanColumn
            status="READY"
            orders={orders.READY}
            onStatusUpdate={handleStatusUpdate}
            updatingOrderId={updatingOrderId}
          />
        </div>
      </div>

      {/* New Order Alert */}
      {orders.PENDING.length > 0 && (
        <div className="fixed top-24 right-6 bg-orange-500 text-white px-6 py-3 rounded-xl shadow-2xl animate-bounce z-50">
          <div className="flex items-center gap-3">
            <Bell className="w-6 h-6" />
            <span className="font-bold text-lg">
              {orders.PENDING.length} new {orders.PENDING.length === 1 ? 'order' : 'orders'}!
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
