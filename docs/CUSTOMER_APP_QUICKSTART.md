# Customer Ordering App - Quick Start Guide

## Overview

The customer ordering app is a beautiful, mobile-first React application that allows restaurant customers to:
- Scan QR codes at tables
- Browse the restaurant menu
- Add items to cart
- Place orders
- Track order status in real-time

---

## Running the App

### Terminal 1: Backend API
```bash
cd C:\Users\sazza\PycharmProjects\foodapp
python manage.py runserver
```

### Terminal 2: Customer App
```bash
cd C:\Users\sazza\PycharmProjects\foodapp\frontend\apps\customer-app
npm run dev
```

**App URL:** http://localhost:5175

---

## Testing the App

### 1. Access Menu Directly
Navigate to: `http://localhost:5175/menu/demo-restaurant`

This will show the menu for a restaurant with slug "demo-restaurant"

### 2. Test QR Code Flow

**Step 1:** Create a table with QR code via backend
```bash
# Using Django shell
python manage.py shell

from orders.models import Table
from menu.models import Restaurant

restaurant = Restaurant.objects.first()
table = Table.objects.create(
    restaurant=restaurant,
    table_number="Table 5"
)
print(f"QR Code: {table.qr_code}")
```

**Step 2:** Access the QR URL
Navigate to: `http://localhost:5175/qr/{qr_code_from_above}`

This will resolve the QR code and redirect to the menu with table context.

### 3. Place a Test Order

1. Browse the menu
2. Click "Add" on menu items
3. Click the floating cart button (bottom-right)
4. Review cart and click "Proceed to Checkout"
5. Fill in customer information:
   - Name: John Doe
   - Phone: 555-1234
   - Special Instructions: (optional)
6. Click "Place Order"
7. You'll be redirected to the order status page
8. The page auto-refreshes every 5 seconds

### 4. View Order in Manager Portal

Open: `http://localhost:5174/orders` (manager portal)

You'll see the order you just placed!

---

## Key Features Implemented

