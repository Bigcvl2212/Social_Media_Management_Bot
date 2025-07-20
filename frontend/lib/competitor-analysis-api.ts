import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for Competitor Analysis
export interface Competitor {
  id: number;
  platform: string;
  username: string;
  display_name?: string;
  follower_count: number;
  following_count: number;
  post_count: number;
  is_active: boolean;
  created_at: string;
  last_analyzed?: string;
}

export interface CompetitorAnalytics {
  competitor_id: number;
  follower_count: number;
  following_count: number;
  post_count: number;
  avg_likes: number;
  avg_comments: number;
  avg_shares: number;
  engagement_rate: number;
  follower_growth: number;
  posting_frequency: number;
  popular_hashtags?: Array<{
    hashtag: string;
    count: number;
    engagement: number;
  }>;
  content_themes?: Array<{
    theme: string;
    percentage: number;
  }>;
  recorded_at: string;
  data_date: string;
}

export interface CompetitorInsights {
  competitor: {
    id: number;
    username: string;
    platform: string;
    follower_count: number;
    engagement_rate: number;
    posting_frequency: number;
  };
  insights: Array<{
    type: string;
    title: string;
    description: string;
    actionable: boolean;
    recommendation: string;
  }>;
  recommendations: string[];
  analytics_summary: {
    data_points: number;
    latest_update?: string;
  };
}

export interface CompetitorTrends {
  total_competitors: number;
  platform_distribution: Record<string, number>;
  growth_leaders: Array<{
    competitor_id: number;
    username: string;
    platform: string;
    follower_growth: number;
    engagement_rate: number;
  }>;
  engagement_leaders: Array<{
    competitor_id: number;
    username: string;
    platform: string;
    avg_engagement_rate: number;
  }>;
  trending_hashtags: Array<{
    hashtag: string;
    usage_count: number;
    avg_engagement: number;
  }>;
  optimal_posting_times: Array<{
    hour: number;
    day: string;
    avg_engagement: number;
  }>;
  content_themes: Array<{
    theme: string;
    percentage: number;
    avg_engagement: number;
  }>;
  analysis_period: {
    start_date: string;
    end_date: string;
    days: number;
  };
}

export interface CompetitorDashboard {
  summary: {
    total_competitors: number;
    active_competitors: number;
    platforms_tracked: number;
    last_updated?: string;
  };
  top_performer?: {
    competitor_id: number;
    username: string;
    platform: string;
    avg_engagement_rate: number;
  };
  platform_distribution: Record<string, number>;
  trending_hashtags: Array<{
    hashtag: string;
    usage_count: number;
    avg_engagement: number;
  }>;
  growth_opportunities: Array<{
    title: string;
    description: string;
    action: string;
  }>;
}

// Competitor Analysis API
export const competitorAnalysisApi = {
  // Add a new competitor
  async addCompetitor(platform: string, username: string, display_name?: string): Promise<Competitor> {
    const response = await api.post('/analytics/competitors/competitors', {
      platform,
      username,
      display_name,
    });
    return response.data;
  },

  // Get all competitors
  async getCompetitors(): Promise<Competitor[]> {
    const response = await api.get('/analytics/competitors/competitors');
    return response.data;
  },

  // Get competitor analytics
  async getCompetitorAnalytics(competitorId: number, days: number = 30): Promise<CompetitorAnalytics[]> {
    const response = await api.get(`/analytics/competitors/competitors/${competitorId}/analytics`, {
      params: { days },
    });
    return response.data;
  },

  // Get competitor insights
  async getCompetitorInsights(competitorId: number): Promise<CompetitorInsights> {
    const response = await api.get(`/analytics/competitors/competitors/${competitorId}/insights`);
    return response.data;
  },

  // Get competitor trends
  async getCompetitorTrends(days: number = 30): Promise<CompetitorTrends> {
    const response = await api.get('/analytics/competitors/trends', {
      params: { days },
    });
    return response.data;
  },

  // Get competitor dashboard
  async getCompetitorDashboard(): Promise<CompetitorDashboard> {
    const response = await api.get('/analytics/competitors/dashboard');
    return response.data;
  },

  // Remove a competitor
  async removeCompetitor(competitorId: number): Promise<void> {
    await api.delete(`/analytics/competitors/competitors/${competitorId}`);
  },
};