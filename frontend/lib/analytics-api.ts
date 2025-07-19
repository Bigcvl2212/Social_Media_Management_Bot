import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface AnalyticsMetric {
  name: string;
  value: number;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
}

export interface PlatformMetrics {
  platform: string;
  followers: number;
  engagement: number;
  posts: number;
  reach: number;
  impressions: number;
}

export interface ContentPerformance {
  id: string;
  title: string;
  platform: string;
  content_type: string;
  published_at: string;
  likes: number;
  comments: number;
  shares: number;
  views: number;
  engagement_rate: number;
}

export interface AnalyticsDashboard {
  overview: {
    total_followers: AnalyticsMetric;
    total_engagement: AnalyticsMetric;
    total_posts: AnalyticsMetric;
    total_reach: AnalyticsMetric;
  };
  platform_metrics: PlatformMetrics[];
  top_content: ContentPerformance[];
  engagement_trend: {
    date: string;
    value: number;
  }[];
  follower_growth: {
    date: string;
    value: number;
  }[];
}

export interface AnalyticsResponse {
  success: boolean;
  data: AnalyticsDashboard;
  message?: string;
}

export interface PlatformAnalytics {
  platform: string;
  metrics: {
    followers: {
      current: number;
      growth: number;
      growth_rate: number;
    };
    engagement: {
      rate: number;
      total: number;
      average_per_post: number;
    };
    content: {
      total_posts: number;
      recent_posts: number;
      top_performing: ContentPerformance[];
    };
    reach: {
      total: number;
      average: number;
      impressions: number;
    };
  };
  trends: {
    followers: { date: string; value: number }[];
    engagement: { date: string; value: number }[];
    posts: { date: string; value: number }[];
  };
}

// API functions
export const analyticsApi = {
  // Dashboard analytics
  async getDashboard(): Promise<AnalyticsDashboard> {
    try {
      const response = await api.get('/analytics/dashboard');
      return response.data.data;
    } catch (error) {
      console.error('Error fetching analytics dashboard:', error);
      return {
        overview: {
          total_followers: { name: 'Total Followers', value: 0, change: 0, changeType: 'neutral' },
          total_engagement: { name: 'Total Engagement', value: 0, change: 0, changeType: 'neutral' },
          total_posts: { name: 'Total Posts', value: 0, change: 0, changeType: 'neutral' },
          total_reach: { name: 'Total Reach', value: 0, change: 0, changeType: 'neutral' },
        },
        platform_metrics: [],
        top_content: [],
        engagement_trend: [],
        follower_growth: [],
      };
    }
  },

  // Overall analytics
  async getAnalytics(timeframe?: '7d' | '30d' | '90d' | '1y'): Promise<AnalyticsResponse> {
    try {
      const response = await api.get('/analytics', {
        params: { timeframe: timeframe || '30d' },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      return {
        success: false,
        data: {
          overview: {
            total_followers: { name: 'Total Followers', value: 0, change: 0, changeType: 'neutral' },
            total_engagement: { name: 'Total Engagement', value: 0, change: 0, changeType: 'neutral' },
            total_posts: { name: 'Total Posts', value: 0, change: 0, changeType: 'neutral' },
            total_reach: { name: 'Total Reach', value: 0, change: 0, changeType: 'neutral' },
          },
          platform_metrics: [],
          top_content: [],
          engagement_trend: [],
          follower_growth: [],
        },
        message: 'Failed to fetch analytics',
      };
    }
  },

  // Platform-specific analytics
  async getPlatformAnalytics(platform: string, timeframe?: '7d' | '30d' | '90d' | '1y'): Promise<PlatformAnalytics | null> {
    try {
      const response = await api.get(`/analytics/platforms/${platform}`, {
        params: { timeframe: timeframe || '30d' },
      });
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching analytics for ${platform}:`, error);
      return null;
    }
  },

  // Content performance
  async getContentPerformance(params?: {
    platform?: string;
    content_type?: string;
    limit?: number;
    sort_by?: 'engagement_rate' | 'likes' | 'views' | 'published_at';
    order?: 'asc' | 'desc';
  }): Promise<ContentPerformance[]> {
    try {
      const response = await api.get('/analytics/content-performance', { params });
      return response.data.data || [];
    } catch (error) {
      console.error('Error fetching content performance:', error);
      return [];
    }
  },

  // Engagement metrics
  async getEngagementMetrics(timeframe?: '7d' | '30d' | '90d' | '1y'): Promise<{
    total_engagement: number;
    engagement_rate: number;
    trend: { date: string; value: number }[];
  }> {
    try {
      const response = await api.get('/analytics/engagement', {
        params: { timeframe: timeframe || '30d' },
      });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching engagement metrics:', error);
      return {
        total_engagement: 0,
        engagement_rate: 0,
        trend: [],
      };
    }
  },

  // Follower growth
  async getFollowerGrowth(timeframe?: '7d' | '30d' | '90d' | '1y'): Promise<{
    total_followers: number;
    growth: number;
    growth_rate: number;
    trend: { date: string; value: number }[];
  }> {
    try {
      const response = await api.get('/analytics/followers', {
        params: { timeframe: timeframe || '30d' },
      });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching follower growth:', error);
      return {
        total_followers: 0,
        growth: 0,
        growth_rate: 0,
        trend: [],
      };
    }
  },

  // Platform comparison
  async getPlatformComparison(metrics: string[] = ['followers', 'engagement', 'reach']): Promise<{
    platforms: string[];
    metrics: {
      [key: string]: {
        platform: string;
        value: number;
        change: number;
      }[];
    };
  }> {
    try {
      const response = await api.get('/analytics/platform-comparison', {
        params: { metrics: metrics.join(',') },
      });
      return response.data.data;
    } catch (error) {
      console.error('Error fetching platform comparison:', error);
      return {
        platforms: [],
        metrics: {},
      };
    }
  },

  // Export analytics data
  async exportAnalytics(format: 'csv' | 'json' = 'csv', timeframe?: '7d' | '30d' | '90d' | '1y'): Promise<Blob | null> {
    try {
      const response = await api.get('/analytics/export', {
        params: { format, timeframe: timeframe || '30d' },
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting analytics:', error);
      return null;
    }
  },
};