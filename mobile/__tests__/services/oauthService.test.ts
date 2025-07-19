/**
 * OAuth Service Tests
 * Comprehensive tests for social media platform OAuth integration
 */

import { MMKV } from 'react-native-mmkv';
import oauthService from '../../../src/services/oauthService';
import { PlatformType } from '../../../src/types';

// Mock MMKV
jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    set: jest.fn(),
    delete: jest.fn(),
  })),
}));

// Mock React Native modules
jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
  Linking: {
    canOpenURL: jest.fn().mockResolvedValue(true),
    openURL: jest.fn().mockResolvedValue(true),
    addEventListener: jest.fn(),
    getInitialURL: jest.fn().mockResolvedValue(null),
  },
}));

// Mock API client
jest.mock('../../../src/services/api', () => ({
  post: jest.fn(),
  get: jest.fn(),
}));

describe('OAuthService', () => {
  let mockStorage: any;

  beforeEach(() => {
    jest.clearAllMocks();
    mockStorage = {
      getString: jest.fn(),
      set: jest.fn(),
      delete: jest.fn(),
    };
    (MMKV as jest.Mock).mockImplementation(() => mockStorage);
  });

  describe('getStoredCredentials', () => {
    it('should return null when no credentials are stored', () => {
      mockStorage.getString.mockReturnValue(undefined);
      
      const result = oauthService.getStoredCredentials('instagram');
      
      expect(result).toBeNull();
      expect(mockStorage.getString).toHaveBeenCalledWith('oauth_instagram');
    });

    it('should return parsed credentials when stored', () => {
      const mockCredentials = {
        accessToken: 'test_token',
        refreshToken: 'refresh_token',
        platformUserId: 'user123',
        platformUsername: 'testuser',
        scopes: ['read', 'write'],
      };
      
      mockStorage.getString.mockReturnValue(JSON.stringify(mockCredentials));
      
      const result = oauthService.getStoredCredentials('instagram');
      
      expect(result).toEqual(mockCredentials);
    });

    it('should handle JSON parse errors gracefully', () => {
      mockStorage.getString.mockReturnValue('invalid_json');
      
      const result = oauthService.getStoredCredentials('instagram');
      
      expect(result).toBeNull();
    });
  });

  describe('storeCredentials', () => {
    it('should store credentials as JSON string', () => {
      const mockCredentials = {
        accessToken: 'test_token',
        refreshToken: 'refresh_token',
        platformUserId: 'user123',
        platformUsername: 'testuser',
        scopes: ['read', 'write'],
      };

      oauthService.storeCredentials('instagram', mockCredentials);

      expect(mockStorage.set).toHaveBeenCalledWith(
        'oauth_instagram',
        JSON.stringify(mockCredentials)
      );
    });

    it('should throw error when storage fails', () => {
      mockStorage.set.mockImplementation(() => {
        throw new Error('Storage error');
      });

      const mockCredentials = {
        accessToken: 'test_token',
        platformUserId: 'user123',
        platformUsername: 'testuser',
        scopes: ['read'],
      };

      expect(() => {
        oauthService.storeCredentials('instagram', mockCredentials);
      }).toThrow('Failed to store instagram credentials');
    });
  });

  describe('isConnected', () => {
    it('should return false when no credentials exist', () => {
      mockStorage.getString.mockReturnValue(undefined);
      
      const result = oauthService.isConnected('instagram');
      
      expect(result).toBe(false);
    });

    it('should return false when token is expired', () => {
      const expiredCredentials = {
        accessToken: 'test_token',
        expiresAt: Date.now() - 1000, // Expired 1 second ago
        platformUserId: 'user123',
        platformUsername: 'testuser',
        scopes: ['read'],
      };
      
      mockStorage.getString.mockReturnValue(JSON.stringify(expiredCredentials));
      
      const result = oauthService.isConnected('instagram');
      
      expect(result).toBe(false);
    });

    it('should return true when credentials exist and not expired', () => {
      const validCredentials = {
        accessToken: 'test_token',
        expiresAt: Date.now() + 3600000, // Expires in 1 hour
        platformUserId: 'user123',
        platformUsername: 'testuser',
        scopes: ['read'],
      };
      
      mockStorage.getString.mockReturnValue(JSON.stringify(validCredentials));
      
      const result = oauthService.isConnected('instagram');
      
      expect(result).toBe(true);
    });
  });

  describe('getConnectedPlatforms', () => {
    it('should return array of connected platforms', () => {
      mockStorage.getString.mockImplementation((key: string) => {
        if (key === 'oauth_instagram' || key === 'oauth_facebook') {
          return JSON.stringify({
            accessToken: 'token',
            expiresAt: Date.now() + 3600000,
            platformUserId: 'user',
            platformUsername: 'user',
            scopes: ['read'],
          });
        }
        return undefined;
      });

      const result = oauthService.getConnectedPlatforms();
      
      expect(result).toEqual(['instagram', 'facebook']);
    });
  });

  describe('startOAuthFlow', () => {
    const { Linking } = require('react-native');

    it('should successfully start OAuth flow', async () => {
      Linking.canOpenURL.mockResolvedValue(true);
      Linking.openURL.mockResolvedValue(true);

      const result = await oauthService.startOAuthFlow('instagram');

      expect(result).toBe(true);
      expect(Linking.canOpenURL).toHaveBeenCalled();
      expect(Linking.openURL).toHaveBeenCalled();
    });

    it('should fail when URL cannot be opened', async () => {
      Linking.canOpenURL.mockResolvedValue(false);

      const result = await oauthService.startOAuthFlow('instagram');

      expect(result).toBe(false);
    });

    it('should handle errors gracefully', async () => {
      Linking.canOpenURL.mockRejectedValue(new Error('Network error'));

      const result = await oauthService.startOAuthFlow('instagram');

      expect(result).toBe(false);
    });
  });

  describe('removeCredentials', () => {
    it('should remove stored credentials', () => {
      oauthService.removeCredentials('instagram');

      expect(mockStorage.delete).toHaveBeenCalledWith('oauth_instagram');
    });

    it('should handle deletion errors gracefully', () => {
      mockStorage.delete.mockImplementation(() => {
        throw new Error('Delete error');
      });

      // Should not throw
      expect(() => {
        oauthService.removeCredentials('instagram');
      }).not.toThrow();
    });
  });

  describe('getPlatformConfig', () => {
    it('should return correct config for each platform', () => {
      const instagramConfig = oauthService.getPlatformConfig('instagram');
      
      expect(instagramConfig).toHaveProperty('name', 'Instagram');
      expect(instagramConfig).toHaveProperty('color', '#E4405F');
      expect(instagramConfig).toHaveProperty('scopes');
      expect(instagramConfig.scopes).toContain('user_profile');
    });

    it('should return configs for all platforms', () => {
      const platforms: PlatformType[] = ['instagram', 'facebook', 'twitter', 'linkedin', 'youtube', 'tiktok'];
      
      platforms.forEach(platform => {
        const config = oauthService.getPlatformConfig(platform);
        expect(config).toBeDefined();
        expect(config.name).toBeDefined();
        expect(config.color).toBeDefined();
        expect(config.scopes).toBeDefined();
      });
    });
  });
});