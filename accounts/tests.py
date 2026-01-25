from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from menu.models import Restaurant
from accounts.models import RestaurantUser


class RestaurantUserModelTest(TestCase):
    """Test RestaurantUser model"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant",
            address="123 Test St",
            phone="555-1234"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def test_create_restaurant_user(self):
        """Test creating a restaurant user"""
        restaurant_user = RestaurantUser.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            role='RESTAURANT_MANAGER',
            phone_number='555-5678'
        )
        self.assertEqual(restaurant_user.user.username, 'testuser')
        self.assertEqual(restaurant_user.role, 'RESTAURANT_MANAGER')
        self.assertTrue(restaurant_user.is_active)

    def test_restaurant_user_str(self):
        """Test string representation"""
        restaurant_user = RestaurantUser.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            role='KITCHEN_STAFF'
        )
        expected = f"{self.user.username} - KITCHEN_STAFF"
        self.assertEqual(str(restaurant_user), expected)


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant",
            address="123 Test St",
            phone="555-1234"
        )
        self.user = User.objects.create_user(
            username="manager",
            password="manager123",
            email="manager@test.com"
        )
        self.restaurant_user = RestaurantUser.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            role='RESTAURANT_MANAGER'
        )

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'manager',
            'password': 'manager123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'manager',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user(self):
        """Test getting current user info"""
        # Login first
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'manager',
            'password': 'manager123'
        })
        token = login_response.data['access']

        # Get current user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'manager')
        self.assertEqual(response.data['role'], 'RESTAURANT_MANAGER')


class PermissionsTest(APITestCase):
    """Test custom permissions"""

    def setUp(self):
        self.restaurant1 = Restaurant.objects.create(
            name="Restaurant 1",
            slug="restaurant-1"
        )
        self.restaurant2 = Restaurant.objects.create(
            name="Restaurant 2",
            slug="restaurant-2"
        )

        # Manager for restaurant 1
        self.manager_user = User.objects.create_user(
            username="manager1",
            password="pass123"
        )
        self.manager = RestaurantUser.objects.create(
            user=self.manager_user,
            restaurant=self.restaurant1,
            role='RESTAURANT_MANAGER'
        )

        # Kitchen staff for restaurant 1
        self.kitchen_user = User.objects.create_user(
            username="kitchen1",
            password="pass123"
        )
        self.kitchen = RestaurantUser.objects.create(
            user=self.kitchen_user,
            restaurant=self.restaurant1,
            role='KITCHEN_STAFF'
        )

    def test_manager_can_access_own_restaurant(self):
        """Test that manager can access their restaurant's data"""
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(f'/api/v1/manager/restaurants/{self.restaurant1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_kitchen_staff_cannot_manage_menu(self):
        """Test that kitchen staff cannot manage menu items"""
        self.client.force_authenticate(user=self.kitchen_user)
        response = self.client.post('/api/v1/manager/menu-items/', {
            'name': 'New Item',
            'price': '10.00'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
