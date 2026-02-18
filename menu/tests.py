from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from menu.models import Restaurant

# Create your tests here.

class IncrementViewMenuCountTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant",
            address="123 Test Street",
            view_menu_count=0
        )
        self.client = APIClient()

    def test_increment_view_menu_count_success(self):
        """Test that the view menu count increments successfully"""
        url = reverse('increment-view-count', kwargs={'restaurant_pk': self.restaurant.pk})
        
        # Initial count should be 0
        self.assertEqual(self.restaurant.view_menu_count, 0)
        
        # Make POST request to increment count
        response = self.client.post(url)
        
        # Check response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['view_menu_count'], 1)
        
        # Check database was updated
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.view_menu_count, 1)

    def test_increment_view_menu_count_multiple_times(self):
        """Test incrementing the count multiple times"""
        url = reverse('increment-view-count', kwargs={'restaurant_pk': self.restaurant.pk})
        
        # Increment 3 times
        for i in range(3):
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            expected_count = i + 1
            self.assertEqual(response.json()['view_menu_count'], expected_count)
        
        # Check final database state
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.view_menu_count, 3)

    def test_increment_view_menu_count_invalid_restaurant(self):
        """Test that invalid restaurant ID returns 404"""
        url = reverse('increment-view-count', kwargs={'restaurant_pk': 999})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Restaurant not found')
