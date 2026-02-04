'use client';

import { AlertTriangle, X } from 'lucide-react';
import { useState } from 'react';

interface UserFriendlyErrorProps {
  message: string;
  details?: string;
  onClose?: () => void;
  variant?: 'error' | 'warning' | 'info';
}

const UserFriendlyError = ({
  message,
  details,
  onClose,
  variant = 'error'
}: UserFriendlyErrorProps) => {
  const [isVisible, setIsVisible] = useState(true);

  const getVariantStyles = () => {
    switch (variant) {
      case 'warning':
        return {
          container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
          icon: 'text-yellow-400',
          title: 'Warning',
        };
      case 'info':
        return {
          container: 'bg-blue-50 border-blue-200 text-blue-800',
          icon: 'text-blue-400',
          title: 'Information',
        };
      default: // error
        return {
          container: 'bg-red-50 border-red-200 text-red-800',
          icon: 'text-red-400',
          title: 'Error',
        };
    }
  };

  const styles = getVariantStyles();

  if (!isVisible) return null;

  return (
    <div className={`border rounded-lg p-4 mb-4 ${styles.container}`}>
      <div className="flex items-start">
        <AlertTriangle className={`h-5 w-5 ${styles.icon} mt-0.5 mr-3 flex-shrink-0`} />
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <h3 className="text-sm font-medium">{styles.title}</h3>
            {onClose && (
              <button
                onClick={() => {
                  setIsVisible(false);
                  onClose();
                }}
                className="text-current hover:opacity-80 transition-opacity"
                aria-label="Dismiss"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <div className="mt-2 text-sm">
            <p>{message}</p>
            {details && (
              <details className="mt-2">
                <summary className="cursor-pointer text-xs opacity-80 hover:opacity-100">
                  Show details
                </summary>
                <div className="mt-1 pt-2 border-t border-current opacity-75 text-xs whitespace-pre-wrap">
                  {details}
                </div>
              </details>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserFriendlyError;