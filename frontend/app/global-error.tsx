'use client';

import { useEffect } from 'react';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

declare global {
  interface Window {
    Sentry?: {
      captureException: (error: Error) => void;
    };
  }
}

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    if (typeof window !== 'undefined' && window.Sentry) {
      window.Sentry.captureException(error);
    }
    console.error('Global error:', error);
  }, [error]);

  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased font-sans">
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div className="text-center">
              <ExclamationTriangleIcon className="mx-auto h-16 w-16 text-red-500" />
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                Application Error
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                A critical error occurred. Please try reloading the page.
              </p>
              {process.env.NODE_ENV === 'development' && error.digest && (
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
            <div className="flex justify-center">
              <button
                onClick={reset}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
                type="button"
              >
                <ArrowPathIcon className="mr-2 h-4 w-4" />
                Try again
              </button>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}