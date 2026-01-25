# Customer Ordering App

A beautiful, mobile-first React application for restaurant customers to browse menus and place orders via QR codes.

## Features

- **QR Code Integration** - Scan table QR codes to access menus
- **Menu Browsing** - Browse restaurant menus with categories and search
- **Shopping Cart** - Add items, adjust quantities, and add special instructions
- **Order Placement** - Place orders with customer information
- **Order Tracking** - Real-time order status updates
- **Mobile-First Design** - Optimized for smartphones and tablets
- **Beautiful UI** - Modern design with Tailwind CSS

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router v7** - Routing
- **TanStack Query** - Server state management
- **Zustand** - Client state management (cart)
- **Axios** - HTTP client
- **Tailwind CSS v4** - Styling
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will run on `http://localhost:5173`

### Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
src/
├── components/
│   ├── ui/              # Reusable UI components
│   ├── menu/            # Menu-specific components
│   ├── cart/            # Cart components
│   └── order/           # Order components
├── pages/
│   ├── MenuPage.tsx     # Main menu browsing
│   ├── CheckoutPage.tsx # Order checkout
│   ├── OrderStatusPage.tsx # Order tracking
│   └── QRLandingPage.tsx # QR code resolution
├── lib/
│   ├── api.ts           # API client
│   └── utils.ts         # Utility functions
├── store/
│   └── cartStore.ts     # Shopping cart state
└── types/
    └── index.ts         # TypeScript types
```

## Key Components

### MenuItemCard
Beautiful card component displaying menu items with:
- Item image
- Name and description
- Price
- Dietary tags (vegan, gluten-free, etc.)
- Allergen information
- Add to cart button

### CartDrawer
Sliding drawer for shopping cart with:
- Item list with images
- Quantity controls
- Remove items
- Total calculation
- Checkout button

### MenuPage
Main menu browsing page with:
- Restaurant header
- Search functionality
- Category filtering
- Special items section
- Floating cart button

### CheckoutPage
Order finalization page with:
- Order summary
- Customer information form
- Special instructions
- Place order button

### OrderStatusPage
Real-time order tracking with:
- Status timeline
- Order details
- Customer information
- Auto-refresh every 5 seconds

## Usage Flow

1. **Customer scans QR code** at table
2. **QR landing page** resolves code and redirects to menu
3. **Browse menu** by category or search
4. **Add items to cart** with special instructions
5. **Checkout** and enter contact information
6. **Order placed** and redirected to status page
7. **Track order** in real-time

## API Endpoints Used

- `GET /customer/restaurant/{slug}/` - Restaurant info
- `GET /customer/menu/{slug}/` - Full menu
- `GET /customer/menu/{slug}/items/` - Menu items with filters
- `GET /customer/menu/{slug}/categories/` - Categories
- `GET /customer/qr/{code}/` - QR code resolution
- `POST /customer/orders/` - Create order
- `GET /customer/orders/{orderNumber}/` - Order status

## Build for Production

```bash
npm run build
```

The optimized build will be in the `dist/` folder.

## Development Tips

- Use React DevTools for component debugging
- Use TanStack Query DevTools for API debugging (bottom-right toggle)
- Cart state persists in localStorage
- Hot Module Replacement (HMR) enabled

## Future Enhancements

- Push notifications for order updates
- Saved customer profiles
- Order history
- Favorites/recently ordered
- Multi-language support
- PWA capabilities for offline access
- Payment integration