### Menu Browsing
- ✅ Restaurant header with logo, address, phone
- ✅ Search bar for menu items
- ✅ Category filtering tabs
- ✅ Special items section (Today's Specials)
- ✅ Menu item cards with:
  - Image
  - Name and description
  - Price
  - Dietary tags (vegan, gluten-free, spicy)
  - Allergen information
  - Preparation time
  - Add to cart button

### Shopping Cart
- ✅ Persistent cart (localStorage)
- ✅ Sliding drawer from right
- ✅ Item thumbnails
- ✅ Quantity controls (+/- buttons)
- ✅ Remove items
- ✅ Subtotal per item
- ✅ Total calculation
- ✅ Floating cart button with item count

### Checkout
- ✅ Order summary
- ✅ Customer information form (name, phone)
- ✅ Special instructions field
- ✅ Form validation
- ✅ Loading states
- ✅ Error handling

### Order Tracking
- ✅ Order confirmation page
- ✅ Status timeline with icons
- ✅ Timestamps for each status
- ✅ Order details with items
- ✅ Customer information display
- ✅ Real-time updates (5-second polling)
- ✅ Beautiful green success header

### QR Code Integration
- ✅ QR code resolution endpoint
- ✅ Automatic redirect to menu with table context
- ✅ Loading state during resolution
- ✅ Error handling for invalid QR codes

---

## Mobile-First Design

The app is optimized for mobile devices:

### Responsive Features
- Touch-friendly buttons (minimum 44px)
- Mobile-optimized layouts
- Sticky header for easy navigation
- Floating cart button for quick access
- Smooth scrolling
- Fast load times

### Color Palette
- Primary: Amber/Orange (#f59e0b) - Appetizing, warm
- Accent: Red (#ef4444) - Call-to-action
- Success: Green (#10b981) - Confirmations
- Background: White (#ffffff) - Clean
- Text: Dark Gray (#1f2937) - Readable

### Typography
- System fonts for fast loading
- Clear hierarchy
- Font sizes optimized for mobile

---

## Testing Checklist

### Menu Page
- [ ] Restaurant info displays correctly
- [ ] Search filters menu items
- [ ] Category tabs switch items
- [ ] Special items section shows marked items
- [ ] Menu item cards display all information
- [ ] Add to cart increments quantity
- [ ] Images load correctly

### Cart
- [ ] Cart persists across page refreshes
- [ ] Quantity updates work (+/-)
- [ ] Remove item works
- [ ] Total calculates correctly
- [ ] Floating cart button shows count
- [ ] Drawer opens/closes smoothly

### Checkout
- [ ] Order summary shows all items
- [ ] Form validation works (required fields)
- [ ] Order submits successfully
- [ ] Redirects to order status page
- [ ] Cart clears after order

### Order Status
- [ ] Order details display correctly
- [ ] Status timeline updates
- [ ] Auto-refresh works (check network tab)
- [ ] Status changes reflect in real-time
- [ ] Back to menu button works

### QR Code Flow
- [ ] QR code resolves correctly
- [ ] Redirects to menu with table parameter
- [ ] Invalid QR shows error message

---

## API Integration

### Endpoints Used

**Restaurant & Menu:**
```
GET /api/v1/customer/restaurant/{slug}/
GET /api/v1/customer/menu/{slug}/
GET /api/v1/customer/menu/{slug}/items/?category=&search=&available=true
GET /api/v1/customer/menu/{slug}/categories/
```

**QR Code:**
```
GET /api/v1/customer/qr/{qr_code}/
```

**Orders:**
```
POST /api/v1/customer/orders/
{
  "restaurant": "demo-restaurant",
  "table_id": 1,
  "items": [
    {
      "menu_item_id": 1,
      "quantity": 2,
      "special_instructions": "No onions"
    }
  ],
  "customer_name": "John Doe",
  "customer_phone": "555-1234",
  "special_instructions": "Extra napkins"
}

GET /api/v1/customer/orders/{order_number}/
```

---

## Project Structure

```
frontend/apps/customer-app/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx       # Primary button component
│   │   │   ├── Badge.tsx        # Tags for dietary info
│   │   │   ├── Input.tsx        # Form input
│   │   │   └── Textarea.tsx     # Form textarea
│   │   ├── menu/
│   │   │   └── MenuItemCard.tsx # Menu item display
│   │   └── cart/
│   │       └── CartDrawer.tsx   # Shopping cart
│   ├── pages/
│   │   ├── MenuPage.tsx         # Main menu browsing
│   │   ├── CheckoutPage.tsx     # Order checkout
│   │   ├── OrderStatusPage.tsx  # Order tracking
│   │   └── QRLandingPage.tsx    # QR code resolution
│   ├── lib/
│   │   ├── api.ts               # API client (axios)
│   │   └── utils.ts             # Utilities
│   ├── store/
│   │   └── cartStore.ts         # Cart state (Zustand)
│   ├── types/
│   │   └── index.ts             # TypeScript types
│   ├── App.tsx                  # Routing
│   ├── main.tsx                 # Entry point
│   └── index.css                # Tailwind CSS
├── .env                         # Environment variables
├── package.json
├── vite.config.ts
└── README.md
```

---

## State Management

### Cart Store (Zustand)
```typescript
useCartStore({
  items: CartItem[],              // Cart items
  restaurantSlug: string | null,  // Current restaurant
  tableId: number | null,         // Current table

  addItem(),                      // Add item to cart
  removeItem(),                   // Remove from cart
  updateQuantity(),               // Change quantity
  updateSpecialInstructions(),    // Add notes
  clearCart(),                    // Empty cart
  setRestaurant(),                // Set restaurant
  setTable(),                     // Set table

  getTotalItems(),                // Item count
  getTotalPrice(),                // Total price
  getItem(),                      // Get specific item
})
```

### Server State (TanStack Query)
- Automatic caching (5 minutes)
- Auto-refetch on window focus disabled
- Retry failed requests once
- Loading and error states

---

## Customization

### Change Colors
Edit `src/index.css`:
```css
@theme {
  --color-primary: #f59e0b;  /* Change to your brand color */
  --color-accent: #ef4444;
  /* ... other colors */
}
```

### Change Default Restaurant
Edit `src/App.tsx`:
```typescript
<Route path="/" element={<Navigate to="/menu/your-restaurant-slug" replace />} />
```

### Change Polling Interval
Edit `src/pages/OrderStatusPage.tsx`:
```typescript
refetchInterval: 5000, // Change to 10000 for 10 seconds
```

### Add More Dietary Tags
Edit `src/components/menu/MenuItemCard.tsx`:
```typescript
const getDietaryIcon = (tag: string) => {
  // Add more icon mappings
}
```

---

## Performance Optimizations

### Implemented
- ✅ Image lazy loading
- ✅ Code splitting (React Router)
- ✅ Query caching (TanStack Query)
- ✅ LocalStorage persistence
- ✅ Optimized re-renders
- ✅ Vite for fast HMR

### Future Optimizations
- Virtual scrolling for long lists
- Service worker for offline access
- Progressive image loading
- Bundle size optimization

---

## Troubleshooting

### Port Already in Use
If port 5173 is taken, Vite auto-selects the next available port.
Check the terminal output for the actual URL.

### CORS Errors
Make sure the backend has CORS enabled for `http://localhost:5173` (or your port).

Check `foodapp_backend/settings/development.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]
```

### Cart Not Persisting
Check browser's localStorage in DevTools:
- Open DevTools → Application → Local Storage
- Look for `customer-cart-storage`

### Order Status Not Updating
- Check network tab for polling requests (every 5 seconds)
- Verify backend order status is changing
- Check for console errors

### Images Not Loading
- Verify Django MEDIA_URL is configured
- Check image paths in database
- Enable CORS for media files

---

## Next Steps

### Immediate Enhancements
1. Add item detail modal (click to see full description)
2. Add quantity selector to cart drawer
3. Add order history page
4. Add estimated prep time on order status

### Future Features
1. **User Accounts**
   - Save favorite items
   - Order history
   - Saved addresses/phone

2. **Enhanced Ordering**
   - Schedule orders for later
   - Split payment
   - Tip calculation

3. **Real-time Updates**
   - WebSocket integration
   - Push notifications
   - Live kitchen status

4. **Social Features**
   - Share favorite items
   - Reviews and ratings
   - Photo uploads

5. **Accessibility**
   - Screen reader support
   - Keyboard navigation
   - High contrast mode

6. **Localization**
   - Multi-language support
   - Currency conversion
   - RTL support

---

## Screenshots Reference

### Menu Page
- Clean restaurant header
- Search bar prominently displayed
- Horizontal scrolling category tabs
- Grid of menu item cards (responsive)
- Floating cart button (bottom-right)

### Cart Drawer
- Slides in from right
- Semi-transparent backdrop
- Item list with thumbnails
- Quantity controls per item
- Total at bottom
- Checkout button

### Checkout Page
- Back button (top-left)
- Order summary card
- Customer info form
- Place order button (bottom)

### Order Status Page
- Green gradient success header
- Order number display
- Timeline with icons and timestamps
- Order details card
- Customer info card
- Back to menu button

---

## Support

For issues or questions:
1. Check browser console for errors
2. Check backend logs
3. Verify API endpoints are working
4. Check network tab in DevTools

---

**Congratulations!** 🎉

You now have a fully functional, beautiful customer ordering app that works seamlessly with your backend API!
