# Kitchen Display System

A real-time Kanban board for kitchen staff to manage orders with automatic updates and audio notifications.

## Features

- **Kanban Board** - Orders organized by status (Pending, Confirmed, Preparing, Ready)
- **Real-Time Updates** - Auto-refresh every 3 seconds
- **Audio Notifications** - Sound alert for new orders
- **One-Click Status Updates** - Move orders through workflow with single button
- **Visual Alerts** - Urgent orders highlighted when taking too long
- **Dark Theme** - Optimized for kitchen environment
- **Fullscreen Layout** - Designed for wall-mounted displays

## Tech Stack

- React 18 + TypeScript
- Vite
- React Router v7
- TanStack Query (3-second polling)
- Tailwind CSS v4 (Dark Theme)
- Lucide React (Icons)

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will run on `http://localhost:5178`

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Usage

### Login
- Navigate to `/login`
- Use kitchen staff credentials
- Demo: username=`kitchen`, password=`kitchen123`

### Kitchen Display
- 4-column Kanban board
- Each column shows orders in that status
- Click button on order card to move to next status
- Sound toggle (top-right)
- Manual refresh button
- Auto-update indicator

### Order Status Flow
1. **PENDING** → Click "Confirm"
2. **CONFIRMED** → Click "Start Preparing"
3. **PREPARING** → Click "Mark Ready"
4. **READY** → Click "Mark Served"
5. **SERVED** → Order complete

### Features

**Order Cards Display:**
- Order number and table
- Time placed and elapsed time
- All items with quantities
- Special instructions (highlighted)
- Preparation time per item
- Customer name and phone
- Action button for next status

**Visual Indicators:**
- Border color matches status
- Urgent orders pulse (>150% of prep time)
- New order count badge (top-right)
- Bouncing alert for pending orders

**Audio Alerts:**
- Plays sound when new order arrives
- Toggle on/off with button
- Simple beep tone

## API Endpoints

```
GET /api/v1/kitchen/orders/by_status/
  Returns: { PENDING: [], CONFIRMED: [], PREPARING: [], READY: [] }

PATCH /api/v1/kitchen/orders/{id}/
  Body: { "status": "PREPARING" }
  Returns: Updated order
```

## Customization

### Change Auto-Refresh Interval
Edit `src/pages/KitchenDisplayPage.tsx`:
```typescript
refetchInterval: 3000, // Change to 5000 for 5 seconds
```

### Change Alert Threshold
Edit `src/components/orders/OrderCard.tsx`:
```typescript
const isUrgent = orderAge > totalPrepTime * 60 * 1000 * 1.5; // Change 1.5 to 2.0 for 200%
```

### Change Colors
Edit `src/index.css` theme variables:
```css
--color-pending: #eab308;
--color-confirmed: #3b82f6;
--color-preparing: #f97316;
--color-ready: #a855f7;
```
