import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Award, Edit2, Eye, EyeOff, Plus, Trash2, Save, X } from 'lucide-react';
import Button from '../components/ui/Button';

interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: string;
  order: number;
  image: string | null;
  is_available: boolean;
  is_special_of_day: boolean;
  preparation_time: number;
  allergens: string[];
  dietary_tags: string[];
  category: number;
}

interface Category {
  id: number;
  name: string;
}

export default function MenuPage() {
  const queryClient = useQueryClient();
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editForm, setEditForm] = useState({
    name: '',
    description: '',
    price: '',
    preparation_time: 15,
    category: 0,
  });

  const { data: menuItems = [], isLoading } = useQuery<MenuItem[]>({
    queryKey: ['manager-menu-items'],
    queryFn: () => managerApi.getMenuItems().then(res => res.data.results || res.data),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const { data: categories = [] } = useQuery<Category[]>({
    queryKey: ['manager-categories'],
    queryFn: () => managerApi.getCategories().then(res => res.data.results || res.data),
  });

  // Mark special mutation
  const markSpecialMutation = useMutation({
    mutationFn: ({ itemId, isSpecial }: { itemId: number; isSpecial: boolean }) =>
      managerApi.markSpecial(itemId, isSpecial),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-menu-items'] });
    },
  });

  // Toggle availability mutation
  const toggleAvailabilityMutation = useMutation({
    mutationFn: ({ itemId, isAvailable }: { itemId: number; isAvailable: boolean }) =>
      managerApi.toggleAvailability(itemId, isAvailable),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-menu-items'] });
    },
  });

  // Update item mutation
  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, data }: { itemId: number; data: any }) =>
      managerApi.updateMenuItem(itemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-menu-items'] });
      setEditingItem(null);
    },
  });

  // Delete item mutation
  const deleteItemMutation = useMutation({
    mutationFn: (itemId: number) => managerApi.deleteMenuItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-menu-items'] });
    },
  });

  // Create item mutation
  const createItemMutation = useMutation({
    mutationFn: (data: any) => managerApi.createMenuItem(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-menu-items'] });
      setIsCreating(false);
      setEditForm({ name: '', description: '', price: '', preparation_time: 15, category: 0 });
    },
  });

  const handleEditStart = (item: MenuItem) => {
    setEditingItem(item);
    setIsCreating(false);
    setEditForm({
      name: item.name,
      description: item.description,
      price: item.price,
      preparation_time: item.preparation_time,
      category: item.category,
    });
  };

  const handleEditSave = () => {
    if (!editingItem) return;
    updateItemMutation.mutate({
      itemId: editingItem.id,
      data: editForm,
    });
  };

  const handleEditCancel = () => {
    setEditingItem(null);
    setIsCreating(false);
    setEditForm({ name: '', description: '', price: '', preparation_time: 15, category: 0 });
  };

  const handleCreateStart = () => {
    setIsCreating(true);
    setEditingItem(null);
    setEditForm({ name: '', description: '', price: '', preparation_time: 15, category: categories[0]?.id || 0 });
  };

  const handleCreateSave = () => {
    if (!editForm.category) {
      alert('Please select a category');
      return;
    }
    createItemMutation.mutate(editForm);
  };

  const handleDelete = (itemId: number, itemName: string) => {
    if (confirm(`Are you sure you want to delete "${itemName}"?`)) {
      deleteItemMutation.mutate(itemId);
    }
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

  const specialItems = menuItems.filter(item => item.is_special_of_day);
  const availableItems = menuItems.filter(item => item.is_available && !item.is_special_of_day);
  const unavailableItems = menuItems.filter(item => !item.is_available);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Menu Management</h1>
          <p className="text-gray-600 mt-2">
            Manage your restaurant's menu items. Changes reflect instantly in the customer app.
          </p>
        </div>
        <Button
          onClick={handleCreateStart}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add New Item
        </Button>
      </div>

      {/* Create New Item Form */}
      {isCreating && (
        <Card className="mb-6 border-2 border-blue-500 shadow-lg">
          <CardHeader>
            <CardTitle className="text-lg">Create New Menu Item</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={editForm.category}
                  onChange={(e) => setEditForm({ ...editForm, category: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={0}>Select Category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price (NRS)</label>
                <input
                  type="number"
                  step="0.01"
                  value={editForm.price}
                  onChange={(e) => setEditForm({ ...editForm, price: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Prep Time (min)</label>
                <input
                  type="number"
                  value={editForm.preparation_time}
                  onChange={(e) => setEditForm({ ...editForm, preparation_time: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <Button
                onClick={handleCreateSave}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
                size="md"
              >
                <Save className="w-4 h-4 mr-2" />
                Create Item
              </Button>
              <Button
                onClick={handleEditCancel}
                variant="secondary"
                size="md"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Today's Specials */}
      {specialItems.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-6 h-6 text-amber-500" />
            <h2 className="text-2xl font-bold text-gray-900">Today's Specials</h2>
            <span className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-sm font-semibold">
              {specialItems.length}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {specialItems.map((item) => (
              <MenuItemCard
                key={item.id}
                item={item}
                isEditing={editingItem?.id === item.id}
                editForm={editForm}
                setEditForm={setEditForm}
                onEditStart={handleEditStart}
                onEditSave={handleEditSave}
                onEditCancel={handleEditCancel}
                onDelete={handleDelete}
                onMarkSpecial={markSpecialMutation.mutate}
                onToggleAvailability={toggleAvailabilityMutation.mutate}
              />
            ))}
          </div>
        </div>
      )}

      {/* Available Items */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Available Items</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableItems.map((item) => (
            <MenuItemCard
              key={item.id}
              item={item}
              isEditing={editingItem?.id === item.id}
              editForm={editForm}
              setEditForm={setEditForm}
              onEditStart={handleEditStart}
              onEditSave={handleEditSave}
              onEditCancel={handleEditCancel}
              onDelete={handleDelete}
              onMarkSpecial={markSpecialMutation.mutate}
              onToggleAvailability={toggleAvailabilityMutation.mutate}
            />
          ))}
        </div>
      </div>

      {/* Unavailable Items */}
      {unavailableItems.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Unavailable Items</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 opacity-60">
            {unavailableItems.map((item) => (
              <MenuItemCard
                key={item.id}
                item={item}
                isEditing={editingItem?.id === item.id}
                editForm={editForm}
                setEditForm={setEditForm}
                onEditStart={handleEditStart}
                onEditSave={handleEditSave}
                onEditCancel={handleEditCancel}
                onDelete={handleDelete}
                onMarkSpecial={markSpecialMutation.mutate}
                onToggleAvailability={toggleAvailabilityMutation.mutate}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Menu Item Card Component
interface MenuItemCardProps {
  item: MenuItem;
  isEditing: boolean;
  editForm: any;
  setEditForm: (form: any) => void;
  onEditStart: (item: MenuItem) => void;
  onEditSave: () => void;
  onEditCancel: () => void;
  onDelete: (id: number, name: string) => void;
  onMarkSpecial: (data: { itemId: number; isSpecial: boolean }) => void;
  onToggleAvailability: (data: { itemId: number; isAvailable: boolean }) => void;
}

function MenuItemCard({
  item,
  isEditing,
  editForm,
  setEditForm,
  onEditStart,
  onEditSave,
  onEditCancel,
  onDelete,
  onMarkSpecial,
  onToggleAvailability,
}: MenuItemCardProps) {
  if (isEditing) {
    return (
      <Card className="border-2 border-blue-500 shadow-lg">
        <CardHeader>
          <CardTitle className="text-lg">Edit Item</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Price (NRS)</label>
              <input
                type="number"
                step="0.01"
                value={editForm.price}
                onChange={(e) => setEditForm({ ...editForm, price: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prep Time (min)</label>
              <input
                type="number"
                value={editForm.preparation_time}
                onChange={(e) => setEditForm({ ...editForm, preparation_time: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <Button
              onClick={onEditSave}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
              size="md"
            >
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
            <Button
              onClick={onEditCancel}
              variant="secondary"
              size="md"
            >
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="hover:shadow-lg transition-all">
      <CardContent className="p-4">
        {/* Badges */}
        <div className="flex gap-2 mb-3">
          {item.is_special_of_day && (
            <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-800 px-2 py-1 rounded-full text-xs font-semibold">
              <Award className="w-3 h-3" />
              Special
            </span>
          )}
          {!item.is_available && (
            <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-semibold">
              Unavailable
            </span>
          )}
        </div>

        {/* Item Info */}
        <h3 className="font-bold text-gray-900 text-lg mb-1">{item.name}</h3>
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{item.description}</p>
        <div className="flex items-center justify-between mb-4">
          <span className="text-2xl font-bold text-blue-600">NRS {parseFloat(item.price).toFixed(2)}</span>
          <span className="text-sm text-gray-500">{item.preparation_time} min</span>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-2">
          {/* Mark Special */}
          <button
            onClick={() => onMarkSpecial({ itemId: item.id, isSpecial: !item.is_special_of_day })}
            className={`flex items-center justify-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              item.is_special_of_day
                ? 'bg-amber-500 text-white hover:bg-amber-600'
                : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200'
            }`}
          >
            <Award className="w-4 h-4" />
            {item.is_special_of_day ? 'Unmark' : 'Mark Special'}
          </button>

          {/* Toggle Availability */}
          <button
            onClick={() => onToggleAvailability({ itemId: item.id, isAvailable: !item.is_available })}
            className={`flex items-center justify-center gap-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              item.is_available
                ? 'bg-green-500 text-white hover:bg-green-600'
                : 'bg-gray-500 text-white hover:bg-gray-600'
            }`}
          >
            {item.is_available ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            {item.is_available ? 'Available' : 'Unavailable'}
          </button>

          {/* Edit */}
          <button
            onClick={() => onEditStart(item)}
            className="flex items-center justify-center gap-1 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-100 border border-blue-200 transition-colors"
          >
            <Edit2 className="w-4 h-4" />
            Edit
          </button>

          {/* Delete */}
          <button
            onClick={() => onDelete(item.id, item.name)}
            className="flex items-center justify-center gap-1 px-3 py-2 bg-red-50 text-red-700 rounded-lg text-sm font-medium hover:bg-red-100 border border-red-200 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>
      </CardContent>
    </Card>
  );
}
