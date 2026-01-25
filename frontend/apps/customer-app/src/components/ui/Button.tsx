import React from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, icon, children, disabled, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variants = {
      primary: 'bg-primary text-primary-foreground hover:bg-amber-600 focus:ring-primary shadow-md hover:shadow-lg',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-gray-200 focus:ring-secondary',
      outline: 'border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground focus:ring-primary',
      ghost: 'text-foreground hover:bg-secondary focus:ring-secondary',
      danger: 'bg-accent text-accent-foreground hover:bg-red-600 focus:ring-accent shadow-md hover:shadow-lg',
    };

    const sizes = {
      sm: 'text-sm px-3 py-1.5',
      md: 'text-base px-5 py-2.5',
      lg: 'text-lg px-7 py-3.5',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        )}
        {!isLoading && icon}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
