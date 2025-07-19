/**
 * Authentication service for Social Media Management Bot
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, UserLogin, UserCreate, Token } from '../types';
import apiClient, { API_ENDPOINTS } from './api';

class AuthService {
  /**
   * Log in user with email and password
   */
  async login(credentials: UserLogin): Promise<{ user: User; token: Token }> {
    try {
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await apiClient.post(API_ENDPOINTS.LOGIN, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const token: Token = response.data;
      
      // Store tokens
      await AsyncStorage.setItem('access_token', token.access_token);
      await AsyncStorage.setItem('refresh_token', token.refresh_token);
      
      // Get user profile
      const user = await this.getProfile();
      
      return { user, token };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Register new user
   */
  async register(userData: UserCreate): Promise<User> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.REGISTER, userData);
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PROFILE);
      return response.data;
    } catch (error) {
      console.error('Get profile error:', error);
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(userData: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.put(API_ENDPOINTS.UPDATE_PROFILE, userData);
      return response.data;
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  }

  /**
   * Log out user
   */
  async logout(): Promise<void> {
    try {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
    } catch (error) {
      console.error('Logout error:', error);
      // Don't throw - logout should always succeed to clear app state
    }
  }

  /**
   * Check if user is authenticated
   */
  async isAuthenticated(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem('access_token');
      return !!token;
    } catch (error) {
      console.error('Auth check error:', error);
      return false;
    }
  }

  /**
   * Get stored access token
   */
  async getAccessToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('access_token');
    } catch (error) {
      console.error('Get token error:', error);
      return null;
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<Token> {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post(API_ENDPOINTS.REFRESH, {
        refresh_token: refreshToken,
      });

      const token: Token = response.data;
      await AsyncStorage.setItem('access_token', token.access_token);
      await AsyncStorage.setItem('refresh_token', token.refresh_token);

      return token;
    } catch (error) {
      console.error('Token refresh error:', error);
      await this.logout();
      throw error;
    }
  }
}

export default new AuthService();