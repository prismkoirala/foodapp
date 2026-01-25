import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { ShoppingBag, DollarSign, Clock, TrendingUp } from 'lucide-react';
import api from '../lib/api';
import { formatCurrency } from '../lib/utils';

export default function DashboardPage() {
  const navigate = useNavigate();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['orderStats'],
    queryFn: async () => {
      const response = await api.get('/manager/orders/stats/');
      return response.data;
    },
  });

  const statsCards = [
    {
      title: 'Total Orders Today',
      value: stats?.total_orders || 0,
      icon: ShoppingBag,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Revenue Today',
      value: formatCurrency(Number(stats?.total_revenue) || 0),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Pending Orders',
      value: stats?.pending_orders || 0,
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      title: 'Completed Orders',
      value: stats?.completed_orders || 0,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's what's happening today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsCards.map((stat) => (
          <Card key={stat.title} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {isLoading ? '...' : stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Order Status Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Order Status Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { label: 'Pending', count: stats?.pending_orders || 0, color: 'bg-yellow-500' },
                { label: 'Confirmed', count: stats?.confirmed_orders || 0, color: 'bg-blue-500' },
                { label: 'Preparing', count: stats?.preparing_orders || 0, color: 'bg-orange-500' },
                { label: 'Ready', count: stats?.ready_orders || 0, color: 'bg-purple-500' },
                { label: 'Served', count: stats?.served_orders || 0, color: 'bg-green-500' },
              ].map((status) => (
                <div key={status.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${status.color}`} />
                    <span className="text-sm font-medium text-gray-700">{status.label}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900">
                    {isLoading ? '...' : status.count}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <button
                onClick={() => navigate('/orders')}
                className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors"
              >
                <p className="font-medium text-gray-900">View All Orders</p>
                <p className="text-sm text-gray-600">Manage and track orders</p>
              </button>
              <button
                onClick={() => navigate('/menu')}
                className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors"
              >
                <p className="font-medium text-gray-900">Edit Menu</p>
                <p className="text-sm text-gray-600">Update menu items and prices</p>
              </button>
              <button
                onClick={() => navigate('/tables')}
                className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:border-primary hover:bg-primary/5 transition-colors"
              >
                <p className="font-medium text-gray-900">Manage Tables</p>
                <p className="text-sm text-gray-600">View QR codes and table status</p>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
