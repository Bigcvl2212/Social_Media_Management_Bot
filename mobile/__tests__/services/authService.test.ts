/**
 * Authentication Service Tests
 * Tests for user authentication, registration, and profile management
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import AuthService from '../../src/services/auth';
import apiClient from '../../src/services/api';
import { User, UserLogin, UserCreate, Token } from '../../src/types';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  multiSet: jest.fn(),
  multiRemove: jest.fn(),
}));

// Mock API client
jest.mock('../../src/services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
  },
  API_ENDPOINTS: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    PROFILE: '/users/me',
    UPDATE_PROFILE: '/users/me',
    REFRESH: '/auth/refresh',
  },
}));

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockCredentials: UserLogin = {
        email: 'test@example.com',
        password: 'password123',
      };

      const mockToken: Token = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'Bearer',
        expires_in: 3600,
      };

      const mockUser: User = {
        id: 'user123',
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User',
        avatar_url: 'https://example.com/avatar.jpg',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce({ data: mockToken });  // login response
      (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockUser });  // profile response

      const result = await AuthService.login(mockCredentials);

      expect(result.user).toEqual(mockUser);
      expect(result.token).toEqual(mockToken);

      // Verify form data submission
      expect(apiClient.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      );

      // Verify token storage
      expect(AsyncStorage.setItem).toHaveBeenCalledWith('access_token', 'access_token_123');
      expect(AsyncStorage.setItem).toHaveBeenCalledWith('refresh_token', 'refresh_token_123');

      // Verify profile fetch
      expect(apiClient.post).toHaveBeenCalledTimes(1);  // Only login call
      expect(apiClient.get).toHaveBeenCalledTimes(1);   // Profile fetch call
    });

    it('should handle login errors', async () => {
      const mockCredentials: UserLogin = {
        email: 'invalid@example.com',
        password: 'wrongpassword',
      };

      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

      await expect(AuthService.login(mockCredentials)).rejects.toThrow('Invalid credentials');
    });

    it('should handle profile fetch errors after successful login', async () => {
      const mockCredentials: UserLogin = {
        email: 'test@example.com',
        password: 'password123',
      };

      const mockToken: Token = {
        access_token: 'access_token_123',
        refresh_token: 'refresh_token_123',
        token_type: 'Bearer',
        expires_in: 3600,
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce({ data: mockToken });  // login succeeds
      (apiClient.get as jest.Mock).mockRejectedValueOnce(new Error('Profile fetch failed'));  // profile fails

      await expect(AuthService.login(mockCredentials)).rejects.toThrow('Profile fetch failed');
    });
  });

  describe('register', () => {
    it('should register new user successfully', async () => {
      const mockUserData: UserCreate = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
        full_name: 'New User',
      };

      const mockUser: User = {
        id: 'user456',
        username: 'newuser',
        email: 'newuser@example.com',
        full_name: 'New User',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockUser });

      const result = await AuthService.register(mockUserData);

      expect(result).toEqual(mockUser);
      expect(apiClient.post).toHaveBeenCalledWith('/auth/register', mockUserData);
    });

    it('should handle registration errors', async () => {
      const mockUserData: UserCreate = {
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'password123',
      };

      (apiClient.post as jest.Mock).mockRejectedValue(new Error('User already exists'));

      await expect(AuthService.register(mockUserData)).rejects.toThrow('User already exists');
    });
  });

  describe('getProfile', () => {
    it('should get user profile successfully', async () => {
      const mockUser: User = {
        id: 'user123',
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockUser });

      const result = await AuthService.getProfile();

      expect(result).toEqual(mockUser);
      expect(apiClient.get).toHaveBeenCalledWith('/users/me');
    });

    it('should handle profile fetch errors', async () => {
      (apiClient.get as jest.Mock).mockRejectedValue(new Error('Unauthorized'));

      await expect(AuthService.getProfile()).rejects.toThrow('Unauthorized');
    });
  });

  describe('updateProfile', () => {
    it('should update user profile successfully', async () => {
      const updateData = {
        full_name: 'Updated Name',
        avatar_url: 'https://example.com/new-avatar.jpg',
      };

      const mockUpdatedUser: User = {
        id: 'user123',
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Updated Name',
        avatar_url: 'https://example.com/new-avatar.jpg',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-02T00:00:00Z',
      };

      (apiClient.put as jest.Mock).mockResolvedValue({ data: mockUpdatedUser });

      const result = await AuthService.updateProfile(updateData);

      expect(result).toEqual(mockUpdatedUser);
      expect(apiClient.put).toHaveBeenCalledWith('/users/me', updateData);
    });

    it('should handle profile update errors', async () => {
      const updateData = { full_name: 'Invalid Update' };

      (apiClient.put as jest.Mock).mockRejectedValue(new Error('Update failed'));

      await expect(AuthService.updateProfile(updateData)).rejects.toThrow('Update failed');
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      await AuthService.logout();

      expect(AsyncStorage.multiRemove).toHaveBeenCalledWith([
        'access_token',
        'refresh_token',
      ]);
    });

    it('should handle logout errors gracefully', async () => {
      (AsyncStorage.multiRemove as jest.Mock).mockRejectedValue(new Error('Storage error'));

      // Should not throw
      await expect(AuthService.logout()).resolves.toBeUndefined();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when access token exists', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('access_token_123');

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(true);
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('access_token');
    });

    it('should return false when access token does not exist', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
    });

    it('should return false when storage access fails', async () => {
      (AsyncStorage.getItem as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.isAuthenticated();

      expect(result).toBe(false);
    });
  });

  describe('getAccessToken', () => {
    it('should return access token when it exists', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('access_token_123');

      const result = await AuthService.getAccessToken();

      expect(result).toBe('access_token_123');
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('access_token');
    });

    it('should return null when token does not exist', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);

      const result = await AuthService.getAccessToken();

      expect(result).toBeNull();
    });

    it('should return null when storage access fails', async () => {
      (AsyncStorage.getItem as jest.Mock).mockRejectedValue(new Error('Storage error'));

      const result = await AuthService.getAccessToken();

      expect(result).toBeNull();
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('refresh_token_123');

      const mockNewToken: Token = {
        access_token: 'new_access_token',
        refresh_token: 'new_refresh_token',
        token_type: 'Bearer',
        expires_in: 3600,
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockNewToken });

      const result = await AuthService.refreshToken();

      expect(result).toEqual(mockNewToken);
      expect(apiClient.post).toHaveBeenCalledWith('/auth/refresh', {
        refresh_token: 'refresh_token_123',
      });
      expect(AsyncStorage.setItem).toHaveBeenCalledWith('access_token', 'new_access_token');
      expect(AsyncStorage.setItem).toHaveBeenCalledWith('refresh_token', 'new_refresh_token');
    });

    it('should handle missing refresh token', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);
      (AsyncStorage.multiRemove as jest.Mock).mockResolvedValue(undefined); // Reset logout mock

      await expect(AuthService.refreshToken()).rejects.toThrow('No refresh token available');
    });

    it('should handle refresh token errors and logout', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('invalid_refresh_token');
      (AsyncStorage.multiRemove as jest.Mock).mockResolvedValue(undefined); // Reset logout mock
      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Invalid refresh token'));

      await expect(AuthService.refreshToken()).rejects.toThrow('Invalid refresh token');
      
      // Should call logout to clear invalid tokens
      expect(AsyncStorage.multiRemove).toHaveBeenCalledWith([
        'access_token',
        'refresh_token',
      ]);
    });
  });

  describe('token management', () => {
    it('should handle concurrent token refresh attempts', async () => {
      (AsyncStorage.getItem as jest.Mock).mockResolvedValue('refresh_token_123');

      const mockNewToken: Token = {
        access_token: 'new_access_token',
        refresh_token: 'new_refresh_token',
        token_type: 'Bearer',
        expires_in: 3600,
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockNewToken });

      // Simulate concurrent refresh attempts
      const refreshPromise1 = AuthService.refreshToken();
      const refreshPromise2 = AuthService.refreshToken();

      const [result1, result2] = await Promise.all([refreshPromise1, refreshPromise2]);

      // Both should succeed (though the second might be from cache/deduplication)
      expect(result1).toBeDefined();
      expect(result2).toBeDefined();
    });

    it('should handle storage errors during token operations', async () => {
      (AsyncStorage.getItem as jest.Mock).mockRejectedValue(new Error('Storage unavailable'));

      const result = await AuthService.getAccessToken();
      expect(result).toBeNull();

      const isAuth = await AuthService.isAuthenticated();
      expect(isAuth).toBe(false);
    });
  });

  describe('form data handling', () => {
    it('should properly format login form data', async () => {
      const mockCredentials: UserLogin = {
        email: 'test@example.com',
        password: 'password123',
      };

      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Test error'));

      try {
        await AuthService.login(mockCredentials);
      } catch (error) {
        // We expect this to fail, we're just testing the form data creation
      }

      const callArgs = (apiClient.post as jest.Mock).mock.calls[0];
      const [endpoint, formData, config] = callArgs;

      expect(endpoint).toBe('/auth/login');
      expect(formData).toBeInstanceOf(FormData);
      expect(config.headers['Content-Type']).toBe('multipart/form-data');
    });
  });
});