/**
 * OAuth Service for Social Media Platform Integration
 * Handles OAuth flows for Instagram, TikTok, YouTube, Twitter/X, Facebook, LinkedIn
 */

import { Alert, Linking } from 'react-native';
import { MMKV } from 'react-native-mmkv';
import apiClient from './api';
import { PlatformType } from '../types';

export interface OAuthCredentials {
  accessToken: string;
  refreshToken?: string;
  expiresAt?: number;
  platformUserId: string;
  platformUsername: string;
  scopes: string[];
}

export interface PlatformConfig {
  authUrl: string;
  clientId: string;
  redirectUri: string;
  scopes: string[];
  name: string;
  color: string;
}

const storage = new MMKV();

// Platform configurations
const PLATFORM_CONFIGS: Record<PlatformType, PlatformConfig> = {
  instagram: {
    authUrl: 'https://api.instagram.com/oauth/authorize',
    clientId: process.env.INSTAGRAM_CLIENT_ID || 'demo_client_id',
    redirectUri: 'socialmediabot://oauth/instagram',
    scopes: ['user_profile', 'user_media'],
    name: 'Instagram',
    color: '#E4405F',
  },
  facebook: {
    authUrl: 'https://www.facebook.com/v18.0/dialog/oauth',
    clientId: process.env.FACEBOOK_CLIENT_ID || 'demo_client_id',
    redirectUri: 'socialmediabot://oauth/facebook',
    scopes: ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list'],
    name: 'Facebook',
    color: '#1877F2',
  },
  twitter: {
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    clientId: process.env.TWITTER_CLIENT_ID || 'demo_client_id',
    redirectUri: 'socialmediabot://oauth/twitter',
    scopes: ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
    name: 'Twitter/X',
    color: '#1DA1F2',
  },
  linkedin: {
    authUrl: 'https://www.linkedin.com/oauth/v2/authorization',
    clientId: process.env.LINKEDIN_CLIENT_ID || 'demo_client_id',
    redirectUri: 'socialmediabot://oauth/linkedin',
    scopes: ['w_member_social', 'r_liteprofile', 'r_emailaddress'],
    name: 'LinkedIn',
    color: '#0A66C2',
  },
  youtube: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    clientId: process.env.GOOGLE_CLIENT_ID || 'demo_client_id',
    redirectUri: 'socialmediabot://oauth/youtube',
    scopes: ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.readonly'],
    name: 'YouTube',
    color: '#FF0000',
  },
  tiktok: {
    authUrl: 'https://www.tiktok.com/auth/authorize/',
    clientId: process.env.TIKTOK_CLIENT_ID || 'demo_client_id',
    redirectUri: 'socialmediabot://oauth/tiktok',
    scopes: ['user.info.basic', 'video.upload', 'video.list'],
    name: 'TikTok',
    color: '#000000',
  },
};

class OAuthService {
  private getStorageKey(platform: PlatformType): string {
    return `oauth_${platform}`;
  }

  /**
   * Get stored credentials for a platform
   */
  getStoredCredentials(platform: PlatformType): OAuthCredentials | null {
    try {
      const stored = storage.getString(this.getStorageKey(platform));
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error(`Error getting credentials for ${platform}:`, error);
      return null;
    }
  }

  /**
   * Store OAuth credentials securely
   */
  storeCredentials(platform: PlatformType, credentials: OAuthCredentials): void {
    try {
      storage.set(this.getStorageKey(platform), JSON.stringify(credentials));
    } catch (error) {
      console.error(`Error storing credentials for ${platform}:`, error);
      throw new Error(`Failed to store ${platform} credentials`);
    }
  }

  /**
   * Remove stored credentials
   */
  removeCredentials(platform: PlatformType): void {
    try {
      storage.delete(this.getStorageKey(platform));
    } catch (error) {
      console.error(`Error removing credentials for ${platform}:`, error);
    }
  }

  /**
   * Check if platform is connected
   */
  isConnected(platform: PlatformType): boolean {
    const credentials = this.getStoredCredentials(platform);
    if (!credentials) return false;

    // Check if token is expired
    if (credentials.expiresAt && credentials.expiresAt < Date.now()) {
      return false;
    }

    return true;
  }

  /**
   * Get all connected platforms
   */
  getConnectedPlatforms(): PlatformType[] {
    const platforms: PlatformType[] = [];
    for (const platform of Object.keys(PLATFORM_CONFIGS) as PlatformType[]) {
      if (this.isConnected(platform)) {
        platforms.push(platform);
      }
    }
    return platforms;
  }

  /**
   * Build OAuth authorization URL
   */
  private buildAuthUrl(platform: PlatformType): string {
    const config = PLATFORM_CONFIGS[platform];
    const params = new URLSearchParams({
      client_id: config.clientId,
      redirect_uri: config.redirectUri,
      scope: config.scopes.join(' '),
      response_type: 'code',
      state: this.generateState(platform),
    });

    // Platform-specific parameters
    if (platform === 'twitter') {
      params.append('code_challenge', 'challenge');
      params.append('code_challenge_method', 'plain');
    }

    return `${config.authUrl}?${params.toString()}`;
  }

