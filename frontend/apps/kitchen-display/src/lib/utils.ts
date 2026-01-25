import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

export function getElapsedTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins === 1) return '1 min ago';
  if (diffMins < 60) return `${diffMins} mins ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours === 1) return '1 hour ago';
  return `${diffHours} hours ago`;
}

export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    PENDING: 'bg-amber-500 text-white',
    CONFIRMED: 'bg-sky-500 text-white',
    PREPARING: 'bg-orange-600 text-white',
    READY: 'bg-emerald-600 text-white',
    SERVED: 'bg-green-600 text-white',
    COMPLETED: 'bg-gray-500 text-white',
    CANCELLED: 'bg-red-500 text-white',
  };
  return statusColors[status] || 'bg-gray-500 text-white';
}

export function getStatusBorderColor(status: string): string {
  const statusColors: Record<string, string> = {
    PENDING: 'border-amber-500',
    CONFIRMED: 'border-sky-500',
    PREPARING: 'border-orange-600',
    READY: 'border-emerald-600',
    SERVED: 'border-green-600',
    COMPLETED: 'border-gray-500',
    CANCELLED: 'border-red-500',
  };
  return statusColors[status] || 'border-gray-500';
}

export function getStatusText(status: string): string {
  const statusTexts: Record<string, string> = {
    PENDING: 'New Order',
    CONFIRMED: 'Confirmed',
    PREPARING: 'In Progress',
    READY: 'Ready to Serve',
    SERVED: 'Served',
    COMPLETED: 'Completed',
    CANCELLED: 'Cancelled',
  };
  return statusTexts[status] || status;
}

export function playNotificationSound() {
  // Create a simple beep sound
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();

  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);

  oscillator.frequency.value = 800;
  oscillator.type = 'sine';

  gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

  oscillator.start(audioContext.currentTime);
  oscillator.stop(audioContext.currentTime + 0.5);
}
