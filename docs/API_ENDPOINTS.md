# API Endpoints Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

---

## Authentication Endpoints

### POST /api/v1/auth/login/
Login and receive JWT tokens.

**Request:**
```json
{
  "username": "manager",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "manager",
    "email": "manager@example.com",
    "restaurant": {
      "id": 1,
      "name": "Joe's Pizza",
      "slug": "joes-pizza"
    },
    "role": "RESTAURANT_MANAGER"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1Qi...",
    "access": "eyJ0eXAiOiJKV1Qi..."
  }
}
```

### POST /api/v1/auth/refresh/
Refresh access token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1Qi..."
}
```

### POST /api/v1/auth/logout/
Logout and blacklist refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1Qi..."
}
```

**Headers:** `Authorization: Bearer <access_token>`

### GET /api/v1/auth/me/
Get current user profile.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": 1,
  "username": "manager",
  "email": "manager@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "restaurant": {
    "id": 1,
    "name": "Joe's Pizza",
    "slug": "joes-pizza"
  },
  "role": "RESTAURANT_MANAGER",
  "phone_number": "+1-555-0100"
}
```

---

## Manager API - Menu Management

**All endpoints require authentication with Manager role.**

**Headers:** `Authorization: Bearer <access_token>`

### Restaurant

**GET /api/v1/manager/restaurant/**
Get restaurant details (managers see their own restaurant).

**PATCH /api/v1/manager/restaurant/{id}/**
Update restaurant settings.

### Menu Groups

**GET /api/v1/manager/menu-groups/**
List all menu groups.

**POST /api/v1/manager/menu-groups/**
Create a new menu group.

**Request:**
```json
{
  "type": "Dinner",
  "restaurant": 1,
  "group_order": 2
}
```

**GET /api/v1/manager/menu-groups/{id}/**
Get menu group details.

**PUT /api/v1/manager/menu-groups/{id}/**
Update menu group.

**DELETE /api/v1/manager/menu-groups/{id}/**
Delete menu group.

### Categories

**GET /api/v1/manager/categories/**
List all categories.

Query parameters:
- `menu_group` - Filter by menu group ID
- `search` - Search by name

**POST /api/v1/manager/categories/**
Create a new category.

**Request:**
```json
{
  "name": "Appetizers",
  "menu_group": 1,
  "cat_order": 1
}
```

**GET /api/v1/manager/categories/{id}/**
Get category details.

**PUT /api/v1/manager/categories/{id}/**
Update category.

**DELETE /api/v1/manager/categories/{id}/**
Delete category.

### Menu Items

**GET /api/v1/manager/menu-items/**
List all menu items.

Query parameters:
- `category` - Filter by category ID
- `is_available` - Filter by availability (true/false)
- `is_special_of_day` - Filter specials (true/false)
- `search` - Search by name or description
- `ordering` - Sort by field (item_order, name, price, created_at)

**POST /api/v1/manager/menu-items/**
Create a new menu item.

**Request:**
```json
{
  "name": "Margherita Pizza",
  "description": "Classic tomato sauce and mozzarella",
  "price": "12.99",
  "category": 1,
  "is_available": true,
  "is_special_of_day": false,
  "preparation_time": 15,
  "allergens": ["dairy", "gluten"],
  "dietary_tags": ["vegetarian"],
  "item_order": 1
}
```

**GET /api/v1/manager/menu-items/{id}/**
Get menu item details.

**PUT /api/v1/manager/menu-items/{id}/**
Update menu item.

**PATCH /api/v1/manager/menu-items/{id}/**
Partial update.

**DELETE /api/v1/manager/menu-items/{id}/**
Delete menu item.

**PATCH /api/v1/manager/menu-items/{id}/toggle_availability/**
Toggle item availability.

**PATCH /api/v1/manager/menu-items/{id}/set_special/**
Set/unset as special of the day.

**Request:**
```json
{
  "is_special": true
}
```

**POST /api/v1/manager/menu-items/reorder/**
Bulk reorder items.

**Request:**
```json
[
  {"item_id": 1, "new_order": 0},
  {"item_id": 2, "new_order": 1},
  {"item_id": 3, "new_order": 2}
]
```

---

## Manager API - Table & QR Code Management

**Headers:** `Authorization: Bearer <access_token>`

### Tables

**GET /api/v1/manager/tables/**
List all tables.

Query parameters:
- `is_active` - Filter by active status
- `search` - Search by table number or QR code

**POST /api/v1/manager/tables/**
Create a new table (QR code auto-generated).

**Request:**
```json
{
  "table_number": "Table 5",
  "capacity": 4,
  "is_active": true
}
```

**Response:**
```json
{
  "id": 5,
  "restaurant": 1,
  "restaurant_name": "Joe's Pizza",
  "table_number": "Table 5",
  "qr_code": "abc123xyz...",
  "qr_code_image": "/media/qr_codes/qr_abc123xyz.png",
  "qr_code_url": "http://localhost:8000/api/v1/customer/qr/abc123xyz/",
  "is_active": true,
  "capacity": 4,
  "created_at": "2024-01-25T10:00:00Z"
}
```

**GET /api/v1/manager/tables/{id}/**
Get table details.

**PUT /api/v1/manager/tables/{id}/**
Update table.

**DELETE /api/v1/manager/tables/{id}/**
Delete table.

**POST /api/v1/manager/tables/{id}/regenerate_qr/**
Regenerate QR code for a table (invalidates old QR code).

**GET /api/v1/manager/tables/{id}/qr_code_download/**
Get QR code details for download/printing.

**Response:**
```json
{
  "qr_code": "abc123xyz",
  "qr_code_image_url": "http://localhost:8000/media/qr_codes/qr_abc123xyz.png",
  "table_number": "Table 5",
  "restaurant": "Joe's Pizza"
}
```

---

## Manager API - Order Management

**Headers:** `Authorization: Bearer <access_token>`

### Orders

**GET /api/v1/manager/orders/**
List all orders.

Query parameters:
- `status` - Filter by status (PENDING, CONFIRMED, PREPARING, READY, SERVED, COMPLETED, CANCELLED)
- `table` - Filter by table ID
- `date_from` - Filter from date (YYYY-MM-DD)
- `date_to` - Filter to date (YYYY-MM-DD)
- `search` - Search by order number, customer name, or phone
- `ordering` - Sort by field (created_at, total_amount, status)

**GET /api/v1/manager/orders/{id}/**
Get order details.

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-20240125-A3F9",
  "restaurant": 1,
  "restaurant_name": "Joe's Pizza",
  "table": 5,
  "table_number": "Table 5",
  "customer_name": "John Doe",
  "customer_phone": "+1-555-0100",
  "status": "PREPARING",
  "status_display": "Preparing",
  "total_amount": "25.98",
  "special_instructions": "Extra napkins",
  "items": [
    {
      "id": 1,
      "menu_item": 10,
      "menu_item_name": "Margherita Pizza",
      "menu_item_image": "/media/items/pizza.jpg",
      "quantity": 2,
      "unit_price": "12.99",
      "subtotal": "25.98",
      "special_instructions": "No onions"
    }
  ],
  "created_at": "2024-01-25T12:00:00Z",
  "confirmed_at": "2024-01-25T12:01:00Z",
  "prepared_at": "2024-01-25T12:05:00Z",
  "ready_at": null,
  "served_at": null,
  "completed_at": null
}
```

