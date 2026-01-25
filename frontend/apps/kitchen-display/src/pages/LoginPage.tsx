import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { ChefHat, LogIn } from 'lucide-react';
import { authApi } from '../lib/api';
import { Button } from '../components/ui/Button';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const loginMutation = useMutation({
    mutationFn: () => authApi.login(username, password),
    onSuccess: (response) => {
      localStorage.setItem('access_token', response.data.tokens.access);
      localStorage.setItem('refresh_token', response.data.tokens.refresh);
      navigate('/kitchen');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Invalid credentials');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    loginMutation.mutate();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <div className="bg-secondary rounded-2xl shadow-2xl p-8 border border-border">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="bg-primary p-6 rounded-2xl">
              <ChefHat className="w-16 h-16 text-primary-foreground" />
            </div>
          </div>

          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">Kitchen Display</h1>
            <p className="text-muted-foreground">Sign in to view orders</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-error/10 border border-error rounded-lg p-4">
                <p className="text-error text-sm text-center">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="username" className="block text-sm font-medium text-foreground mb-2">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter username"
                required
                autoFocus
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Enter password"
                required
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              isLoading={loginMutation.isPending}
              icon={<LogIn className="w-5 h-5" />}
            >
              {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-sm text-muted-foreground text-center mb-2">Demo Credentials:</p>
            <div className="bg-background/50 rounded-lg p-3 text-center">
              <p className="text-sm text-foreground">
                <span className="font-semibold">Username:</span> kitchen
              </p>
              <p className="text-sm text-foreground mt-1">
                <span className="font-semibold">Password:</span> kitchen123
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
