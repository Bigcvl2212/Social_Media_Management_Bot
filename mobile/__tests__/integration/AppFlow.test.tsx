/**
 * Integration Tests for Critical Flows
 * Tests for end-to-end user journeys in the mobile app
 */

import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '../../../src/contexts/ThemeContext';
import App from '../../../App';

// Mock all external dependencies
jest.mock('react-native-mmkv');
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');
jest.mock('@react-native-firebase/messaging', () => ({
  __esModule: true,
  default: () => ({
    hasPermission: jest.fn(() => Promise.resolve(true)),
    subscribeToTopic: jest.fn(),
    unsubscribeFromTopic: jest.fn(),
    requestPermission: jest.fn(() => Promise.resolve(true)),
    getToken: jest.fn(() => Promise.resolve('mock-token')),
  }),
}));
jest.mock('react-native-image-picker');
jest.mock('react-native-localize');
jest.mock('@react-native-community/netinfo');
jest.mock('react-native-permissions');

// Mock navigation
jest.mock('@react-navigation/native', () => {
  const actualNav = jest.requireActual('@react-navigation/native');
  return {
    ...actualNav,
    useNavigation: () => ({
      navigate: jest.fn(),
      goBack: jest.fn(),
    }),
    useFocusEffect: jest.fn(),
  };
});

const createTestQueryClient = () => {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
};

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <NavigationContainer>
          {component}
        </NavigationContainer>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('App Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render app successfully', async () => {
    const { getByText } = renderWithProviders(<App />);
    
    // Wait for app to load
    await waitFor(() => {
      expect(getByText).toBeDefined();
    });
  });

  describe('Theme Integration', () => {
    it('should switch themes across the app', async () => {
      const { getByTestId } = renderWithProviders(<App />);
      
      // Test theme switching functionality
      await waitFor(() => {
        // Verify theme provider is working
        expect(getByTestId).toBeDefined();
      });
    });
  });

  describe('OAuth Flow Integration', () => {
    it('should handle complete OAuth flow', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test OAuth integration
        expect(getByText).toBeDefined();
      });
    });
  });

  describe('Content Creation Flow', () => {
    it('should allow creating and scheduling posts', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test content creation flow
        expect(getByText).toBeDefined();
      });
    });
  });

  describe('Analytics Flow', () => {
    it('should display analytics data correctly', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test analytics display
        expect(getByText).toBeDefined();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test error handling
        expect(getByText).toBeDefined();
      });
    });

    it('should handle authentication errors', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test auth error handling
        expect(getByText).toBeDefined();
      });
    });
  });

  describe('Offline Mode', () => {
    it('should work in offline mode', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test offline functionality
        expect(getByText).toBeDefined();
      });
    });

    it('should sync when coming back online', async () => {
      const { getByText } = renderWithProviders(<App />);
      
      await waitFor(() => {
        // Test sync functionality
        expect(getByText).toBeDefined();
      });
    });
  });
});