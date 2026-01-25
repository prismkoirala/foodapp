import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Pages
import { MenuPageNew as MenuPage } from './pages/MenuPageNew';
import { OrderStatusPage } from './pages/OrderStatusPage';
import { QRLandingPage } from './pages/QRLandingPage';

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* QR Code Landing */}
          <Route path="/qr/:qrCode" element={<QRLandingPage />} />

          {/* Menu Page */}
          <Route path="/menu/:restaurantId" element={<MenuPage />} />

          {/* Order Status */}
          <Route path="/order/:orderNumber" element={<OrderStatusPage />} />

          {/* Default redirect to Kalpa restaurant */}
          <Route path="/" element={<Navigate to="/menu/2" replace />} />

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-gray-600">Page not found</p>
                </div>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