  /**
   * Generate a state parameter for OAuth security
   */
  private generateState(platform: PlatformType): string {
    const state = `${platform}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    storage.set(`oauth_state_${platform}`, state);
    return state;
  }

  /**
   * Verify OAuth state parameter
   */
  private verifyState(platform: PlatformType, receivedState: string): boolean {
    const storedState = storage.getString(`oauth_state_${platform}`);
    storage.delete(`oauth_state_${platform}`);
    return storedState === receivedState;
  }

  /**
   * Initiate OAuth flow for a platform
   */
  async startOAuthFlow(platform: PlatformType): Promise<boolean> {
    try {
      const authUrl = this.buildAuthUrl(platform);
      const canOpen = await Linking.canOpenURL(authUrl);
      
      if (!canOpen) {
        throw new Error('Cannot open OAuth URL');
      }

      await Linking.openURL(authUrl);
      return true;
    } catch (error) {
      console.error(`OAuth flow failed for ${platform}:`, error);
      Alert.alert(
        'Authentication Error',
        `Failed to start ${PLATFORM_CONFIGS[platform].name} authentication. Please try again.`
      );
      return false;
    }
  }

  /**
   * Handle OAuth callback with authorization code
   */
  async handleOAuthCallback(platform: PlatformType, code: string, state: string): Promise<boolean> {
    try {
      // Verify state parameter
      if (!this.verifyState(platform, state)) {
        throw new Error('Invalid state parameter');
      }

      // Exchange code for access token
      const response = await apiClient.post('/auth/oauth/exchange', {
        platform,
        code,
        redirect_uri: PLATFORM_CONFIGS[platform].redirectUri,
      });

      const credentials: OAuthCredentials = {
        accessToken: response.data.access_token,
        refreshToken: response.data.refresh_token,
        expiresAt: response.data.expires_in ? Date.now() + (response.data.expires_in * 1000) : undefined,
        platformUserId: response.data.user_id,
        platformUsername: response.data.username,
        scopes: PLATFORM_CONFIGS[platform].scopes,
      };

      // Store credentials
      this.storeCredentials(platform, credentials);

      Alert.alert(
        'Success!',
        `Successfully connected ${PLATFORM_CONFIGS[platform].name} account.`
      );

      return true;
    } catch (error) {
      console.error(`OAuth callback failed for ${platform}:`, error);
      Alert.alert(
        'Authentication Error',
        `Failed to connect ${PLATFORM_CONFIGS[platform].name} account. Please try again.`
      );
      return false;
    }
  }

  /**
   * Refresh access token if possible
   */
  async refreshToken(platform: PlatformType): Promise<boolean> {
    try {
      const credentials = this.getStoredCredentials(platform);
      if (!credentials?.refreshToken) {
        return false;
      }

      const response = await apiClient.post('/auth/oauth/refresh', {
        platform,
        refresh_token: credentials.refreshToken,
      });

      const updatedCredentials: OAuthCredentials = {
        ...credentials,
        accessToken: response.data.access_token,
        expiresAt: response.data.expires_in ? Date.now() + (response.data.expires_in * 1000) : undefined,
      };

      this.storeCredentials(platform, updatedCredentials);
      return true;
    } catch (error) {
      console.error(`Token refresh failed for ${platform}:`, error);
      // Remove invalid credentials
      this.removeCredentials(platform);
      return false;
    }
  }

  /**
   * Disconnect a platform
   */
  async disconnectPlatform(platform: PlatformType): Promise<boolean> {
    try {
      const credentials = this.getStoredCredentials(platform);
      if (credentials) {
        // Revoke token on server
        await apiClient.post('/auth/oauth/revoke', {
          platform,
          access_token: credentials.accessToken,
        });
      }

      // Remove local credentials
      this.removeCredentials(platform);
      
      Alert.alert(
        'Disconnected',
        `${PLATFORM_CONFIGS[platform].name} account has been disconnected.`
      );
      
      return true;
    } catch (error) {
      console.error(`Disconnect failed for ${platform}:`, error);
      // Still remove local credentials even if server call fails
      this.removeCredentials(platform);
      return false;
    }
  }

  /**
   * Get platform configuration
   */
  getPlatformConfig(platform: PlatformType): PlatformConfig {
    return PLATFORM_CONFIGS[platform];
  }

  /**
   * Get all platform configurations
   */
  getAllPlatformConfigs(): Record<PlatformType, PlatformConfig> {
    return PLATFORM_CONFIGS;
  }

  /**
   * Test API connection for a platform
   */
  async testConnection(platform: PlatformType): Promise<boolean> {
    try {
      const credentials = this.getStoredCredentials(platform);
      if (!credentials) return false;

      const response = await apiClient.get(`/platforms/${platform}/test`, {
        headers: {
          Authorization: `Bearer ${credentials.accessToken}`,
        },
      });

      return response.status === 200;
    } catch (error) {
      console.error(`Connection test failed for ${platform}:`, error);
      return false;
    }
  }
}

export default new OAuthService();