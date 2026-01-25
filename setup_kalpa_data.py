"""
Setup Kalpa restaurant data to match the external API example.
This creates data similar to http://gipech.pythonanywhere.com/api/restaurants/1/

Usage:
    python setup_kalpa_data.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodapp_backend.settings')
django.setup()

from menu.models import Restaurant, MenuGroup, MenuCategory, MenuItem


def create_kalpa_data():
    """Create Kalpa restaurant data matching the external API."""
    print("Creating Kalpa restaurant data...")

    # 1. Create Restaurant
    print("\n1. Creating restaurant...")
    restaurant, created = Restaurant.objects.get_or_create(
        slug='kalpa',
        defaults={
            'name': "Kalpa",
            'address': "Birtamode-06",
            'phone': "9818181818",
            'is_active': True,
            'timezone': "Asia/Kathmandu",
        }
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Restaurant: {restaurant.name}")

    # 2. Create Menu Groups
    print("\n2. Creating menu groups...")

    # Food Group
    food_group, created = MenuGroup.objects.get_or_create(
        type='Food',
        restaurant=restaurant,
        defaults={'group_order': 0}
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Menu Group: {food_group.type}")

    # Drinks Group
    drinks_group, created = MenuGroup.objects.get_or_create(
        type='Drinks',
        restaurant=restaurant,
        defaults={'group_order': 1}
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Menu Group: {drinks_group.type}")

    # 3. Create Categories
    print("\n3. Creating categories...")

    # Starters Category (under Food)
    starters_category, created = MenuCategory.objects.get_or_create(
        name='Starters',
        menu_group=food_group,
        defaults={'cat_order': 0}
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Category: {starters_category.name} (in {food_group.type})")

    # Soft Drinks Category (under Drinks)
    soft_drinks_category, created = MenuCategory.objects.get_or_create(
        name='Soft Drinks',
        menu_group=drinks_group,
        defaults={'cat_order': 0}
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Category: {soft_drinks_category.name} (in {drinks_group.type})")

    # 4. Create Menu Items
    print("\n4. Creating menu items...")

    # Peanut sadheko
    peanut_item, created = MenuItem.objects.get_or_create(
        name='Peanut sadheko',
        category=starters_category,
        defaults={
            'price': '100.00',
            'description': 'Detailed flavor profile highlighting crispiness and seasoning',
            'item_order': 0,
            'is_available': True,
        }
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Item: {peanut_item.name} - Rs.{peanut_item.price}")

    # Coke
    coke_item, created = MenuItem.objects.get_or_create(
        name='Coke',
        category=soft_drinks_category,
        defaults={
            'price': '75.00',
            'description': 'Coca cola',
            'item_order': 0,
            'is_available': True,
        }
    )
    action = "Created" if created else "Found existing"
    print(f"   [{action}] Item: {coke_item.name} - Rs.{coke_item.price}")

    print("\n" + "="*60)
    print("Kalpa restaurant data setup complete!")
    print("="*60)
    print(f"\nYou can now access the API at:")
    print(f"  http://localhost:8000/api/restaurants/{restaurant.id}/")
    print(f"\nThis matches the format from:")
    print(f"  http://gipech.pythonanywhere.com/api/restaurants/1/")
    print("\n")


if __name__ == '__main__':
    create_kalpa_data()
