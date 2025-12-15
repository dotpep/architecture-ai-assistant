/**
 * ErrorMessage Component
 * Displays user-friendly error messages with retry functionality
 * Requirements: 1.5
 */

import React from 'react';

export type ErrorType = 'network' | 'timeout' | 'invalid' | 'parse' | 'general';

interface ErrorMessageProps {
  /** The error type for appropriate messaging */
  type?: ErrorType;
  /** Custom error message (overrides default) */
  message?: string;
  /** Callback for retry action */
  onRetry?: () => void;
  /** Callback for dismiss action */
  onDismiss?: () => void;
  /** Whether to show as inline or full-width */
  variant?: 'inline' | 'banner' | 'card';
  /** Additional CSS classes */
  className?: string;
}

/**
 * Default error messages by type
 */
const ERROR_MESSAGES: Record<ErrorType, { title: string; message: string }> = {
  network: {
    title: 'Connection Error',
    message: 'Unable to connect. Please check your internet connection.',
  },
  timeout: {
    title: 'Request Timeout',
    message: 'Request timed out. Please try again.',
  },
  invalid: {
    title: 'Invalid Response',
    message: 'Something went wrong. Please try again.',
  },
  parse: {
    title: 'Rendering Error',
    message: 'Unable to render diagram. The generated code may be invalid.',
  },
  general: {
    title: 'Error',
    message: 'An unexpected error occurred. Please try again.',
  },
};

/**
 * Error icon component
 */
const ErrorIcon: React.FC<{ className?: string }> = ({ className = 'w-5 h-5' }) => (
  <svg
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
    />
  </svg>
);

/**
 * Retry icon component
 */
const RetryIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <svg
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
    />
  </svg>
);

/**
 * Close icon component
 */
const CloseIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <svg
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M6 18L18 6M6 6l12 12"
    />
  </svg>
);

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  type = 'general',
  message,
  onRetry,
  onDismiss,
  variant = 'inline',
  className = '',
}) => {
  const errorContent = ERROR_MESSAGES[type];
  const displayMessage = message || errorContent.message;

  // Inline variant - compact error display
  if (variant === 'inline') {
    return (
      <div
        className={`flex items-center gap-2 text-red-600 text-sm ${className}`}
        role="alert"
      >
        <ErrorIcon className="w-4 h-4 flex-shrink-0" />
        <span>{displayMessage}</span>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-2 text-red-700 hover:text-red-800 underline text-xs font-medium"
            aria-label="Retry"
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  // Banner variant - full-width notification
  if (variant === 'banner') {
    return (
      <div
        className={`bg-red-50 border-l-4 border-red-500 p-4 ${className}`}
        role="alert"
      >
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <ErrorIcon className="w-5 h-5 text-red-500" />
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-red-800">
              {errorContent.title}
            </p>
            <p className="mt-1 text-sm text-red-700">{displayMessage}</p>
          </div>
          <div className="ml-4 flex items-center gap-2">
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-700 bg-red-100 rounded-md hover:bg-red-200 transition-colors"
                aria-label="Retry"
              >
                <RetryIcon className="w-4 h-4 mr-1" />
                Retry
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-red-500 hover:text-red-700 transition-colors"
                aria-label="Dismiss"
              >
                <CloseIcon />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Card variant - centered error card
  return (
    <div
      className={`bg-white rounded-lg shadow-md border border-red-200 p-6 text-center max-w-md mx-auto ${className}`}
      role="alert"
    >
      <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
        <ErrorIcon className="w-6 h-6 text-red-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {errorContent.title}
      </h3>
      <p className="text-gray-600 mb-4">{displayMessage}</p>
      <div className="flex items-center justify-center gap-3">
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            aria-label="Retry"
          >
            <RetryIcon className="w-4 h-4 mr-2" />
            Try Again
          </button>
        )}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
            aria-label="Dismiss"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;

/**
 * Helper function to determine error type from error object
 */
export const getErrorType = (error: unknown): ErrorType => {
  if (error instanceof Error) {
    const message = error.message.toLowerCase();
    if (message.includes('network') || message.includes('fetch')) {
      return 'network';
    }
    if (message.includes('timeout') || message.includes('timed out')) {
      return 'timeout';
    }
    if (message.includes('parse') || message.includes('render') || message.includes('mermaid')) {
      return 'parse';
    }
    if (message.includes('invalid') || message.includes('bad request')) {
      return 'invalid';
    }
  }
  return 'general';
};
