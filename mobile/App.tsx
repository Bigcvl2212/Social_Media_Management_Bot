/**
 * Social Media Management Bot Mobile App
 * https://github.com/Bigcvl2212/Social_Media_Management_Bot
 *
 * @format
 */

import React, { useEffect } from 'react';
import { Linking } from 'react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './src/hooks/useAuth';
import { ThemeProvider } from './src/contexts/ThemeContext';
import AppNavigator from './src/navigation/AppNavigator';
import pushNotificationService from './src/services/pushNotificationService';
import oauthService from './src/services/oauthService';
import { PlatformType } from './src/types';
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

    // Set up deep link handling for OAuth callbacks
    const handleDeepLink = (url: string) => {
      console.log('Deep link received:', url);
      
      if (url.startsWith('socialmediabot://oauth/')) {
        handleOAuthCallback(url);
      }
    };

    // Handle initial deep link (app was closed)
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink(url);
      }
    });

    // Listen for deep links while app is running
    const linkingSubscription = Linking.addEventListener('url', (event) => {
      handleDeepLink(event.url);
    });

    return () => {
      linkingSubscription?.remove();
    };
  }, []);

  const handleOAuthCallback = (url: string) => {
    try {
      const urlObject = new URL(url);
      const platform = urlObject.pathname.split('/').pop() as PlatformType;
      const code = urlObject.searchParams.get('code');
      const state = urlObject.searchParams.get('state');
      const error = urlObject.searchParams.get('error');

      if (error) {
        console.error('OAuth error:', error);
        return;
      }

      if (code && state && platform) {
        oauthService.handleOAuthCallback(platform, code, state);
      }
    } catch (error) {
      console.error('Error parsing OAuth callback URL:', error);
    }
  };

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
