import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export enum SocialPlatform {
  INSTAGRAM = 'instagram',
  TIKTOK = 'tiktok',
  YOUTUBE = 'youtube',
  TWITTER = 'twitter',
  FACEBOOK = 'facebook',
  LINKEDIN = 'linkedin',
}

export enum AccountStatus {
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected',
  ERROR = 'error',
  PENDING = 'pending',
  EXPIRED = 'expired',
}

export interface SocialAccount {
  id: string;
  platform: SocialPlatform;
  username: string;
  display_name?: string;
  profile_picture?: string;
  status: AccountStatus;
  followers_count?: number;
  posts_count?: number;
  engagement_rate?: number;
  last_sync?: string;
  access_token?: string;
  refresh_token?: string;
  token_expires_at?: string;
  permissions?: string[];
  account_settings?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PlatformInfo {
  platform: SocialPlatform;
  name: string;
  description: string;
  icon_url?: string;
  color: string;
  features: string[];
  oauth_scopes: string[];
  is_available: boolean;
  connection_url?: string;
}

// Alias for backwards compatibility
export type Platform = PlatformInfo;

export interface ConnectionResult {
  success: boolean;
  account?: SocialAccount;
  message?: string;
  auth_url?: string;
}

export interface SyncResult {
  success: boolean;
  updated_fields?: string[];
  message?: string;
  last_sync?: string;
}

export interface AccountStats {
  total_accounts: number;
  connected_accounts: number;
  by_platform: Record<SocialPlatform, number>;
  by_status: Record<AccountStatus, number>;
  total_followers: number;
  total_posts: number;
  average_engagement: number;
}

// API functions
export const socialAccountsApi = {
  // Get all social accounts
  async getAccounts(): Promise<{ accounts: SocialAccount[]; total: number }> {
    try {
      const response = await api.get('/social-accounts');
      return response.data;
    } catch (error) {
      console.error('Error fetching social accounts:', error);
      return { accounts: [], total: 0 };
    }
  },

  // Get account by ID
  async getAccountById(id: string): Promise<SocialAccount | null> {
    try {
      const response = await api.get(`/social-accounts/${id}`);
      return response.data.account;
    } catch (error) {
      console.error('Error fetching account by ID:', error);
      return null;
    }
  },

  // Get accounts by platform
  async getAccountsByPlatform(platform: SocialPlatform): Promise<SocialAccount[]> {
    try {
      const response = await api.get('/social-accounts', {
        params: { platform },
      });
      return response.data.accounts || [];
    } catch (error) {
      console.error(`Error fetching ${platform} accounts:`, error);
      return [];
    }
  },

  // Get available platforms
  async getPlatforms(): Promise<PlatformInfo[]> {
    try {
      const response = await api.get('/social-accounts/platforms');
      return response.data.platforms || [];
    } catch (error) {
      console.error('Error fetching platforms:', error);
      return [];
    }
  },

  // Start OAuth connection
  async startConnection(platform: SocialPlatform): Promise<ConnectionResult> {
    try {
      const response = await api.post(`/social-accounts/connect/${platform}/start`);
      return response.data;
    } catch (error) {
      console.error(`Error starting ${platform} connection:`, error);
      return { success: false, message: `Failed to start ${platform} connection` };
    }
  },

  // Complete OAuth connection
  async completeConnection(platform: SocialPlatform, code: string, state?: string): Promise<ConnectionResult> {
    try {
      const response = await api.post(`/social-accounts/connect/${platform}/complete`, {
        code,
        state,
      });
      return response.data;
    } catch (error) {
      console.error(`Error completing ${platform} connection:`, error);
      return { success: false, message: `Failed to complete ${platform} connection` };
    }
  },

  // Disconnect account
  async disconnectAccount(id: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await api.delete(`/social-accounts/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error disconnecting account:', error);
      return { success: false, message: 'Failed to disconnect account' };
    }
  },

  // Sync account data
  async syncAccount(id: string): Promise<SyncResult> {
    try {
      const response = await api.post(`/social-accounts/${id}/sync`);
      return response.data;
    } catch (error) {
      console.error('Error syncing account:', error);
      return { success: false, message: 'Failed to sync account' };
    }
  },

  // Sync all accounts
  async syncAllAccounts(): Promise<{ 
    success: boolean; 
    results: { [accountId: string]: SyncResult }; 
    message?: string 
  }> {
    try {
      const response = await api.post('/social-accounts/sync-all');
      return response.data;
    } catch (error) {
      console.error('Error syncing all accounts:', error);
      return { success: false, results: {}, message: 'Failed to sync accounts' };
    }
  },

  // Update account settings
  async updateAccountSettings(id: string, settings: Record<string, unknown>): Promise<{ 
    success: boolean; 
    account?: SocialAccount; 
    message?: string 
  }> {
    try {
      const response = await api.put(`/social-accounts/${id}/settings`, settings);
      return response.data;
    } catch (error) {
      console.error('Error updating account settings:', error);
      return { success: false, message: 'Failed to update account settings' };
    }
  },

  // Refresh access token
  async refreshToken(id: string): Promise<{ 
    success: boolean; 
    token_expires_at?: string; 
    message?: string 
  }> {
    try {
      const response = await api.post(`/social-accounts/${id}/refresh-token`);
      return response.data;
    } catch (error) {
      console.error('Error refreshing token:', error);
      return { success: false, message: 'Failed to refresh token' };
    }
  },

  // Get account statistics
  async getAccountStats(): Promise<AccountStats> {
    try {
      const response = await api.get('/social-accounts/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching account stats:', error);
      return {
        total_accounts: 0,
        connected_accounts: 0,
        by_platform: {} as Record<SocialPlatform, number>,
        by_status: {} as Record<AccountStatus, number>,
        total_followers: 0,
        total_posts: 0,
        average_engagement: 0,
      };
    }
  },

  // Test account connection
  async testConnection(id: string): Promise<{ 
    success: boolean; 
    status: AccountStatus; 
    message?: string 
  }> {
    try {
      const response = await api.post(`/social-accounts/${id}/test`);
      return response.data;
    } catch (error) {
      console.error('Error testing connection:', error);
      return { success: false, status: AccountStatus.ERROR, message: 'Failed to test connection' };
    }
  },

  // Get account permissions
  async getAccountPermissions(id: string): Promise<{ 
    permissions: string[]; 
    missing_permissions: string[]; 
    requires_reauth: boolean 
  }> {
    try {
      const response = await api.get(`/social-accounts/${id}/permissions`);
      return response.data;
    } catch (error) {
      console.error('Error fetching account permissions:', error);
      return { permissions: [], missing_permissions: [], requires_reauth: false };
    }
  },

  // Start OAuth connection (alias for startConnection)
  async startOAuth(platform: SocialPlatform): Promise<ConnectionResult> {
    return this.startConnection(platform);
  },

  // Get account statistics (alias for getAccountStats) 
  async getStats(): Promise<AccountStats> {
    return this.getAccountStats();
  },

  // Update account (alias for updateAccountSettings)
  async updateAccount(id: string, data: Record<string, unknown>): Promise<{
    success: boolean;
    account?: SocialAccount;
    message?: string;
  }> {
    return this.updateAccountSettings(id, data);
  },

  // Reauthorize account
  async reauthorizeAccount(id: string): Promise<ConnectionResult> {
    try {
      const response = await api.post(`/social-accounts/${id}/reauthorize`);
      return response.data;
    } catch (error) {
      console.error('Error reauthorizing account:', error);
      return { success: false, message: 'Failed to reauthorize account' };
    }
  },
};