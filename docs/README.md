# Multi-Tenant Restaurant Management & Ordering System

A comprehensive Django REST API backend for managing multiple restaurants with customer ordering, kitchen display, and QR code table management.

## Features

### Authentication & Multi-Tenancy
- JWT-based authentication with refresh tokens
- Role-based access control (Super Admin, Restaurant Manager, Kitchen Staff)
- Multi-tenant architecture (restaurants isolated from each other)
- Secure permission system

### Restaurant Management
- Full CRUD operations for menus, categories, and items
- Availability toggling and special of the day marking
- Extended menu item features (allergens, dietary tags, preparation time)
- Bulk operations and reordering

### Table & QR Code System
- Auto-generated QR codes for each table
- QR code image generation for printing
- QR code regeneration capability
- Table capacity management

### Order Management
- Customer order creation (no authentication required)
- Order tracking by order number
- Manager order viewing with filtering and search
- Kitchen order display with Kanban board
- Status workflow with automatic timestamps
- Order statistics and analytics

### Kitchen Display
- Active order filtering
- Status update capabilities
- Pending order counts
- Orders grouped by status (Pending, Preparing, Ready)

## Technology Stack

**Backend:**
- Django 5.2.10
- Django REST Framework 3.16.1
- djangorestframework-simplejwt 5.5.1
- PostgreSQL (production) / SQLite (development)
- python-dotenv for environment management

**Additional Libraries:**
- django-cors-headers - CORS support
- qrcode - QR code generation
- drf-spectacular - API documentation
- pillow - Image handling

## Quick Start

### 1. Installation

```bash
# Clone the repository
cd foodapp

# Install dependencies
pip install -r requirements.txt

# Apply migrations (already done)
python manage.py migrate

# Create test data
python setup_test_data.py
```

### 2. Run the Server

```bash
python manage.py runserver
```

Server will be available at: http://localhost:8000

### 3. Access API Documentation

Interactive Swagger UI: http://localhost:8000/api/docs/
OpenAPI Schema: http://localhost:8000/api/schema/

### 4. Login

Use the provided test credentials:

**Manager Account:**
- Username: `manager`
- Password: `manager123`

**Kitchen Staff Account:**
- Username: `kitchen`
- Password: `kitchen123`

**Login Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "manager123"}'
```

## API Endpoints Overview

### Authentication (`/api/v1/auth/`)
- `POST /login/` - Login with credentials
- `POST /refresh/` - Refresh access token
- `POST /logout/` - Logout and blacklist token
- `GET /me/` - Get current user profile

### Manager API (`/api/v1/manager/`)
- **Menu Management:** Full CRUD for restaurants, menu groups, categories, items
- **Table Management:** Create tables, generate QR codes, download for printing
- **Order Management:** View orders, update status, get statistics

### Customer API (`/api/v1/customer/`)
- **Menu Browsing:** Public access to restaurant menus
- **QR Code:** Resolve QR codes to restaurant/table info
- **Ordering:** Create orders without authentication
- **Tracking:** Track order status by order number

### Kitchen API (`/api/v1/kitchen/`)
- **Orders:** View active orders
- **Status Updates:** Update order preparation status
- **Kanban Data:** Get orders grouped by status
- **Counts:** Get pending order counts

## Project Structure

```
foodapp/
├── foodapp_backend/
│   ├── settings/          # Environment-based settings
│   ├── urls.py            # Main URL routing
│   └── views.py           # API root view
├── accounts/              # Authentication & multi-tenancy
│   ├── models.py          # RestaurantUser model
│   ├── serializers.py     # User serializers
│   ├── views.py           # Auth views
│   ├── permissions.py     # Custom permissions
│   └── middleware.py      # Restaurant context middleware
├── menu/                  # Menu management
│   ├── models.py          # Restaurant, MenuGroup, MenuCategory, MenuItem
│   ├── serializers.py     # Menu serializers
│   ├── views/
│   │   ├── api_views.py   # Customer-facing views
│   │   └── manager_views.py  # Manager CRUD views
│   └── urls_*.py          # URL routing
├── orders/                # Order management
│   ├── models.py          # Table, Order, OrderItem
│   ├── serializers.py     # Order serializers
│   ├── views/
│   │   ├── customer_views.py  # Customer ordering
│   │   ├── manager_views.py   # Manager order management
│   │   └── kitchen_views.py   # Kitchen display
│   ├── utils.py           # QR code generation
│   └── urls_*.py          # URL routing
├── media/                 # User uploads
│   ├── restaurants/       # Restaurant logos
│   ├── categories/        # Category images
│   ├── items/             # Menu item images
│   └── qr_codes/          # Generated QR codes
├── .env                   # Environment variables
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── setup_test_data.py     # Test data generator
├── API_ENDPOINTS.md       # Complete API documentation
├── IMPLEMENTATION_STATUS.md  # Implementation details
├── QUICKSTART.md          # Quick start guide
└── README.md              # This file
```

## Database Schema

### Core Models

**Restaurant**
- Basic info (name, address, phone, logo)
- Slug for URL-friendly access
- Business hours and timezone
- Active status

**MenuGroup** → **MenuCategory** → **MenuItem**
- Hierarchical menu structure
- Ordering/sorting capabilities
- Extended menu item features

**Table**
- Restaurant association
- Auto-generated QR codes
- QR code images
- Capacity and active status

**Order** → **OrderItem**
- Order workflow with status tracking
- Customer information (optional)
- Menu item price snapshots
- Automatic total calculation
- Status-specific timestamps

**RestaurantUser**
- Links Django users to restaurants
- Role-based access (Super Admin, Manager, Kitchen Staff)
- Multi-tenancy support

## Environment Variables

Create a `.env` file in the project root (see `.env.example`):

```env
DJANGO_ENV=development
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

