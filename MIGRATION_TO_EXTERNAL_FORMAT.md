# Migration to External API Format

## Overview

This guide explains the changes made to match the external API format from `http://gipech.pythonanywhere.com/api/restaurants/1/`

---

## Backend Changes

### 1. Simplified Serializers (`menu/serializers.py`)

**Old Structure:** Multiple serializers for different use cases (customer, manager, read-only, write)

**New Structure:** Simple, single-purpose serializers matching external format

```python
# Menu Item
{
    "id": 1,
    "name": "Peanut sadheko",
    "price": "100.00",
    "order": 0,
    "description": "...",
    "image": "full_url"
}

# Category
{
    "id": 1,
    "name": "Starters",
    "order": 0,
    "items": [...]  # Array of menu items
}

# Menu Group
{
    "id": 1,
    "type": "Food",
    "order": 0,
    "categories": [...]  # Array of categories
}

# Restaurant
{
    "id": 1,
    "name": "Kalpa",
    "address": "Birtamode-06",
    "phone": "9818181818",
    "logo": "full_url",
    "menu_groups": [...]  # Array of menu groups
}
```

### 2. New API Endpoints

**Old Endpoints (Removed):**
- `/api/v1/manager/*` - Manager-specific endpoints
- `/api/v1/customer/*` - Customer-specific endpoints
- `/api/v1/kitchen/*` - Kitchen-specific endpoints

**New Endpoints:**
```
GET  /api/restaurants/          # List all restaurants
GET  /api/restaurants/{id}/     # Get restaurant with full menu + CSRF token
POST /api/orders/               # Create new order
GET  /api/orders/{order_number}/  # Get order status
GET  /api/kitchen/orders/       # Kitchen: List orders
POST /api/kitchen/orders/{id}/status/  # Kitchen: Update order status
```

---

## Frontend Changes Required

### Customer App

**File:** `frontend/apps/customer-app/src/lib/api.ts`

**Old:**
```typescript
const API_BASE_URL = '/api/v1/customer';

export const customerApi = {
  getRestaurant: (slug) => api.get(`/restaurant/${slug}/`),
  getMenuItems: (slug, params) => api.get(`/menu/${slug}/items/`, { params }),
  getCategories: (slug) => api.get(`/menu/${slug}/categories/`),
  resolveQR: (code) => api.get(`/qr/${code}/`),
  createOrder: (data) => api.post(`/orders/`, data),
  getOrderStatus: (orderNumber) => api.get(`/orders/${orderNumber}/`),
};
```

**New:**
```typescript
const API_BASE_URL = '/api';

export const customerApi = {
  // Get restaurant with full menu
  getRestaurant: (id) => api.get(`/restaurants/${id}/`),

  // Create order
  createOrder: (data) => api.post(`/orders/`, data),

  // Get order status
  getOrderStatus: (orderNumber) => api.get(`/orders/${orderNumber}/`),
};
```

**File:** `frontend/apps/customer-app/src/types/index.ts`

**Update Types:**
```typescript
export interface MenuItem {
  id: number;
  name: string;
  price: string;
  order: number;
  description: string;
  image: string | null;
}

export interface MenuCategory {
  id: number;
  name: string;
  order: number;
  items: MenuItem[];
  image: string | null;
}

export interface MenuGroup {
  id: number;
  type: string;  // "Food", "Drinks", etc.
  order: number;
  categories: MenuCategory[];
}

export interface Restaurant {
  id: number;
  name: string;
  address: string;
  phone: string;
  logo: string | null;
  menu_groups: MenuGroup[];
  csrfHeaderName?: string;
  csrfToken?: string;
}
```

**File:** `frontend/apps/customer-app/src/pages/MenuPage.tsx`

**Changes:**
1. Change from `useParams<{ restaurantSlug }>` to `useParams<{ restaurantId }>`
2. Fetch by ID instead of slug
3. Parse menu_groups → categories → items structure

```typescript
// Old
const { restaurantSlug } = useParams();
const { data: restaurant } = useQuery({
  queryKey: ['restaurant', restaurantSlug],
  queryFn: () => customerApi.getRestaurant(restaurantSlug!),
});

// New
const { restaurantId } = useParams();
const { data: restaurantData } = useQuery({
  queryKey: ['restaurant', restaurantId],
  queryFn: () => customerApi.getRestaurant(restaurantId!),
});

// Parse menu structure
const restaurant = restaurantData?.data;
const allCategories = restaurant?.menu_groups?.flatMap(g => g.categories) || [];
const allItems = allCategories.flatMap(c => c.items) || [];
```

