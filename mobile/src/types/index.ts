/**
 * TypeScript type definitions for Social Media Management Bot
 * Based on backend Pydantic schemas
 */

// User types
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Social Account types
export type PlatformType = 'instagram' | 'tiktok' | 'youtube' | 'twitter' | 'facebook' | 'linkedin';

export interface SocialAccount {
  id: string;
  user_id: string;
  platform: PlatformType;
  account_name: string;
  account_id: string;
  access_token: string;
  is_active: boolean;
  last_sync: string;
  created_at: string;
}

export interface SocialAccountLink {
  platform: PlatformType;
  access_token: string;
  account_name: string;
  account_id: string;
}

// Content types
export type ContentType = 'post' | 'story' | 'reel' | 'video';
export type PostStatus = 'draft' | 'scheduled' | 'published' | 'failed';

export interface Content {
  id: string;
  user_id: string;
  title: string;
  caption: string;
  content_type: ContentType;
  media_urls: string[];
  platforms: PlatformType[];
  scheduled_time?: string;
  status: PostStatus;
  created_at: string;
  updated_at: string;
}

export interface ContentCreate {
  title: string;
  caption: string;
  content_type: ContentType;
  media_urls: string[];
  platforms: PlatformType[];
  scheduled_time?: string;
}

// Analytics types
export interface AnalyticsData {
  platform: PlatformType;
  followers: number;
  following: number;
  posts: number;
  engagement_rate: number;
  reach: number;
  impressions: number;
  date: string;
}

export interface DashboardData {
  total_followers: number;
  total_posts: number;
  avg_engagement_rate: number;
  platforms_count: number;
  recent_posts: Content[];
  analytics_summary: AnalyticsData[];
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// Navigation types
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  Profile: undefined;
  SocialAccounts: undefined;
  LinkAccount: { platform: PlatformType };
  ContentCalendar: undefined;
  CreatePost: undefined;
  EditPost: { postId: string };
  Analytics: undefined;
  Settings: undefined;
};

export type MainTabParamList = {
  Dashboard: undefined;
  Calendar: undefined;
  Create: undefined;
  Analytics: undefined;
  Profile: undefined;
};

// Form types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName?: string;
}

export interface PostForm {
  title: string;
  caption: string;
  contentType: ContentType;
  platforms: PlatformType[];
  scheduledTime?: Date;
  mediaFiles: string[];
}