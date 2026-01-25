# Quick Start Guide

## Initial Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations (Already Done)
```bash
python manage.py migrate
```

### 3. Create a Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin user.

### 4. Start the Development Server
```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

---

## Setting Up Test Data

### Option 1: Using Django Admin

1. **Access Admin Panel**
   - Go to: `http://localhost:8000/admin/`
   - Login with your superuser credentials

2. **Create a Restaurant**
   - Go to "Restaurants"
   - Click "Add Restaurant"
   - Fill in:
     - Name: "Joe's Pizza"
     - Address: "123 Main St, New York, NY 10001"
     - Phone: "+1-555-0100"
     - Is active: ✓
     - Timezone: "America/New_York"
   - Save

3. **Create a Restaurant Manager User**
   - Go to "Restaurant Users"
   - Click "Add Restaurant User"
   - User: Select your superuser (or create a new User first)
   - Restaurant: Select "Joe's Pizza"
   - Role: "Restaurant Manager"
   - Phone: "+1-555-0101"
   - Is active: ✓
   - Save

4. **Create Menu Structure**

   **Menu Group:**
   - Go to "Menu Groups"
   - Add: Type="Lunch", Restaurant="Joe's Pizza", Group Order=1

   **Menu Category:**
   - Go to "Menu Categories"
   - Add: Name="Pizzas", Menu Group="Lunch (Joe's Pizza)", Cat Order=1

   **Menu Items:**
   - Go to "Menu Items"
   - Add multiple items:
     ```
     Name: Margherita Pizza
     Description: Classic tomato sauce and mozzarella
     Price: 12.99
     Category: Pizzas
     Is available: ✓
     Preparation time: 15
     ```

### Option 2: Using Python Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from menu.models import Restaurant, MenuGroup, MenuCategory, MenuItem
from accounts.models import RestaurantUser

# Create restaurant
restaurant = Restaurant.objects.create(
    name="Joe's Pizza",
    address="123 Main St, New York, NY 10001",
    phone="+1-555-0100",
    slug="joes-pizza",
    is_active=True,
    timezone="America/New_York"
)

# Create or get user
user = User.objects.get(username='admin')  # Use your superuser

# Create restaurant user
restaurant_user = RestaurantUser.objects.create(
    user=user,
    restaurant=restaurant,
    role='RESTAURANT_MANAGER',
    phone_number='+1-555-0101',
    is_active=True
)

# Create menu group
menu_group = MenuGroup.objects.create(
    type="Lunch",
    restaurant=restaurant,
    group_order=1
)

# Create category
category = MenuCategory.objects.create(
    name="Pizzas",
    menu_group=menu_group,
    cat_order=1
)

# Create menu items
items = [
    {
        "name": "Margherita Pizza",
        "description": "Classic tomato sauce and mozzarella",
        "price": 12.99,
        "preparation_time": 15
    },
    {
        "name": "Pepperoni Pizza",
        "description": "Tomato sauce, mozzarella, and pepperoni",
        "price": 14.99,
        "preparation_time": 15
    },
    {
        "name": "Vegetarian Pizza",
        "description": "Tomato sauce, mozzarella, peppers, onions, mushrooms",
        "price": 13.99,
        "preparation_time": 15,
        "dietary_tags": ["vegetarian"]
    }
]

for item_data in items:
    MenuItem.objects.create(
        category=category,
        is_available=True,
        **item_data
    )

print("Test data created successfully!")
```

---

## Testing the API

### 1. Login to Get JWT Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "restaurant": {
      "id": 1,
      "name": "Joe's Pizza",
      "slug": "joes-pizza"
    },
    "role": "RESTAURANT_MANAGER"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Save the access token** for subsequent requests!

### 2. Test Manager API - List Menu Items

```bash
curl -X GET http://localhost:8000/api/v1/manager/menu-items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Test Manager API - Create Menu Item

```bash
curl -X POST http://localhost:8000/api/v1/manager/menu-items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hawaiian Pizza",
    "description": "Ham and pineapple",
    "price": 13.99,
    "category": 1,
    "is_available": true,
    "preparation_time": 15
  }'
```

### 4. Test Manager API - Toggle Item Availability

```bash
curl -X PATCH http://localhost:8000/api/v1/manager/menu-items/1/toggle_availability/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Get Current User Profile

```bash
curl -X GET http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Using Swagger UI (Recommended for Testing)

1. Go to: `http://localhost:8000/api/docs/`

2. Click "Authorize" button

3. Enter: `Bearer YOUR_ACCESS_TOKEN`

4. Now you can test all endpoints interactively!

---

## Creating Tables for QR Codes

```bash
python manage.py shell
```

```python
from menu.models import Restaurant
from orders.models import Table

restaurant = Restaurant.objects.get(slug='joes-pizza')

# Create tables
tables = []
for i in range(1, 11):  # Create 10 tables
    table = Table.objects.create(
        restaurant=restaurant,
        table_number=f"Table {i}",
        capacity=4,
        is_active=True
    )
    tables.append(table)
    print(f"Created {table.table_number} with QR code: {table.qr_code}")
```

The QR codes are automatically generated!

---

## Common Issues

### Issue: "No module named 'dotenv'"
**Solution:** Install python-dotenv
```bash
pip install python-dotenv
```

### Issue: JWT token errors
**Solution:** Check that you're including the Bearer prefix
```
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
```

### Issue: Permission denied errors
**Solution:** Ensure your user has a RestaurantUser profile with appropriate role

### Issue: CORS errors (when testing with frontend)
**Solution:** Check `.env` file has correct CORS_ALLOWED_ORIGINS

---

## Next Steps After Setup

1. ✅ Create test restaurant
2. ✅ Create restaurant manager user
3. ✅ Create menu structure
4. ✅ Test authentication
5. ✅ Test manager API
6. Continue implementation:
   - Customer order API
   - Kitchen display API
   - QR code generation
   - Frontend applications

---

## Useful Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Open Django shell
python manage.py shell

# Run tests (when we create them)
python manage.py test

# Or with pytest
pytest
```

---

## API Endpoint Summary

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/refresh/` - Refresh token
- `GET /api/v1/auth/me/` - Current user

### Manager API
- `/api/v1/manager/restaurant/` - Restaurant settings
- `/api/v1/manager/menu-groups/` - Menu groups CRUD
- `/api/v1/manager/categories/` - Categories CRUD
- `/api/v1/manager/menu-items/` - Menu items CRUD

### Documentation
- `/api/schema/` - OpenAPI schema
- `/api/docs/` - Swagger UI

---

Happy testing! 🚀
