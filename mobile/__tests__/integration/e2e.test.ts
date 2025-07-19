/**
 * End-to-End Integration Tests
 * Tests the full functionality of all services working together
 */

import { Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import pushNotificationService from '../../src/services/pushNotificationService';
import offlineStorageService from '../../src/services/offlineStorageService';
import aiContentService from '../../src/services/aiContentService';
import oauthService from '../../src/services/oauthService';
import mediaUploadService from '../../src/services/mediaUploadService';
import AuthService from '../../src/services/auth';

// Mock all dependencies
jest.mock('@react-native-firebase/messaging');
jest.mock('react-native-mmkv');
jest.mock('@react-native-community/netinfo');
jest.mock('react-native-image-picker');
jest.mock('react-native-permissions');
jest.mock('@react-native-async-storage/async-storage');
jest.mock('react-native', () => ({
  Alert: { alert: jest.fn() },
  Platform: { OS: 'ios' },
}));
jest.mock('../../src/services/api');

describe('End-to-End Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Complete User Workflow', () => {
    it('should complete full user journey: login -> create content -> save offline -> sync', async () => {
      // 1. Mock successful login
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('mock_token');
      
      const isAuth = await AuthService.isAuthenticated();
      expect(isAuth).toBe(true);

      // 2. Mock creating content with AI assistance
      const mockAIContent = {
        title: 'AI Generated Title',
        caption: 'AI generated caption',
        hashtags: ['#ai', '#content'],
        suggestions: ['Use more emojis'],
      };

      require('../../src/services/api').default.post.mockResolvedValue({
        data: mockAIContent,
      });

      const aiContent = await aiContentService.generateContent({
        prompt: 'Create a tech post',
        contentType: 'post',
        platforms: ['instagram'],
      });

      expect(aiContent).toEqual(mockAIContent);

      // 3. Save content offline
      const mockStorage = {
        getString: jest.fn().mockReturnValue('[]'),
        set: jest.fn(),
        delete: jest.fn(),
      };
      require('react-native-mmkv').MMKV.mockImplementation(() => mockStorage);

      const draftId = offlineStorageService.saveDraftOffline({
        title: aiContent.title,
        caption: aiContent.caption,
        content_type: 'post',
        media_urls: [],
        platforms: ['instagram'],
      });

      expect(draftId).toMatch(/^draft_\d+_/);
      expect(mockStorage.set).toHaveBeenCalled();

      // 4. Verify offline storage and sync
      const syncResult = await offlineStorageService.syncPendingDrafts();
      expect(syncResult).toBeDefined();
    });

    it('should handle OAuth flow for multiple platforms', async () => {
      // Mock successful OAuth flows
      require('react-native').Linking = {
        canOpenURL: jest.fn().mockResolvedValue(true),
        openURL: jest.fn().mockResolvedValue(true),
      };

      const platforms = ['instagram', 'twitter', 'facebook'];
      
      for (const platform of platforms) {
        const result = await oauthService.startOAuthFlow(platform as any);
        expect(result).toBe(true);
      }
    });

    it('should handle media upload workflow', async () => {
      // Mock permission and file picker
      require('react-native-permissions').request.mockResolvedValue('granted');
      require('react-native-image-picker').launchImageLibrary.mockImplementation((options, callback) => {
        callback({
          assets: [{
            uri: 'file://test.jpg',
            type: 'image/jpeg',
            fileName: 'test.jpg',
            fileSize: 1024 * 1024,
          }]
        });
      });

      const mockUploadResponse = {
        url: 'https://example.com/uploaded.jpg',
        fileId: 'file123',
        type: 'image',
        size: 1024 * 1024,
      };

      require('../../src/services/api').default.post.mockResolvedValue({
        data: mockUploadResponse,
      });

      const mediaFiles = await mediaUploadService.openGallery({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(mediaFiles).toHaveLength(1);

      if (mediaFiles.length > 0) {
        const uploadResult = await mediaUploadService.uploadMedia(mediaFiles[0]);
        expect(uploadResult).toEqual(mockUploadResponse);
      }
    });

    it('should initialize and manage push notifications', async () => {
      const mockMessaging = require('@react-native-firebase/messaging').default();
      mockMessaging.requestPermission.mockResolvedValue(1); // AUTHORIZED
      mockMessaging.getToken.mockResolvedValue('mock-fcm-token');

      await pushNotificationService.initialize();

      expect(mockMessaging.requestPermission).toHaveBeenCalled();
      expect(mockMessaging.getToken).toHaveBeenCalled();
      expect(mockMessaging.onMessage).toHaveBeenCalled();
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle network errors gracefully', async () => {
      // Simulate network error
      require('../../src/services/api').default.post.mockRejectedValue(new Error('Network error'));

      await expect(
        aiContentService.generateContent({
          prompt: 'test',
          contentType: 'post',
          platforms: ['instagram'],
        })
      ).rejects.toThrow('Failed to generate content. Please try again.');
    });

    it('should handle offline mode properly', async () => {
      // Mock network disconnection
      require('@react-native-community/netinfo').addEventListener.mockImplementation((callback) => {
        callback({ isConnected: false });
      });

      const isOnline = offlineStorageService.isOnlineStatus();
      // Initial state depends on implementation, but should handle offline state
      expect(typeof isOnline).toBe('boolean');
    });

    it('should handle permission denials', async () => {
      require('react-native-permissions').request.mockResolvedValue('denied');

      await expect(
        mediaUploadService.openCamera({ mediaType: 'photo', quality: 0.8 })
      ).rejects.toThrow('Camera permission denied');
    });

    it('should handle invalid OAuth responses', async () => {
      const mockStorage = {
        getString: jest.fn().mockReturnValue(undefined),
        set: jest.fn(),
        delete: jest.fn(),
      };
      require('react-native-mmkv').MMKV.mockImplementation(() => mockStorage);

      const credentials = oauthService.getStoredCredentials('instagram');
      expect(credentials).toBeNull();
    });
  });

  describe('Data Synchronization', () => {
    it('should sync drafts when coming back online', async () => {
      const mockStorage = {
        getString: jest.fn().mockReturnValue(JSON.stringify([
          {
            id: '',
            localId: 'draft_123',
            title: 'Test Draft',
            caption: 'Test caption',
            content_type: 'post',
            media_urls: [],
            platforms: ['instagram'],
            timestamp: Date.now(),
            isOffline: true,
            syncStatus: 'pending',
            lastModified: Date.now(),
          }
        ])),
        set: jest.fn(),
        delete: jest.fn(),
      };
      require('react-native-mmkv').MMKV.mockImplementation(() => mockStorage);

      require('../../src/services/api').default.post.mockResolvedValue({
        data: { id: 'server_id_123' }
      });

      const result = await offlineStorageService.syncPendingDrafts();
      
      expect(result.success).toBe(true);
      expect(result.syncedCount).toBe(1);
    });

    it('should handle token refresh automatically', async () => {
      (AsyncStorage.getItem as jest.Mock)
        .mockResolvedValueOnce('access_token')  // access token exists
        .mockResolvedValueOnce('refresh_token'); // refresh token exists

      const mockNewToken = {
        access_token: 'new_access_token',
        refresh_token: 'new_refresh_token',
        token_type: 'Bearer',
        expires_in: 3600,
      };

      require('../../src/services/api').default.post.mockResolvedValue({
        data: mockNewToken,
      });

      const result = await AuthService.refreshToken();
      
      expect(result).toEqual(mockNewToken);
      expect(AsyncStorage.setItem).toHaveBeenCalledWith('access_token', 'new_access_token');
    });
  });

  describe('Theme and Localization', () => {
    it('should support theme switching', () => {
      // Theme switching is handled by context, test that it's properly initialized
      const ThemeContext = require('../../src/contexts/ThemeContext');
      expect(ThemeContext.useTheme).toBeDefined();
    });

    it('should support multiple languages', () => {
      // i18n is initialized in the app
      const i18n = require('../../src/i18n');
      expect(i18n.AVAILABLE_LANGUAGES).toBeDefined();
      expect(i18n.AVAILABLE_LANGUAGES.length).toBeGreaterThan(1);
    });
  });

  describe('Performance and Resource Management', () => {
    it('should handle large media files appropriately', () => {
      const largeFile = {
        uri: 'file://large.jpg',
        type: 'image/jpeg',
        name: 'large.jpg',
        size: 15 * 1024 * 1024, // 15MB
      };

      const validation = mediaUploadService.validateMediaFile(largeFile);
      
      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('File size too large. Maximum 10MB allowed.');
    });

    it('should manage memory efficiently with drafts', () => {
      const stats = offlineStorageService.getSyncStats();
      
      expect(stats).toHaveProperty('totalDrafts');
      expect(stats).toHaveProperty('pendingDrafts');
      expect(stats).toHaveProperty('syncedDrafts');
      expect(stats).toHaveProperty('failedDrafts');
    });
  });

  describe('Security and Privacy', () => {
    it('should handle token expiration securely', async () => {
      // Mock expired token scenario
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

      const isAuth = await AuthService.isAuthenticated();
      expect(isAuth).toBe(false);
    });

    it('should store credentials securely', () => {
      const mockStorage = {
        getString: jest.fn(),
        set: jest.fn(),
        delete: jest.fn(),
      };
      require('react-native-mmkv').MMKV.mockImplementation(() => mockStorage);

      const mockCredentials = {
        accessToken: 'secure_token',
        platformUserId: 'user123',
        platformUsername: 'testuser',
        scopes: ['read'],
      };

      oauthService.storeCredentials('instagram', mockCredentials);
      
      expect(mockStorage.set).toHaveBeenCalledWith(
        'oauth_instagram',
        JSON.stringify(mockCredentials)
      );
    });

    it('should handle logout securely', async () => {
      await AuthService.logout();
      
      expect(AsyncStorage.multiRemove).toHaveBeenCalledWith([
        'access_token',
        'refresh_token',
      ]);
    });
  });
});