**PATCH /api/v1/manager/orders/{id}/update_status/**
Update order status.

**Request:**
```json
{
  "status": "READY"
}
```

Valid status transitions:
- PENDING → CONFIRMED, CANCELLED
- CONFIRMED → PREPARING, CANCELLED
- PREPARING → READY, CANCELLED
- READY → SERVED, CANCELLED
- SERVED → COMPLETED

**DELETE /api/v1/manager/orders/{id}/**
Cancel order (sets status to CANCELLED, doesn't actually delete).

**GET /api/v1/manager/orders/stats/**
Get order statistics.

Query parameters:
- `date_from` - From date (defaults to today)
- `date_to` - To date (defaults to today)

**Response:**
```json
{
  "total_orders": 50,
  "pending_orders": 3,
  "confirmed_orders": 2,
  "preparing_orders": 5,
  "ready_orders": 2,
  "served_orders": 10,
  "completed_orders": 25,
  "cancelled_orders": 3,
  "total_revenue": "1250.50",
  "average_order_value": "35.73",
  "date_from": "2024-01-25",
  "date_to": "2024-01-25"
}
```

**GET /api/v1/manager/orders/export/**
Export orders (placeholder for CSV export).

---

## Customer API - Menu Browsing

**No authentication required.**

### Menu

**GET /api/v1/customer/menu/restaurants/{id}/**
Get restaurant menu by ID.

**GET /api/v1/customer/menu/restaurants/{slug}/**
Get restaurant menu by slug.

**Response:**
```json
{
  "id": 1,
  "name": "Joe's Pizza",
  "slug": "joes-pizza",
  "address": "123 Main St",
  "phone": "+1-555-0100",
  "logo": "/media/restaurants/logo.jpg",
  "is_active": true,
  "business_hours": {
    "monday": "11:00-22:00",
    "tuesday": "11:00-22:00"
  },
  "timezone": "America/New_York",
  "menu_groups": [
    {
      "id": 1,
      "type": "Lunch",
      "group_order": 1,
      "categories": [
        {
          "id": 1,
          "name": "Pizzas",
          "cat_order": 1,
          "items": [
            {
              "id": 10,
              "name": "Margherita Pizza",
              "description": "Classic tomato sauce and mozzarella",
              "price": "12.99",
              "image": "/media/items/margherita.jpg",
              "is_available": true,
              "is_special_of_day": false,
              "preparation_time": 15,
              "allergens": ["dairy", "gluten"],
              "dietary_tags": ["vegetarian"]
            }
          ]
        }
      ]
    }
  ]
}
```

**GET /api/v1/customer/menu/menu-items/**
List menu items with filters.

Query parameters:
- `category` - Filter by category
- `search` - Search items

---

## Customer API - QR Code & Ordering

**No authentication required.**

### QR Code

**GET /api/v1/customer/qr/{qr_code}/**
Resolve QR code to restaurant and table information.

**Response:**
```json
{
  "restaurant": {
    "id": 1,
    "name": "Joe's Pizza",
    "slug": "joes-pizza",
    "logo": "/media/restaurants/logo.jpg",
    "is_active": true
  },
  "table": {
    "id": 5,
    "table_number": "Table 5",
    "capacity": 4
  },
  "redirect_url": "/menu/joes-pizza?table=5"
}
```

### Orders

**POST /api/v1/customer/orders/**
Create a new order.

**Request:**
```json
{
  "restaurant_slug": "joes-pizza",
  "table_id": 5,
  "items": [
    {
      "menu_item_id": 10,
      "quantity": 2,
      "special_instructions": "No onions"
    },
    {
      "menu_item_id": 11,
      "quantity": 1
    }
  ],
  "customer_name": "John Doe",
  "customer_phone": "+1-555-0100",
  "special_instructions": "Extra napkins"
}
```

**Response:**
```json
{
  "id": 1,
  "order_number": "ORD-20240125-A3F9",
  "restaurant": 1,
  "restaurant_name": "Joe's Pizza",
  "table": 5,
  "table_number": "Table 5",
  "customer_name": "John Doe",
  "customer_phone": "+1-555-0100",
  "status": "PENDING",
  "status_display": "Pending",
  "total_amount": "25.98",
  "items": [...],
  "created_at": "2024-01-25T12:00:00Z"
}
```

**GET /api/v1/customer/orders/{order_number}/**
Get order status (for customer tracking).

---

## Kitchen API - Order Display

**Authentication required (Kitchen Staff role).**

**Headers:** `Authorization: Bearer <access_token>`

### Orders

**GET /api/v1/kitchen/orders/**
List active orders.

Query parameters:
- `show_all` - Show all orders including completed (default: false)
- `status` - Filter by status
- `table` - Filter by table

**GET /api/v1/kitchen/orders/{id}/**
Get order details.

**PATCH /api/v1/kitchen/orders/{id}/update_status/**
Update order status.

**Request:**
```json
{
  "status": "PREPARING"
}
```

**GET /api/v1/kitchen/orders/pending_count/**
Get count of orders by status.

**Response:**
```json
{
  "pending": 3,
  "confirmed": 2,
  "preparing": 5,
  "ready": 2,
  "total_active": 12
}
```

**GET /api/v1/kitchen/orders/by_status/**
Get orders grouped by status (for Kanban board).

**Response:**
```json
{
  "pending": [
    {
      "id": 1,
      "order_number": "ORD-20240125-A3F9",
      "table_number": "Table 5",
      "status": "PENDING",
      "total_amount": "25.98",
      "items_count": 2,
      "created_at": "2024-01-25T12:00:00Z"
    }
  ],
  "preparing": [...],
  "ready": [...]
}
```

---

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "field_name": ["Error message"],
  "detail": "Overall error message"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

---

## Testing with cURL

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "manager", "password": "password123"}'
```

### Create Table
```bash
curl -X POST http://localhost:8000/api/v1/manager/tables/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_number": "Table 1", "capacity": 4, "is_active": true}'
```

### Create Order (Customer)
```bash
curl -X POST http://localhost:8000/api/v1/customer/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_slug": "joes-pizza",
    "table_id": 1,
    "items": [{"menu_item_id": 1, "quantity": 2}],
    "customer_name": "John Doe"
  }'
```

### Update Order Status (Kitchen)
```bash
curl -X PATCH http://localhost:8000/api/v1/kitchen/orders/1/update_status/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "PREPARING"}'
```

---

## Swagger UI

For interactive API testing, visit:
```
http://localhost:8000/api/docs/
```

Complete OpenAPI schema available at:
```
http://localhost:8000/api/schema/
```
