# Frontend Quick Start Guide

## 🎨 Beautiful Manager Portal Created!

A modern, responsive React application with:
- Clean authentication system
- Real-time dashboard with statistics
- Beautiful Tailwind CSS styling
- Smooth animations and transitions
- Protected routes
- Auto token refresh

---

## 🚀 How to Run

### 1. Start the Backend Server (Terminal 1)

```bash
cd C:\Users\sazza\PycharmProjects\foodapp
python manage.py runserver
```

The backend should be running at: `http://localhost:8000`

### 2. Start the Frontend Dev Server (Terminal 2)

```bash
cd C:\Users\sazza\PycharmProjects\foodapp\frontend\apps\manager-portal
npm run dev
```

The frontend will be available at: `http://localhost:5173`

---

## 🔐 Login Credentials

Use the test credentials:
- **Username:** `manager`
- **Password:** `manager123`

---

## ✨ What You'll See

### Login Page
- Beautiful gradient background
- Clean card-based form
- Loading states
- Error handling
- Demo credentials displayed

### Dashboard
After logging in, you'll see:

**Statistics Cards:**
- Total Orders Today
- Revenue Today
- Pending Orders
- Completed Orders

**Order Status Overview:**
- Visual breakdown of order statuses
- Pending, Confirmed, Preparing, Ready, Served counts

**Quick Actions:**
- Links to view orders
- Edit menu
- Manage tables

### Navigation
Beautiful dark sidebar with:
- Restaurant name display
- Dashboard
- Menu
- Orders
- Tables & QR
- Settings
- User info and logout

---

## 🎨 Design Features

- **Modern UI:** Clean, professional design with Tailwind CSS
- **Responsive:** Works on all screen sizes
- **Dark Sidebar:** Professional dark theme sidebar
- **Smooth Transitions:** Hover effects and animations
- **Real-time Data:** Dashboard updates with live API data
- **Loading States:** Elegant loading indicators
- **Error Handling:** User-friendly error messages

---

## 📁 Project Structure

```
manager-portal/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   │   └── DashboardLayout.tsx  # Main layout wrapper
│   │   ├── ui/
│   │   │   ├── Button.tsx           # Reusable button component
│   │   │   ├── Card.tsx             # Card components
│   │   │   └── Input.tsx            # Form input component
│   │   └── ProtectedRoute.tsx       # Route protection
│   ├── lib/
│   │   ├── api.ts                   # Axios API client
│   │   └── utils.ts                 # Utility functions
│   ├── pages/
│   │   ├── LoginPage.tsx            # Login page
│   │   └── DashboardPage.tsx        # Dashboard
│   ├── store/
│   │   └── authStore.ts             # Zustand auth state
│   ├── App.tsx                      # Main app with routing
│   ├── main.tsx                     # Entry point
│   └── index.css                    # Tailwind CSS
├── tailwind.config.js               # Tailwind configuration
├── package.json                     # Dependencies
└── vite.config.ts                   # Vite configuration
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool & dev server |
| Tailwind CSS | Styling |
| React Router | Navigation |
| TanStack Query | Server state management |
| Zustand | Client state management |
| Axios | HTTP client |
| Lucide React | Beautiful icons |

---

## 🎯 Features Implemented

### ✅ Complete
- [x] Authentication system with JWT
- [x] Login page with validation
- [x] Protected routes
- [x] Auto token refresh
- [x] Dashboard with real-time stats
- [x] Navigation sidebar
- [x] Responsive layout
- [x] Loading states
- [x] Error handling
- [x] Beautiful UI components

### ⏳ Coming Next
- [ ] Menu Management (full CRUD)
- [ ] Order Management (view, update status)
- [ ] Table & QR Code Management
- [ ] Restaurant Settings
- [ ] Image uploads
- [ ] Advanced filtering and search

---

## 🐛 Troubleshooting

### Frontend won't start
```bash
# Make sure you're in the right directory
cd C:\Users\sazza\PycharmProjects\foodapp\frontend\apps\manager-portal

# Install dependencies if needed
npm install

# Run dev server
npm run dev
```

### Login not working
- Make sure backend is running at `http://localhost:8000`
- Check that test data is created (run `python setup_test_data.py`)
- Check browser console for errors
- Verify credentials: manager / manager123

### CORS errors
- Backend should have CORS configured for `http://localhost:5173`
- Check `.env` file in backend has correct CORS_ALLOWED_ORIGINS

---

## 📸 Screenshots

### Login Page
- Clean, centered card design
- Gradient background (blue to indigo)
- Restaurant icon at top
- Demo credentials shown below form
- Loading spinner on submit

### Dashboard
- 4 statistics cards with icons
- Order status breakdown
- Quick action buttons
- Professional gray theme

---

## 🎨 Color Scheme

**Primary:** Blue (#3b82f6)
- Used for buttons, links, active states

**Background:** Light gray (#f9fafb)
- Clean, professional background

**Sidebar:** Dark gray (#111827)
- Professional dark theme

**Cards:** White with subtle shadows
- Clean, elevated appearance

---

## 🔄 Next Steps

1. **Run Both Servers:**
   - Terminal 1: `python manage.py runserver`
   - Terminal 2: `npm run dev` (in manager-portal folder)

2. **Open Browser:**
   - Go to `http://localhost:5173`

3. **Login:**
   - Use `manager` / `manager123`

4. **Explore:**
   - View dashboard statistics
   - Navigate through sidebar
   - Check out the beautiful UI!

---

## 🎉 You're Ready!

The beautiful manager portal is ready to use! It's a professional, modern interface that connects seamlessly to your Django backend.

**Enjoy your new restaurant management system! 🍕**
