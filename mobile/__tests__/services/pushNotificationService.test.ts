/**
 * Push Notification Service Tests
 * Tests for Firebase Cloud Messaging integration
 */

import { Platform, PermissionsAndroid } from 'react-native';
import messaging from '@react-native-firebase/messaging';
import pushNotificationService from '../../src/services/pushNotificationService';

// Mock Firebase messaging
jest.mock('@react-native-firebase/messaging', () => ({
  __esModule: true,
  default: () => ({
    requestPermission: jest.fn().mockResolvedValue(1), // AuthorizationStatus.AUTHORIZED
    getToken: jest.fn().mockResolvedValue('mock-fcm-token'),
    onTokenRefresh: jest.fn(),
    onMessage: jest.fn(),
    onNotificationOpenedApp: jest.fn(),
    getInitialNotification: jest.fn().mockResolvedValue(null),
    setBackgroundMessageHandler: jest.fn(),
    subscribeToTopic: jest.fn().mockResolvedValue(undefined),
    unsubscribeFromTopic: jest.fn().mockResolvedValue(undefined),
  }),
  AuthorizationStatus: {
    AUTHORIZED: 1,
    DENIED: 0,
    PROVISIONAL: 2,
  },
}));

// Mock React Native modules
jest.mock('react-native', () => ({
  Platform: {
    OS: 'ios',
    Version: 14,
  },
  PermissionsAndroid: {
    request: jest.fn().mockResolvedValue('granted'),
    PERMISSIONS: {
      POST_NOTIFICATIONS: 'android.permission.POST_NOTIFICATIONS',
    },
    RESULTS: {
      GRANTED: 'granted',
    },
  },
  Alert: {
    alert: jest.fn(),
  },
}));

// Mock MMKV
jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    set: jest.fn(),
    delete: jest.fn(),
  })),
}));

// Mock API client
jest.mock('../../src/services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn().mockResolvedValue({ data: { success: true } }),
  },
}));

describe('PushNotificationService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('initialize', () => {
    it('should initialize successfully with proper permissions', async () => {
      const mockMessaging = messaging();
      mockMessaging.requestPermission.mockResolvedValue(1); // AUTHORIZED
      mockMessaging.getToken.mockResolvedValue('test-token');

      await pushNotificationService.initialize();

      expect(mockMessaging.requestPermission).toHaveBeenCalled();
      expect(mockMessaging.getToken).toHaveBeenCalled();
      expect(mockMessaging.onMessage).toHaveBeenCalled();
      expect(mockMessaging.onNotificationOpenedApp).toHaveBeenCalled();
    });

    it('should handle permission denial gracefully', async () => {
      const mockMessaging = messaging();
      mockMessaging.requestPermission.mockResolvedValue(0); // DENIED

      // Should not throw
      await expect(pushNotificationService.initialize()).resolves.not.toThrow();
    });

    it('should request Android notification permission on API level 33+', async () => {
      Platform.OS = 'android';
      Platform.Version = 33;

      await pushNotificationService.initialize();

      expect(PermissionsAndroid.request).toHaveBeenCalledWith(
        PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
      );
    });
  });

  describe('FCM token management', () => {
    it('should get and store FCM token', async () => {
      const mockMessaging = messaging();
      mockMessaging.getToken.mockResolvedValue('new-token');

      await pushNotificationService.initialize();

      expect(mockMessaging.getToken).toHaveBeenCalled();
    });

    it('should handle token refresh', async () => {
      const mockMessaging = messaging();
      const mockOnTokenRefresh = jest.fn();
      mockMessaging.onTokenRefresh.mockImplementation(mockOnTokenRefresh);

      await pushNotificationService.initialize();

      expect(mockMessaging.onTokenRefresh).toHaveBeenCalled();
    });

    it('should return current token', () => {
      const token = pushNotificationService.getCurrentToken();
      // Initially null before initialization
      expect(typeof token === 'string' || token === null).toBe(true);
    });
  });

  describe('topic subscription', () => {
    it('should subscribe to topic successfully', async () => {
      const mockMessaging = messaging();
      mockMessaging.subscribeToTopic.mockResolvedValue(undefined);

      await pushNotificationService.subscribeToTopic('user-updates');

      expect(mockMessaging.subscribeToTopic).toHaveBeenCalledWith('user-updates');
    });

    it('should unsubscribe from topic successfully', async () => {
      const mockMessaging = messaging();
      mockMessaging.unsubscribeFromTopic.mockResolvedValue(undefined);

      await pushNotificationService.unsubscribeFromTopic('user-updates');

      expect(mockMessaging.unsubscribeFromTopic).toHaveBeenCalledWith('user-updates');
    });

    it('should handle subscription errors gracefully', async () => {
      const mockMessaging = messaging();
      mockMessaging.subscribeToTopic.mockRejectedValue(new Error('Network error'));

      // Should not throw
      await expect(
        pushNotificationService.subscribeToTopic('invalid-topic')
      ).resolves.not.toThrow();
    });
  });

  describe('notification handling', () => {
    it('should handle foreground messages', async () => {
      const mockMessaging = messaging();
      const mockOnMessage = jest.fn();
      mockMessaging.onMessage.mockImplementation(mockOnMessage);

      await pushNotificationService.initialize();

      expect(mockMessaging.onMessage).toHaveBeenCalled();
    });

    it('should handle notification opened app', async () => {
      const mockMessaging = messaging();
      const mockOnNotificationOpenedApp = jest.fn();
      mockMessaging.onNotificationOpenedApp.mockImplementation(mockOnNotificationOpenedApp);

      await pushNotificationService.initialize();

      expect(mockMessaging.onNotificationOpenedApp).toHaveBeenCalled();
    });

    it('should check for initial notification', async () => {
      const mockMessaging = messaging();
      mockMessaging.getInitialNotification.mockResolvedValue(null);

      await pushNotificationService.initialize();

      expect(mockMessaging.getInitialNotification).toHaveBeenCalled();
    });
  });

  describe('notification storage', () => {
    it('should get stored notifications', () => {
      const notifications = pushNotificationService.getStoredNotifications();
      
      expect(Array.isArray(notifications)).toBe(true);
    });

    it('should mark notification as read', () => {
      // Should not throw
      expect(() => {
        pushNotificationService.markAsRead('test-notification-id');
      }).not.toThrow();
    });

    it('should clear all notifications', () => {
      // Should not throw
      expect(() => {
        pushNotificationService.clearAllNotifications();
      }).not.toThrow();
    });

    it('should get unread count', () => {
      const count = pushNotificationService.getUnreadCount();
      
      expect(typeof count).toBe('number');
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  describe('background message handling', () => {
    it('should set background message handler', async () => {
      const mockMessaging = messaging();
      mockMessaging.setBackgroundMessageHandler.mockImplementation(() => {});

      await pushNotificationService.initialize();

      expect(mockMessaging.setBackgroundMessageHandler).toHaveBeenCalled();
    });
  });
});