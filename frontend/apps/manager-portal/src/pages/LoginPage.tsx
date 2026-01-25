import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { UtensilsCrossed } from 'lucide-react';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary text-white p-3 rounded-full">
              <UtensilsCrossed className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Restaurant Manager</h1>
          <p className="text-gray-600 mt-2">Sign in to manage your restaurant</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Welcome back</CardTitle>
            <CardDescription>Enter your credentials to access your dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md text-sm">
                  {error}
                </div>
              )}

              <Input
                label="Username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                required
                autoFocus
              />

              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />

              <Button
                type="submit"
                className="w-full"
                size="lg"
                isLoading={isLoading}
              >
                Sign In
              </Button>

              <div className="text-center text-sm text-muted-foreground mt-4">
                <p>Demo Credentials:</p>
                <p className="font-mono text-xs mt-1">manager / manager123</p>
              </div>
            </form>
          </CardContent>
        </Card>

        <p className="text-center text-sm text-gray-600 mt-6">
          Need help? Contact your administrator
        </p>
      </div>
    </div>
  );
}
