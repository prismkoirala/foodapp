import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Pages
import { LoginPage } from './pages/LoginPage';
import { KitchenDisplayPage } from './pages/KitchenDisplayPage';

// Create Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000, // 1 second
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const hasToken = localStorage.getItem('access_token');

  if (!hasToken) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Login */}
          <Route path="/login" element={<LoginPage />} />

          {/* Kitchen Display */}
          <Route
            path="/kitchen"
            element={
              <ProtectedRoute>
                <KitchenDisplayPage />
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/kitchen" replace />} />

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-foreground mb-4">404</h1>
                  <p className="text-muted-foreground">Page not found</p>
                </div>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
