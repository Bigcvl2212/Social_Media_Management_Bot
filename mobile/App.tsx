/**
 * Social Media Management Bot Mobile App
 * https://github.com/Bigcvl2212/Social_Media_Management_Bot
 *
 * @format
 */

import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './src/hooks/useAuth';
import { ThemeProvider } from './src/contexts/ThemeContext';
import AppNavigator from './src/navigation/AppNavigator';
import pushNotificationService from './src/services/pushNotificationService';
import './src/i18n'; // Initialize i18n

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  useEffect(() => {
    // Initialize push notifications
    pushNotificationService.initialize();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <AppNavigator />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
