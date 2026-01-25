import { useQuery } from '@tanstack/react-query';
import { managerApi } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Clock, CheckCircle2, XCircle, Package } from 'lucide-react';

interface Order {
  id: number;
  order_number: string;
  status: string;
  total_amount: string;
  customer_name: string;
  customer_phone: string;
  table_number: string;
  created_at: string;
  items: Array<{
    id: number;
    menu_item_snapshot: {
      name: string;
      price: string;
    };
    quantity: number;
    subtotal: string;
  }>;
}

export default function OrdersPage() {
  const { data: orders = [], isLoading } = useQuery<Order[]>({
    queryKey: ['manager-orders'],
    queryFn: () => managerApi.getOrders().then(res => res.data.results || res.data),
    refetchInterval: 3000, // Refresh every 3 seconds
  });

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      CONFIRMED: 'bg-blue-100 text-blue-800',
      PREPARING: 'bg-orange-100 text-orange-800',
      READY: 'bg-purple-100 text-purple-800',
      SERVED: 'bg-green-100 text-green-800',
      COMPLETED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, React.ReactNode> = {
      PENDING: <Clock className="w-4 h-4" />,
      CONFIRMED: <Package className="w-4 h-4" />,
      PREPARING: <Package className="w-4 h-4" />,
      READY: <CheckCircle2 className="w-4 h-4" />,
      SERVED: <CheckCircle2 className="w-4 h-4" />,
      COMPLETED: <CheckCircle2 className="w-4 h-4" />,
      CANCELLED: <XCircle className="w-4 h-4" />,
    };
    return icons[status] || <Clock className="w-4 h-4" />;
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Orders</h1>
        <p className="text-gray-600 mt-2">
          {orders.length} total {orders.length === 1 ? 'order' : 'orders'}
        </p>
      </div>

      {orders.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Orders Yet</h3>
            <p className="text-gray-600">Orders placed by customers will appear here.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Card key={order.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg font-semibold">
                      Order #{order.order_number}
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(order.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                      {getStatusIcon(order.status)}
                      {order.status}
                    </span>
                    <div className="text-right">
                      <p className="text-sm text-gray-600">Total</p>
                      <p className="text-xl font-bold text-gray-900">
                        NRS {parseFloat(order.total_amount).toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {order.customer_name && (
                    <div>
                      <p className="text-sm text-gray-600">Customer</p>
                      <p className="font-medium">{order.customer_name}</p>
                    </div>
                  )}
                  {order.customer_phone && (
                    <div>
                      <p className="text-sm text-gray-600">Phone</p>
                      <p className="font-medium">{order.customer_phone}</p>
                    </div>
                  )}
                  {order.table_number && (
                    <div>
                      <p className="text-sm text-gray-600">Table</p>
                      <p className="font-medium">{order.table_number}</p>
                    </div>
                  )}
                </div>

                <div className="border-t pt-4">
                  <p className="text-sm font-semibold text-gray-700 mb-2">Items:</p>
                  <div className="space-y-2">
                    {order.items.map((item) => (
                      <div key={item.id} className="flex justify-between items-center text-sm">
                        <div>
                          <span className="font-medium">{item.menu_item_snapshot.name}</span>
                          <span className="text-gray-600 ml-2">x{item.quantity}</span>
                        </div>
                        <span className="font-semibold">
                          NRS {parseFloat(item.subtotal).toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
