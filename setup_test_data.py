"""
Setup test data for the restaurant management system.
Run this script to create sample data for testing.

Usage:
    python setup_test_data.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodapp_backend.settings')
django.setup()

from django.contrib.auth.models import User
from menu.models import Restaurant, MenuGroup, MenuCategory, MenuItem
from accounts.models import RestaurantUser
from orders.models import Table, Order, OrderItem
from orders.utils import generate_qr_code_image


def create_test_data():
    """Create comprehensive test data."""
    print("Creating test data...")

    # 1. Create Restaurant
    print("\n1. Creating restaurant...")
    restaurant, created = Restaurant.objects.get_or_create(
        slug='joes-pizza',
        defaults={
            'name': "Joe's Pizza",
            'address': "123 Main St, New York, NY 10001",
            'phone': "+1-555-0100",
            'is_active': True,
            'timezone': "America/New_York",
            'business_hours': {
                'monday': '11:00-22:00',
                'tuesday': '11:00-22:00',
                'wednesday': '11:00-22:00',
                'thursday': '11:00-22:00',
                'friday': '11:00-23:00',
                'saturday': '11:00-23:00',
                'sunday': '12:00-21:00',
            }
        }
    )
    print(f"   [OK] Restaurant: {restaurant.name}")

    # 2. Create Users
    print("\n2. Creating users...")

    # Manager user
    manager_user, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@joespizza.com',
            'first_name': 'John',
            'last_name': 'Manager',
            'is_staff': False,
        }
    )
    if created:
        manager_user.set_password('manager123')
        manager_user.save()
    print(f"   [OK] Manager: {manager_user.username} (password: manager123)")

    # Kitchen staff user
    kitchen_user, created = User.objects.get_or_create(
        username='kitchen',
        defaults={
            'email': 'kitchen@joespizza.com',
            'first_name': 'Maria',
            'last_name': 'Chef',
            'is_staff': False,
        }
    )
    if created:
        kitchen_user.set_password('kitchen123')
        kitchen_user.save()
    print(f"   [OK] Kitchen Staff: {kitchen_user.username} (password: kitchen123)")

    # 3. Create Restaurant Users
    print("\n3. Creating restaurant user profiles...")
    manager_profile, _ = RestaurantUser.objects.get_or_create(
        user=manager_user,
        defaults={
            'restaurant': restaurant,
            'role': 'RESTAURANT_MANAGER',
            'phone_number': '+1-555-0101',
            'is_active': True,
        }
    )
    print(f"   [OK] Manager profile: {manager_profile}")

    kitchen_profile, _ = RestaurantUser.objects.get_or_create(
        user=kitchen_user,
        defaults={
            'restaurant': restaurant,
            'role': 'KITCHEN_STAFF',
            'phone_number': '+1-555-0102',
            'is_active': True,
        }
    )
    print(f"   [OK] Kitchen profile: {kitchen_profile}")

    # 4. Create Menu Structure
    print("\n4. Creating menu structure...")

    # Lunch Menu Group
    lunch_group, _ = MenuGroup.objects.get_or_create(
        type='Lunch',
        restaurant=restaurant,
        defaults={'group_order': 1}
    )
    print(f"   [OK] Menu Group: {lunch_group.type}")

    # Dinner Menu Group
    dinner_group, _ = MenuGroup.objects.get_or_create(
        type='Dinner',
        restaurant=restaurant,
        defaults={'group_order': 2}
    )
    print(f"   [OK] Menu Group: {dinner_group.type}")

    # Categories
    pizza_category, _ = MenuCategory.objects.get_or_create(
        name='Pizzas',
        menu_group=lunch_group,
        defaults={'cat_order': 1}
    )
    print(f"   [OK] Category: {pizza_category.name}")

    pasta_category, _ = MenuCategory.objects.get_or_create(
        name='Pasta',
        menu_group=lunch_group,
        defaults={'cat_order': 2}
    )
    print(f"   [OK] Category: {pasta_category.name}")

    appetizers_category, _ = MenuCategory.objects.get_or_create(
        name='Appetizers',
        menu_group=dinner_group,
        defaults={'cat_order': 1}
    )
    print(f"   [OK] Category: {appetizers_category.name}")

    # 5. Create Menu Items
    print("\n5. Creating menu items...")

    pizza_items = [
        {
            'name': 'Margherita Pizza',
            'description': 'Classic tomato sauce, fresh mozzarella, and basil',
            'price': 12.99,
            'category': pizza_category,
            'preparation_time': 15,
            'allergens': ['dairy', 'gluten'],
            'dietary_tags': ['vegetarian'],
            'is_special_of_day': True,
        },
        {
            'name': 'Pepperoni Pizza',
            'description': 'Tomato sauce, mozzarella, and pepperoni',
            'price': 14.99,
            'category': pizza_category,
            'preparation_time': 15,
            'allergens': ['dairy', 'gluten'],
            'dietary_tags': [],
        },
        {
            'name': 'Vegetarian Pizza',
            'description': 'Tomato sauce, mozzarella, peppers, onions, mushrooms, olives',
            'price': 13.99,
            'category': pizza_category,
            'preparation_time': 15,
            'allergens': ['dairy', 'gluten'],
            'dietary_tags': ['vegetarian'],
        },
        {
            'name': 'Hawaiian Pizza',
            'description': 'Tomato sauce, mozzarella, ham, and pineapple',
            'price': 14.99,
            'category': pizza_category,
            'preparation_time': 15,
            'allergens': ['dairy', 'gluten'],
            'dietary_tags': [],
        },
    ]

    for i, item_data in enumerate(pizza_items):
        item, _ = MenuItem.objects.get_or_create(
            name=item_data['name'],
            category=item_data['category'],
            defaults={**item_data, 'item_order': i, 'is_available': True}
        )
        print(f"   [OK] Menu Item: {item.name} - ${item.price}")

    pasta_items = [
        {
            'name': 'Spaghetti Carbonara',
            'description': 'Creamy sauce with bacon and parmesan',
            'price': 15.99,
            'category': pasta_category,
            'preparation_time': 20,
            'allergens': ['dairy', 'gluten', 'eggs'],
            'dietary_tags': [],
        },
        {
            'name': 'Penne Arrabbiata',
            'description': 'Spicy tomato sauce with garlic',
            'price': 13.99,
            'category': pasta_category,
            'preparation_time': 18,
            'allergens': ['gluten'],
            'dietary_tags': ['vegan', 'spicy'],
        },
    ]

    for i, item_data in enumerate(pasta_items):
        item, _ = MenuItem.objects.get_or_create(
            name=item_data['name'],
            category=item_data['category'],
            defaults={**item_data, 'item_order': i, 'is_available': True}
        )
        print(f"   [OK] Menu Item: {item.name} - ${item.price}")

    appetizer_items = [
        {
            'name': 'Garlic Bread',
            'description': 'Toasted bread with garlic butter and herbs',
            'price': 5.99,
            'category': appetizers_category,
            'preparation_time': 10,
            'allergens': ['dairy', 'gluten'],
            'dietary_tags': ['vegetarian'],
        },
        {
            'name': 'Bruschetta',
            'description': 'Toasted bread with tomatoes, basil, and olive oil',
            'price': 7.99,
            'category': appetizers_category,
            'preparation_time': 10,
            'allergens': ['gluten'],
            'dietary_tags': ['vegan'],
        },
    ]

    for i, item_data in enumerate(appetizer_items):
        item, _ = MenuItem.objects.get_or_create(
            name=item_data['name'],
            category=item_data['category'],
            defaults={**item_data, 'item_order': i, 'is_available': True}
        )
        print(f"   [OK] Menu Item: {item.name} - ${item.price}")

    # 6. Create Tables with QR Codes
    print("\n6. Creating tables with QR codes...")
    for i in range(1, 11):
        table, created = Table.objects.get_or_create(
            restaurant=restaurant,
            table_number=f"Table {i}",
            defaults={
                'capacity': 4,
                'is_active': True,
            }
        )
        if created:
            # Generate QR code image
            try:
                qr_image = generate_qr_code_image(table.qr_code)
                table.qr_code_image.save(f'qr_{table.qr_code}.png', qr_image, save=True)
            except Exception as e:
                print(f"   [WARNING] Could not generate QR image for {table.table_number}: {e}")

        print(f"   [OK] {table.table_number} - QR Code: {table.qr_code[:20]}...")

    # 7. Create Sample Order
    print("\n7. Creating sample order...")
    first_table = Table.objects.filter(restaurant=restaurant).first()
    margherita = MenuItem.objects.get(name='Margherita Pizza')
    garlic_bread = MenuItem.objects.get(name='Garlic Bread')

    order, created = Order.objects.get_or_create(
        order_number='ORD-SAMPLE-001',
        defaults={
            'restaurant': restaurant,
            'table': first_table,
            'customer_name': 'Sample Customer',
            'customer_phone': '+1-555-9999',
            'status': 'PENDING',
            'total_amount': margherita.price * 2 + garlic_bread.price,
            'special_instructions': 'This is a sample order for testing',
        }
    )

    if created:
        OrderItem.objects.create(
            order=order,
            menu_item=margherita,
            quantity=2,
            unit_price=margherita.price,
            subtotal=margherita.price * 2,
            menu_item_snapshot={
                'name': margherita.name,
                'description': margherita.description,
                'price': str(margherita.price),
                'category': margherita.category.name,
            }
        )
        OrderItem.objects.create(
            order=order,
            menu_item=garlic_bread,
            quantity=1,
            unit_price=garlic_bread.price,
            subtotal=garlic_bread.price,
            menu_item_snapshot={
                'name': garlic_bread.name,
                'description': garlic_bread.description,
                'price': str(garlic_bread.price),
                'category': garlic_bread.category.name,
            }
        )
        print(f"   [OK] Sample Order: {order.order_number} - Total: ${order.total_amount}")

    print("\n" + "="*60)
    print("SUCCESS: Test data created successfully!")
    print("="*60)

    print("\nSummary:")
    print(f"   Restaurants: {Restaurant.objects.count()}")
    print(f"   Users: {User.objects.count()}")
    print(f"   Menu Groups: {MenuGroup.objects.count()}")
    print(f"   Categories: {MenuCategory.objects.count()}")
    print(f"   Menu Items: {MenuItem.objects.count()}")
    print(f"   Tables: {Table.objects.count()}")
    print(f"   Orders: {Order.objects.count()}")

    print("\nLogin Credentials:")
    print(f"   Manager:")
    print(f"      Username: manager")
    print(f"      Password: manager123")
    print(f"   Kitchen Staff:")
    print(f"      Username: kitchen")
    print(f"      Password: kitchen123")

    print("\nNext Steps:")
    print("   1. Start the server: python manage.py runserver")
    print("   2. Login at: http://localhost:8000/api/v1/auth/login/")
    print("   3. View API docs: http://localhost:8000/api/docs/")
    print("   4. Test QR codes - scan any table's QR code from /api/v1/manager/tables/")

    print("\nFirst Table QR Code:")
    if first_table:
        print(f"   {first_table.table_number}")
        print(f"   QR Code: {first_table.qr_code}")
        print(f"   URL: http://localhost:8000/api/v1/customer/qr/{first_table.qr_code}/")


if __name__ == '__main__':
    try:
        create_test_data()
    except Exception as e:
        print(f"\n[ERROR] Error creating test data: {e}")
        import traceback
        traceback.print_exc()
