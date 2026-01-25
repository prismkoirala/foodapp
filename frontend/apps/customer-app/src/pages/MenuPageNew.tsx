import React, { useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { MapPin, Phone, Award, Plus, Minus, Trash2 } from 'lucide-react';
import { customerApi } from '../lib/api';
import type { Restaurant, MenuItem, OrderData, OrderItem } from '../types';

interface SelectedItem extends MenuItem {
  quantity: number;
  categoryName: string;
}

export const MenuPageNew: React.FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const tableId = searchParams.get('table');

  const [selectedItems, setSelectedItems] = useState<Map<number, SelectedItem>>(new Map());
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');

  // Fetch restaurant with full menu
  const { data: restaurant, isLoading } = useQuery({
    queryKey: ['restaurant', restaurantId],
    queryFn: () => customerApi.getRestaurant(parseInt(restaurantId!)).then(res => res.data),
    enabled: !!restaurantId,
    refetchInterval: 5000, // Refresh every 5 seconds to get manager updates
  });

  // Create order mutation
  const createOrderMutation = useMutation({
    mutationFn: (orderData: OrderData) => customerApi.createOrder(orderData),
    onSuccess: (response) => {
      navigate(`/order/${response.data.order_number}`);
    },
    onError: (error: any) => {
      alert(`Failed to create order: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleAddItem = (item: MenuItem, categoryName: string) => {
    const newMap = new Map(selectedItems);
    const existing = newMap.get(item.id);

    if (existing) {
      newMap.set(item.id, { ...existing, quantity: existing.quantity + 1 });
    } else {
      newMap.set(item.id, { ...item, quantity: 1, categoryName });
    }

    setSelectedItems(newMap);
  };

  const handleRemoveItem = (itemId: number) => {
    const newMap = new Map(selectedItems);
    const existing = newMap.get(itemId);

    if (existing && existing.quantity > 1) {
      newMap.set(itemId, { ...existing, quantity: existing.quantity - 1 });
    } else {
      newMap.delete(itemId);
    }

    setSelectedItems(newMap);
  };

  const handleDeleteItem = (itemId: number) => {
    const newMap = new Map(selectedItems);
    newMap.delete(itemId);
    setSelectedItems(newMap);
  };

  const calculateTotal = () => {
    let total = 0;
    selectedItems.forEach((item) => {
      total += parseFloat(item.price) * item.quantity;
    });
    return total.toFixed(2);
  };

  const handleFinalizeOrder = () => {
    if (selectedItems.size === 0) {
      alert('Please select at least one item');
      return;
    }

    if (!restaurant) return;

    const orderItems: OrderItem[] = Array.from(selectedItems.values()).map(item => ({
      menu_item_id: item.id,
      quantity: item.quantity,
    }));

    const orderData: OrderData = {
      restaurant_slug: restaurant.slug,
      items: orderItems,
      customer_name: customerName,
      customer_phone: customerPhone,
      table_id: tableId ? parseInt(tableId) : undefined,
    };

    createOrderMutation.mutate(orderData);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading menu...</p>
        </div>
      </div>
    );
  }

  if (!restaurant) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Restaurant not found</h2>
          <p className="text-gray-600">Please check the QR code and try again</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-start gap-4">
            {restaurant.logo && (
              <img
                src={restaurant.logo}
                alt={restaurant.name}
                className="w-16 h-16 rounded-xl object-cover"
              />
            )}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{restaurant.name}</h1>
              <div className="flex flex-wrap gap-3 mt-2 text-sm text-gray-600">
                {restaurant.address && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    <span>{restaurant.address}</span>
                  </div>
                )}
                {restaurant.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="w-4 h-4" />
                    <span>{restaurant.phone}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Menu Groups */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {restaurant.menu_groups.map((group) => (
          <div key={group.id} className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">{group.type}</h2>

            {group.categories.map((category) => (
              <div key={category.id} className="mb-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-3">{category.name}</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {category.items.map((item) => {
                    const selectedItem = selectedItems.get(item.id);

                    return (
                      <div
                        key={item.id}
                        className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow border border-gray-200"
                      >
                        {item.is_special_of_day && (
                          <div className="flex items-center gap-1 text-amber-600 text-sm font-medium mb-2">
                            <Award className="w-4 h-4" />
                            <span>Today's Special</span>
                          </div>
                        )}

                        {item.image && (
                          <img
                            src={item.image}
                            alt={item.name}
                            className="w-full h-40 object-cover rounded-lg mb-3"
                          />
                        )}

                        <h4 className="font-semibold text-gray-900 mb-1">{item.name}</h4>
                        {item.description && (
                          <p className="text-sm text-gray-600 mb-3">{item.description}</p>
                        )}

                        <div className="flex items-center justify-between">
                          <span className="text-lg font-bold text-amber-600">
                            Rs. {item.price}
                          </span>

                          {selectedItem ? (
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleRemoveItem(item.id)}
                                className="p-1 rounded-full bg-gray-200 hover:bg-gray-300"
                              >
                                <Minus className="w-4 h-4" />
                              </button>
                              <span className="font-semibold px-2">{selectedItem.quantity}</span>
                              <button
                                onClick={() => handleAddItem(item, category.name)}
                                className="p-1 rounded-full bg-amber-500 text-white hover:bg-amber-600"
                              >
                                <Plus className="w-4 h-4" />
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleAddItem(item, category.name)}
                              className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
                            >
                              Add
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Selected Items Summary */}
      {selectedItems.size > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-2xl z-40">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="mb-4">
              <h3 className="font-semibold text-gray-900 mb-2">Selected Items:</h3>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {Array.from(selectedItems.values()).map((item) => (
                  <div key={item.id} className="flex items-center justify-between text-sm">
                    <div className="flex-1">
                      <span className="font-medium">{item.name}</span>
                      <span className="text-gray-600 ml-2">x{item.quantity}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-semibold">Rs. {(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
                      <button
                        onClick={() => handleDeleteItem(item.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
              <input
                type="text"
                placeholder="Your Name (optional)"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
              <input
                type="tel"
                placeholder="Phone Number (optional)"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Amount</p>
                <p className="text-2xl font-bold text-amber-600">Rs. {calculateTotal()}</p>
              </div>

              <button
                onClick={handleFinalizeOrder}
                disabled={createOrderMutation.isPending}
                className="px-8 py-3 bg-amber-500 text-white font-semibold rounded-lg hover:bg-amber-600 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {createOrderMutation.isPending ? 'Creating Order...' : 'Finalize Order'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Spacer for fixed bottom panel */}
      {selectedItems.size > 0 && <div className="h-64"></div>}
    </div>
  );
};