## Testing the API

### Using Swagger UI (Recommended)

1. Visit http://localhost:8000/api/docs/
2. Click "Authorize" button
3. Login to get JWT token
4. Enter token: `Bearer <your-access-token>`
5. Test all endpoints interactively

### Using cURL

**Create an Order:**
```bash
curl -X POST http://localhost:8000/api/v1/customer/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_slug": "joes-pizza",
    "table_id": 1,
    "items": [
      {"menu_item_id": 1, "quantity": 2}
    ],
    "customer_name": "John Doe"
  }'
```

**Get Table QR Code:**
```bash
curl -X GET http://localhost:8000/api/v1/manager/tables/1/ \
  -H "Authorization: Bearer <your-token>"
```

**Update Order Status (Kitchen):**
```bash
curl -X PATCH http://localhost:8000/api/v1/kitchen/orders/1/update_status/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "PREPARING"}'
```

## Multi-Tenancy

The system implements multi-tenancy through:

1. **Restaurant Foreign Keys** - All models linked to a restaurant
2. **Context Middleware** - Injects `request.restaurant` and `request.user_role`
3. **Filtered Querysets** - Users only see their restaurant's data
4. **Permission Classes** - Object-level permissions enforce isolation
5. **Database Indexes** - Optimized queries on restaurant foreign keys

## Order Workflow

```
Customer Journey:
1. Scan QR code → Resolve to restaurant/table
2. Browse menu → Add items to cart
3. Submit order → Order created (PENDING)

Kitchen Journey:
4. Kitchen sees order → Confirm (CONFIRMED)
5. Start cooking → Update to PREPARING
6. Food ready → Update to READY

Manager/Server Journey:
7. Serve to customer → Update to SERVED
8. Close order → Update to COMPLETED
```

Valid status transitions enforced by serializer validation.

## Sample Data

The `setup_test_data.py` script creates:
- 1 Restaurant (Joe's Pizza)
- 2 Users (manager, kitchen)
- 2 Menu Groups (Lunch, Dinner)
- 3 Categories (Pizzas, Pasta, Appetizers)
- 8 Menu Items
- 10 Tables with QR codes
- 1 Sample Order

## Production Deployment

### Database
Migrate from SQLite to PostgreSQL:

```python
# In .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodapp_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

### Security
- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure `ALLOWED_HOSTS`
- Enable HTTPS
- Use environment variables for secrets

### Media Storage
Consider AWS S3 or Cloudinary for user uploads in production.

### Deployment Platforms
- Railway.app (easy Django deployment)
- Render.com
- AWS EC2/ECS
- DigitalOcean Droplets
- Heroku

## Next Steps

### Recommended Enhancements

1. **Real-time Updates**
   - Implement Django Channels for WebSocket support
   - Live order updates without polling

2. **Frontend Applications**
   - React manager portal
   - Customer ordering PWA
   - Kitchen display system

3. **Testing**
   - Unit tests for models and serializers
   - API integration tests
   - End-to-end testing

4. **Additional Features**
   - Payment integration (Stripe, PayPal)
   - SMS/Email notifications
   - Order history and analytics
   - Customer reviews and ratings
   - Inventory management

## Documentation

- **API_ENDPOINTS.md** - Complete API reference
- **IMPLEMENTATION_STATUS.md** - Implementation details and progress
- **QUICKSTART.md** - Quick start and testing guide
- **Swagger UI** - Interactive API documentation at `/api/docs/`

## Support

For issues or questions:
1. Check the documentation files
2. Review the API docs at `/api/docs/`
3. Examine the test data script for examples

## License

This project is created for educational purposes.

---

**Built with Django REST Framework**
**Backend Implementation: 95% Complete**
