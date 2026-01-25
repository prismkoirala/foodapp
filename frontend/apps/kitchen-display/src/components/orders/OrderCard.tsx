import React from 'react';
import { Clock, User, Phone, ChefHat, AlertCircle } from 'lucide-react';
import type { Order } from '../../types/index.js';
import { formatTime, getElapsedTime, getStatusBorderColor } from '../../lib/utils';
import { Button } from '../ui/Button';

interface OrderCardProps {
  order: Order;
  onStatusUpdate: (orderId: number, newStatus: string) => void;
  isUpdating: boolean;
}

export const OrderCard: React.FC<OrderCardProps> = ({ order, onStatusUpdate, isUpdating }) => {
  const getNextStatus = (currentStatus: string): string | null => {
    const statusFlow: Record<string, string> = {
      PENDING: 'CONFIRMED',
      CONFIRMED: 'PREPARING',
      PREPARING: 'READY',
      READY: 'SERVED',
    };
    return statusFlow[currentStatus] || null;
  };

  const getNextStatusLabel = (currentStatus: string): string => {
    const labels: Record<string, string> = {
      PENDING: 'Confirm',
      CONFIRMED: 'Start Preparing',
      PREPARING: 'Mark Ready',
      READY: 'Mark Served',
    };
    return labels[currentStatus] || 'Update';
  };

  const nextStatus = getNextStatus(order.status);
  const hasSpecialInstructions = order.special_instructions || order.items.some(item => item.special_instructions);

  // Calculate total preparation time
  const totalPrepTime = order.items.reduce(
    (total, item) => Math.max(total, item.menu_item_snapshot.preparation_time * item.quantity),
    0
  );

  // Check if order is taking too long
  const orderAge = new Date().getTime() - new Date(order.created_at).getTime();
  const isUrgent = orderAge > totalPrepTime * 60 * 1000 * 1.5; // 150% of prep time

  return (
    <div
      className={`bg-white rounded-lg border-l-4 ${getStatusBorderColor(order.status)} shadow-md p-3 space-y-2.5 hover:shadow-lg transition-all ${
        isUrgent && order.status !== 'READY' && order.status !== 'SERVED' ? 'ring-2 ring-red-400' : ''
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900">#{order.order_number.split('-').pop()}</h3>
          {order.table_number && (
            <p className="text-xs text-gray-500 font-medium">{order.table_number}</p>
          )}
        </div>
        <div className="text-right">
          <p className="text-xs font-medium text-gray-700">{formatTime(order.created_at)}</p>
          <p className={`text-xs font-semibold ${isUrgent ? 'text-red-600' : 'text-gray-500'}`}>
            {getElapsedTime(order.created_at)}
          </p>
        </div>
      </div>

      {/* Items */}
      <div className="space-y-1.5">
        {order.items.map((item) => (
          <div key={item.id} className="bg-gray-50 rounded-md p-2">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 text-sm flex items-center gap-2">
                  <span className="inline-flex items-center justify-center bg-orange-500 text-white rounded-full w-6 h-6 text-xs font-bold flex-shrink-0">
                    {item.quantity}
                  </span>
                  <span className="truncate">{item.menu_item_snapshot.name}</span>
                </p>
                {item.special_instructions && (
                  <div className="mt-1 flex items-start gap-1 text-orange-600 bg-orange-50 rounded px-2 py-1">
                    <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    <p className="text-xs font-medium">{item.special_instructions}</p>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-1 text-gray-500 text-xs flex-shrink-0">
                <Clock className="w-3 h-3" />
                <span>{item.menu_item_snapshot.preparation_time}m</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Special Instructions */}
      {order.special_instructions && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-2">
          <div className="flex items-start gap-1.5">
            <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-yellow-800 text-xs">Note:</p>
              <p className="text-xs text-gray-700 mt-0.5">{order.special_instructions}</p>
            </div>
          </div>
        </div>
      )}

      {/* Customer Info */}
      {(order.customer_name || order.customer_phone) && (
        <div className="flex items-center gap-3 text-xs text-gray-600 pt-2 border-t border-gray-100">
          {order.customer_name && (
            <div className="flex items-center gap-1">
              <User className="w-3 h-3" />
              <span className="truncate">{order.customer_name}</span>
            </div>
          )}
          {order.customer_phone && (
            <div className="flex items-center gap-1">
              <Phone className="w-3 h-3" />
              <span>{order.customer_phone}</span>
            </div>
          )}
        </div>
      )}

      {/* Action Button */}
      {nextStatus && (
        <Button
          variant={order.status === 'PREPARING' ? 'success' : 'primary'}
          size="md"
          className="w-full"
          onClick={() => onStatusUpdate(order.id, nextStatus)}
          isLoading={isUpdating}
          icon={<ChefHat className="w-4 h-4" />}
        >
          {getNextStatusLabel(order.status)}
        </Button>
      )}

      {/* Prep Time Warning */}
      {isUrgent && order.status !== 'READY' && order.status !== 'SERVED' && (
        <div className="bg-red-50 border border-red-200 rounded-md p-1.5 text-center">
          <p className="text-red-600 text-xs font-semibold">⚠️ Taking longer than expected!</p>
        </div>
      )}
    </div>
  );
};
