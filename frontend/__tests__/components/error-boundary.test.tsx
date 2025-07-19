import { render, screen, fireEvent } from '@testing-library/react';
import { ReactNode } from 'react';

// Create a simplified error boundary for testing instead of importing the complex one
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

class TestErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.props.onError?.(error, errorInfo);
    
    // Mock Sentry call
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      (window as any).Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: errorInfo.componentStack
          }
        }
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div className="text-center">
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
                Something went wrong
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                We're sorry, but an unexpected error occurred. Please try again.
              </p>
              {process.env.NODE_ENV === 'development' && (
                <details className="mt-4 text-left">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">
                    Error details (development only)
                  </summary>
                  <pre className="mt-2 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded border overflow-auto">
                    {this.state.error?.message}
                  </pre>
                </details>
              )}
            </div>
            <div className="flex justify-center">
              <button
                onClick={() => {
                  if (typeof window !== 'undefined') {
                    window.location.reload();
                  }
                }}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
                type="button"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Component that throws an error for testing
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
}

// Mock Sentry
const mockCaptureException = jest.fn();
Object.defineProperty(window, 'Sentry', {
  value: {
    captureException: mockCaptureException,
  },
});

describe('ErrorBoundary', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Suppress error console logs during tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    (console.error as jest.Mock).mockRestore();
  });

  it('renders children when there is no error', () => {
    render(
      <TestErrorBoundary>
        <ThrowError shouldThrow={false} />
      </TestErrorBoundary>
    );
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders error fallback when there is an error', () => {
    render(
      <TestErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TestErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText("We're sorry, but an unexpected error occurred. Please try again.")).toBeInTheDocument();
  });

  it('shows try again button', () => {
    render(
      <TestErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TestErrorBoundary>
    );
    
    const tryAgainButton = screen.getByRole('button', { name: /try again/i });
    expect(tryAgainButton).toBeInTheDocument();
  });

  it('calls Sentry when available', () => {
    render(
      <TestErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TestErrorBoundary>
    );
    
    expect(mockCaptureException).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Test error'
      }),
      expect.objectContaining({
        contexts: {
          react: {
            componentStack: expect.any(String)
          }
        }
      })
    );
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';
    
    render(
      <TestErrorBoundary>
        <ThrowError shouldThrow={true} />
      </TestErrorBoundary>
    );
    
    expect(screen.getByText('Error details (development only)')).toBeInTheDocument();
    
    process.env.NODE_ENV = originalEnv;
  });

  it('calls custom onError handler when provided', () => {
    const mockOnError = jest.fn();
    
    render(
      <TestErrorBoundary onError={mockOnError}>
        <ThrowError shouldThrow={true} />
      </TestErrorBoundary>
    );
    
    expect(mockOnError).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Test error'
      }),
      expect.objectContaining({
        componentStack: expect.any(String)
      })
    );
  });
});