import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi, authApi } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Save, User, Building2 } from 'lucide-react';
import Button from '../components/ui/Button';

interface Restaurant {
  id: number;
  name: string;
  slug: string;
  address: string;
  phone: string;
  logo: string | null;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export default function SettingsPage() {
  const queryClient = useQueryClient();

  // Fetch restaurant data
  const { data: restaurant, isLoading: restaurantLoading } = useQuery<Restaurant>({
    queryKey: ['manager-restaurant'],
    queryFn: () => managerApi.getRestaurant().then(res => {
      // Handle both single object and array responses
      const data = res.data.results ? res.data.results[0] : res.data;
      return data;
    }),
  });

  // Fetch user profile
  const { data: user, isLoading: userLoading } = useQuery<UserProfile>({
    queryKey: ['user-profile'],
    queryFn: () => authApi.getCurrentUser().then(res => res.data),
  });

  // Restaurant form state
  const [restaurantForm, setRestaurantForm] = useState({
    name: '',
    address: '',
    phone: '',
  });

  // User form state
  const [userForm, setUserForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
  });

  // Update forms when data loads
  useEffect(() => {
    if (restaurant) {
      setRestaurantForm({
        name: restaurant.name,
        address: restaurant.address,
        phone: restaurant.phone,
      });
    }
  }, [restaurant]);

  useEffect(() => {
    if (user) {
      setUserForm({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
      });
    }
  }, [user]);

  // Update restaurant mutation
  const updateRestaurantMutation = useMutation({
    mutationFn: (data: any) => managerApi.updateRestaurant(restaurant?.id || 0, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-restaurant'] });
      alert('Restaurant settings updated successfully!');
    },
    onError: (error: any) => {
      alert(`Failed to update: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Update user mutation
  const updateUserMutation = useMutation({
    mutationFn: (data: any) => authApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
      alert('Profile updated successfully!');
    },
    onError: (error: any) => {
      alert(`Failed to update: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleRestaurantSave = () => {
    updateRestaurantMutation.mutate(restaurantForm);
  };

  const handleUserSave = () => {
    updateUserMutation.mutate(userForm);
  };

  if (restaurantLoading || userLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your restaurant and profile settings. Changes reflect instantly across all apps.
        </p>
      </div>

      <div className="space-y-6">
        {/* Restaurant Settings */}
        <Card>
          <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-blue-600" />
              <CardTitle className="text-lg">Restaurant Information</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Restaurant Name
              </label>
              <input
                type="text"
                value={restaurantForm.name}
                onChange={(e) => setRestaurantForm({ ...restaurantForm, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter restaurant name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <textarea
                value={restaurantForm.address}
                onChange={(e) => setRestaurantForm({ ...restaurantForm, address: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter full address"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={restaurantForm.phone}
                onChange={(e) => setRestaurantForm({ ...restaurantForm, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter phone number"
              />
            </div>

            <Button
              onClick={handleRestaurantSave}
              className="w-full bg-blue-600 hover:bg-blue-700"
              isLoading={updateRestaurantMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Restaurant Settings
            </Button>
          </CardContent>
        </Card>

        {/* User Profile Settings */}
        <Card>
          <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50">
            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-purple-600" />
              <CardTitle className="text-lg">Manager Profile</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  value={userForm.first_name}
                  onChange={(e) => setUserForm({ ...userForm, first_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="First name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  value={userForm.last_name}
                  onChange={(e) => setUserForm({ ...userForm, last_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  placeholder="Last name"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={userForm.email}
                onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                placeholder="email@example.com"
              />
            </div>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-sm text-gray-600">
                <strong>Username:</strong> {user?.username}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Username cannot be changed
              </p>
            </div>

            <Button
              onClick={handleUserSave}
              className="w-full bg-purple-600 hover:bg-purple-700"
              isLoading={updateUserMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Profile Settings
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
