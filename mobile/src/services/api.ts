/**
 * API client configuration for Social Media Management Bot
 * Connects to FastAPI backend endpoints
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API configuration
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://your-production-api.com/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token } = response.data;
          await AsyncStorage.setItem('access_token', access_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        await AsyncStorage.multiRemove(['access_token', 'refresh_token']);
        // TODO: Navigate to login screen
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH: '/auth/refresh',
  
  // Users
  PROFILE: '/users/me',
  UPDATE_PROFILE: '/users/me',
  
  // Social Accounts
  SOCIAL_ACCOUNTS: '/social-accounts',
  LINK_ACCOUNT: '/social-accounts/link',
  UNLINK_ACCOUNT: '/social-accounts/unlink',
  
  // Content
  CONTENT: '/content',
  SCHEDULE_POST: '/content/schedule',
  POSTS: '/content/posts',
  
  // Analytics
  ANALYTICS: '/analytics',
  DASHBOARD_DATA: '/analytics/dashboard',
  
  // Upload
  UPLOAD: '/upload',
  UPLOAD_MEDIA: '/upload/media',
} as const;