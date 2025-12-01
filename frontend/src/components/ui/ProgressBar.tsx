import React from 'react';

export type ProgressBarVariant = 'primary' | 'success' | 'danger' | 'warning' | 'info';

export interface ProgressBarProps {
  progress: number; // 0 to 1
  variant?: ProgressBarVariant;
  showLabel?: boolean;
  label?: string;
  className?: string;
}

const variantClasses: Record<ProgressBarVariant, string> = {
  primary: 'bg-blue-500',
  success: 'bg-green-500',
  danger: 'bg-red-500',
  warning: 'bg-yellow-500',
  info: 'bg-purple-500',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  variant = 'primary',
  showLabel = false,
  label,
  className = '',
}) => {
  const percentage = Math.min(Math.max(progress * 100, 0), 100);
  const displayLabel = label || `${Math.round(percentage)}%`;

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm text-gray-600">{displayLabel}</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${variantClasses[variant]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

