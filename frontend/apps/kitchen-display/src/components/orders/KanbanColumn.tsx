import React from 'react';
import type { Order } from '../../types/index.js';
import { OrderCard } from './OrderCard';
import { getStatusColor, getStatusText } from '../../lib/utils';

interface KanbanColumnProps {
  status: string;
  orders: Order[];
  onStatusUpdate: (orderId: number, newStatus: string) => void;
  updatingOrderId: number | null;
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({
  status,
  orders,
  onStatusUpdate,
  updatingOrderId,
}) => {
  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Column Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-xl flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className={`px-4 py-2 rounded-lg ${getStatusColor(status)} font-bold text-sm shadow-sm`}>
            {getStatusText(status)}
          </div>
          <div className="bg-gray-200 text-gray-800 px-3 py-1 rounded-full font-bold text-sm">
            {orders.length}
          </div>
        </div>
      </div>

      {/* Orders - Scrollable */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3" style={{ maxHeight: 'calc(100vh - 200px)' }}>
        {orders.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400 text-sm">No orders</p>
          </div>
        ) : (
          orders.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              onStatusUpdate={onStatusUpdate}
              isUpdating={updatingOrderId === order.id}
            />
          ))
        )}
      </div>
    </div>
  );
};
