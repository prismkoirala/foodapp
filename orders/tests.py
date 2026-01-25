from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from menu.models import Restaurant, MenuCategory, MenuItem
from orders.models import Table, Order, OrderItem
from accounts.models import RestaurantUser


class TableModelTest(TestCase):
    """Test Table model"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant"
        )

    def test_create_table(self):
        """Test creating a table"""
        table = Table.objects.create(
            restaurant=self.restaurant,
            table_number="Table 1"
        )
        self.assertIsNotNone(table.qr_code)
        self.assertEqual(table.table_number, "Table 1")

    def test_qr_code_auto_generation(self):
        """Test that QR code is auto-generated"""
        table = Table.objects.create(
            restaurant=self.restaurant,
            table_number="Table 2"
        )
        self.assertTrue(len(table.qr_code) > 10)

    def test_table_str(self):
        """Test string representation"""
        table = Table.objects.create(
            restaurant=self.restaurant,
            table_number="Table 3"
        )
        expected = f"{self.restaurant.name} - Table 3"
        self.assertEqual(str(table), expected)


class OrderModelTest(TestCase):
    """Test Order model"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant"
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            table_number="Table 1"
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name="Test Category"
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Test Item",
            description="Test Description",
            price="10.00"
        )

    def test_create_order(self):
        """Test creating an order"""
        order = Order.objects.create(
            restaurant=self.restaurant,
            table=self.table,
            customer_name="John Doe",
            customer_phone="555-1234"
        )
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.status, 'PENDING')
        self.assertIsNotNone(order.created_at)

    def test_order_number_generation(self):
        """Test that order number is auto-generated"""
        order = Order.objects.create(
            restaurant=self.restaurant,
            customer_name="Jane Doe",
            customer_phone="555-5678"
        )
        self.assertTrue(order.order_number.startswith('ORD'))

    def test_calculate_total(self):
        """Test order total calculation"""
        order = Order.objects.create(
            restaurant=self.restaurant,
            customer_name="Test User",
            customer_phone="555-0000"
        )

        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=2,
            unit_price=self.menu_item.price
        )

        self.assertEqual(order.total_amount, Decimal('20.00'))


class CustomerOrderAPITest(APITestCase):
    """Test customer order creation API"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant"
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            table_number="Table 1"
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name="Main Course"
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Burger",
            description="Delicious burger",
            price="12.50",
            is_available=True
        )

    def test_resolve_qr_code(self):
        """Test QR code resolution"""
        response = self.client.get(f'/api/v1/customer/qr/{self.table.qr_code}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['restaurant_slug'], 'test-restaurant')
        self.assertEqual(response.data['table_id'], self.table.id)

    def test_resolve_invalid_qr_code(self):
        """Test QR code resolution with invalid code"""
        response = self.client.get('/api/v1/customer/qr/invalid-code/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order(self):
        """Test creating an order"""
        order_data = {
            'restaurant': 'test-restaurant',
            'table_id': self.table.id,
            'customer_name': 'John Doe',
            'customer_phone': '555-1234',
            'items': [
                {
                    'menu_item_id': self.menu_item.id,
                    'quantity': 2,
                    'special_instructions': 'No onions'
                }
            ]
        }

        response = self.client.post('/api/v1/customer/orders/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)
        self.assertEqual(response.data['customer_name'], 'John Doe')
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['total_amount'], '25.00')

    def test_create_order_without_items(self):
        """Test creating an order without items"""
        order_data = {
            'restaurant': 'test-restaurant',
            'customer_name': 'John Doe',
            'customer_phone': '555-1234',
            'items': []
        }

        response = self.client.post('/api/v1/customer/orders/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_status(self):
        """Test getting order status"""
        # Create an order first
        order = Order.objects.create(
            restaurant=self.restaurant,
            table=self.table,
            customer_name='Test User',
            customer_phone='555-9999'
        )

        response = self.client.get(f'/api/v1/customer/orders/{order.order_number}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_number'], order.order_number)
        self.assertEqual(response.data['status'], 'PENDING')


class KitchenOrderAPITest(APITestCase):
    """Test kitchen order management API"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant"
        )
        self.user = User.objects.create_user(
            username="kitchen",
            password="kitchen123"
        )
        self.restaurant_user = RestaurantUser.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            role='KITCHEN_STAFF'
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name="Main"
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Pizza",
            price="15.00"
        )
        self.order = Order.objects.create(
            restaurant=self.restaurant,
            customer_name="Customer",
            customer_phone="555-0000",
            status='PENDING'
        )
        OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=1,
            unit_price=self.menu_item.price
        )

    def test_get_orders_by_status(self):
        """Test getting orders grouped by status"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/kitchen/orders/by_status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('PENDING', response.data)
        self.assertIn('CONFIRMED', response.data)
        self.assertIn('PREPARING', response.data)
        self.assertIn('READY', response.data)
        self.assertEqual(len(response.data['PENDING']), 1)

    def test_update_order_status(self):
        """Test updating order status"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/v1/kitchen/orders/{self.order.id}/',
            {'status': 'CONFIRMED'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CONFIRMED')

        # Verify timestamp was set
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.confirmed_at)

    def test_invalid_status_transition(self):
        """Test invalid status transition"""
        self.client.force_authenticate(user=self.user)

        # Try to jump from PENDING to READY (should fail)
        response = self.client.patch(
            f'/api/v1/kitchen/orders/{self.order.id}/',
            {'status': 'READY'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_access_kitchen(self):
        """Test that unauthenticated users cannot access kitchen API"""
        response = self.client.get('/api/v1/kitchen/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ManagerOrderAPITest(APITestCase):
    """Test manager order management API"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            slug="test-restaurant"
        )
        self.user = User.objects.create_user(
            username="manager",
            password="manager123"
        )
        self.restaurant_user = RestaurantUser.objects.create(
            user=self.user,
            restaurant=self.restaurant,
            role='RESTAURANT_MANAGER'
        )
        self.category = MenuCategory.objects.create(
            restaurant=self.restaurant,
            name="Drinks"
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Coke",
            price="2.50"
        )

    def test_create_table(self):
        """Test creating a table"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/v1/manager/tables/',
            {'table_number': 'Table 5'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['qr_code'])

    def test_regenerate_qr_code(self):
        """Test regenerating QR code for a table"""
        table = Table.objects.create(
            restaurant=self.restaurant,
            table_number="Table 1"
        )
        old_qr = table.qr_code

        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/v1/manager/tables/{table.id}/regenerate_qr/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['qr_code'], old_qr)

    def test_get_order_statistics(self):
        """Test getting order statistics"""
        # Create some orders
        Order.objects.create(
            restaurant=self.restaurant,
            customer_name="Customer 1",
            customer_phone="555-0001",
            status='PENDING'
        )
        Order.objects.create(
            restaurant=self.restaurant,
            customer_name="Customer 2",
            customer_phone="555-0002",
            status='COMPLETED'
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/manager/orders/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_orders', response.data)
        self.assertIn('active_orders', response.data)
        self.assertEqual(response.data['total_orders'], 2)
