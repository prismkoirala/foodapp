import React, { useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ShoppingCart, Search, Award, MapPin, Phone } from 'lucide-react';
import { customerApi } from '../lib/api';
import { MenuItemCard } from '../components/menu/MenuItemCard';
import { CartDrawer } from '../components/cart/CartDrawer';
import { Button } from '../components/ui/Button';
import { useCartStore } from '../store/cartStore';
import type { MenuItem as MenuItemType, MenuCategory } from '../types/index.js';

export const MenuPage: React.FC = () => {
  const { restaurantSlug } = useParams<{ restaurantSlug: string }>();
  const [searchParams] = useSearchParams();
  const tableId = searchParams.get('table');

  const [isCartOpen, setIsCartOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const { getTotalItems, setRestaurant, setTable } = useCartStore();

  // Fetch restaurant info
  const { data: restaurant, isLoading: isLoadingRestaurant } = useQuery({
    queryKey: ['restaurant', restaurantSlug],
    queryFn: () => customerApi.getRestaurant(restaurantSlug!).then(res => res.data),
    enabled: !!restaurantSlug,
  });

  // Fetch menu items
  const { data: menuItems = [], isLoading: isLoadingMenu } = useQuery({
    queryKey: ['menu-items', restaurantSlug, selectedCategory, searchQuery],
    queryFn: () =>
      customerApi
        .getMenuItems(restaurantSlug!, {
          category: selectedCategory || undefined,
          available: true,
          search: searchQuery || undefined,
        })
        .then(res => res.data),
    enabled: !!restaurantSlug,
  });

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ['categories', restaurantSlug],
    queryFn: () => customerApi.getCategories(restaurantSlug!).then(res => res.data),
    enabled: !!restaurantSlug,
  });

  // Set restaurant and table in cart store
  React.useEffect(() => {
    if (restaurantSlug) {
      setRestaurant(restaurantSlug);
    }
    if (tableId) {
      setTable(parseInt(tableId));
    }
  }, [restaurantSlug, tableId, setRestaurant, setTable]);

  if (isLoadingRestaurant) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading menu...</p>
        </div>
      </div>
    );
  }

  const specialItems = menuItems.filter((item: MenuItemType) => item.is_special_of_day);

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="bg-white border-b border-border sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* Restaurant Info */}
          <div className="flex items-start gap-4 mb-4">
            {restaurant?.logo && (
              <img
                src={restaurant.logo}
                alt={restaurant.name}
                className="w-16 h-16 rounded-xl object-cover"
              />
            )}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-foreground">{restaurant?.name}</h1>
              <div className="flex flex-wrap gap-3 mt-2 text-sm text-muted-foreground">
                {restaurant?.address && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    <span>{restaurant.address}</span>
                  </div>
                )}
                {restaurant?.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="w-4 h-4" />
                    <span>{restaurant.phone}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search menu items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="bg-white border-b border-border sticky top-[132px] z-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-2 overflow-x-auto py-3 scrollbar-hide">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap font-medium transition-colors ${
                selectedCategory === null
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-gray-200'
              }`}
            >
              All Items
            </button>
            {categories.map((category: MenuCategory) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg whitespace-nowrap font-medium transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-gray-200'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Special Items Banner */}
        {specialItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Award className="w-6 h-6 text-warning" />
              <h2 className="text-2xl font-bold text-foreground">Today's Specials</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {specialItems.map((item: MenuItemType) => (
                <MenuItemCard key={item.id} item={item} />
              ))}
            </div>
          </div>
        )}

        {/* Menu Items */}
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            {selectedCategory
              ? categories.find((c: MenuCategory) => c.id === selectedCategory)?.name
              : 'All Items'}
          </h2>
        </div>

        {isLoadingMenu ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading items...</p>
          </div>
        ) : menuItems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">No items found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {menuItems
              .filter((item: MenuItemType) => !item.is_special_of_day)
              .map((item: MenuItemType) => (
                <MenuItemCard key={item.id} item={item} />
              ))}
          </div>
        )}
      </div>

      {/* Floating Cart Button */}
      {getTotalItems() > 0 && (
        <button
          onClick={() => setIsCartOpen(true)}
          className="fixed bottom-6 right-6 bg-primary text-primary-foreground rounded-full shadow-2xl p-4 flex items-center gap-3 hover:bg-amber-600 transition-all z-30 hover:scale-105"
        >
          <ShoppingCart className="w-6 h-6" />
          <span className="font-semibold">{getTotalItems()} Items</span>
          <span className="bg-white text-primary px-3 py-1 rounded-full font-bold text-sm">
            View Cart
          </span>
        </button>
      )}

      {/* Cart Drawer */}
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </div>
  );
};
