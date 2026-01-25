import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UtensilsCrossed,
  ShoppingBag,
  QrCode,
  Settings,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { cn } from '../../lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Menu', href: '/menu', icon: UtensilsCrossed },
  { name: 'Orders', href: '/orders', icon: ShoppingBag },
  { name: 'Tables & QR', href: '/tables', icon: QrCode },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <div className="flex h-full w-64 flex-col bg-gray-900 text-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-gray-800 px-6">
        <div className="bg-primary p-2 rounded-lg">
          <UtensilsCrossed className="h-6 w-6 text-white" />
        </div>
        <span className="text-xl font-semibold">Manager Portal</span>
      </div>

      {/* Restaurant Info */}
      {user?.restaurant && (
        <div className="border-b border-gray-800 px-6 py-4">
          <p className="text-xs text-gray-400 mb-1">Restaurant</p>
          <p className="font-medium truncate">{user.restaurant.name}</p>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-300 hover:bg-gray-800/50 hover:text-white'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* User Info & Logout */}
      <div className="border-t border-gray-800 p-4">
        <div className="mb-3">
          <p className="text-sm font-medium">{user?.first_name || user?.username}</p>
          <p className="text-xs text-gray-400">{user?.role?.replace('_', ' ')}</p>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800/50 hover:text-white transition-colors"
        >
          <LogOut className="h-5 w-5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