**Routing Update:**
```typescript
// Old
<Route path="/menu/:restaurantSlug" element={<MenuPage />} />

// New
<Route path="/menu/:restaurantId" element={<MenuPage />} />
```

---

### Manager Portal

**File:** `frontend/apps/manager-portal/src/lib/api.ts`

**Old:**
```typescript
const API_BASE_URL = '/api/v1/manager';
```

**New:**
```typescript
const API_BASE_URL = '/api';

// Use Django Admin for management instead
// Or create custom admin endpoints as needed
```

**Recommendation:** Use Django Admin (`/admin/`) for restaurant management instead of custom manager portal.

---

### Kitchen Display

**File:** `frontend/apps/kitchen-display/src/lib/api.ts`

**Old:**
```typescript
const API_BASE_URL = '/api/v1/kitchen';

export const kitchenApi = {
  getOrdersByStatus: () => api.get('/orders/by_status/'),
  updateOrderStatus: (orderId, status) =>
    api.patch(`/orders/${orderId}/`, { status }),
};
```

**New:**
```typescript
const API_BASE_URL = '/api/kitchen';

export const kitchenApi = {
  getOrders: () => api.get('/orders/'),
  updateOrderStatus: (orderId, status) =>
    api.post(`/orders/${orderId}/status/`, { status }),
};
```

---

## Testing the Changes

### 1. Test Restaurant API

```bash
curl http://localhost:8000/api/restaurants/2/
```

Expected response:
```json
{
  "id": 2,
  "name": "Kalpa",
  "address": "Birtamode-06",
  "phone": "9818181818",
  "logo": null,
  "menu_groups": [
    {
      "id": 3,
      "type": "Food",
      "order": 0,
      "categories": [
        {
          "id": 4,
          "name": "Starters",
          "order": 0,
          "items": [
            {
              "id": 9,
              "name": "Peanut sadheko",
              "price": "100.00",
              "order": 0,
              "description": "..."
            }
          ]
        }
      ]
    }
  ],
  "csrfHeaderName": "X-CSRFTOKEN",
  "csrfToken": "..."
}
```

### 2. Frontend Access

**Customer App:**
- Old: `http://localhost:5175/menu/kalpa`
- New: `http://localhost:5175/menu/2`

**Manager Portal:**
- Use Django Admin: `http://localhost:8000/admin/`

**Kitchen Display:**
- Same: `http://localhost:5178/kitchen`

---

## Migration Steps

### Phase 1: Backend (Done)
- [x] Simplified serializers
- [x] Created new view functions
- [x] Updated URL patterns
- [x] Removed complex manager/customer view separation

### Phase 2: Frontend (To Do)
1. Update API client in each app
2. Update TypeScript types
3. Update components to use new data structure
4. Update routing (slug → id)
5. Test all functionality

### Phase 3: Cleanup
1. Remove old serializer files
2. Remove old view files
3. Remove old URL files
4. Update documentation

---

## Key Differences

### Data Structure
| Aspect | Old | New |
|--------|-----|-----|
| Restaurant ID | By slug | By numeric ID |
| Menu Structure | Flat categories | Grouped (Food/Drinks) |
| Item Fields | Many (allergens, etc.) | Simple (id, name, price) |
| URLs | Nested (/v1/customer/menu/...) | Flat (/api/restaurants/...) |
| Authentication | JWT on all endpoints | Public + auth where needed |
| CSRF | Separate | Included in response |

### Simplified Flow
1. Frontend requests `/api/restaurants/{id}/`
2. Backend returns complete restaurant with nested menu
3. Frontend parses menu_groups → categories → items
4. Display organized by groups

---

## Benefits of New Structure

1. **Simpler API** - One endpoint for full menu
2. **Less Requests** - Get everything in one call
3. **Standard Format** - Matches external API
4. **Easier Frontend** - Single data fetch, no complex state management
5. **Better Performance** - Fewer HTTP requests

---

## Next Steps

1. Fix any backend import errors
2. Update each frontend app's API client
3. Update TypeScript types
4. Test each page individually
5. Update routing to use IDs instead of slugs

Would you like me to proceed with updating the frontend apps one by one?
