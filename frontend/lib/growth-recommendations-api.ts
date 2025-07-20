import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for Growth Recommendations
export interface GrowthRecommendation {
  id: number;
  recommendation_type: string;
  category: string;
  title: string;
  description: string;
  confidence_score: number;
  impact_score: number;
  difficulty_score: number;
  priority_score: number;
  recommendation_data: Record<string, unknown>;
  expected_outcomes?: Array<{
    metric: string;
    improvement: number;
  }>;
  actionable_steps?: Array<{
    step: number;
    action: string;
    estimated_time: string;
  }>;
  estimated_effort?: string;
  estimated_time?: string;
  is_urgent: boolean;
  created_at: string;
}

export interface RecommendationsDashboard {
  summary: {
    total_recommendations: number;
    urgent_recommendations: number;
    quick_wins: number;
    implemented_count: number;
    dismissed_count: number;
    completion_rate: number;
  };
  priority_breakdown: {
    high_priority: number;
    medium_priority: number;
    low_priority: number;
  };
  recommendations_by_type: {
    content: number;
    timing: number;
    hashtag: number;
    engagement: number;
    growth_strategy: number;
  };
  top_recommendations: GrowthRecommendation[];
  urgent_recommendations: GrowthRecommendation[];
  quick_wins: GrowthRecommendation[];
  recent_implementations: GrowthRecommendation[];
}

export interface ContentSuggestions {
  trending_topics: Array<{
    topic: string;
    relevance_score: number;
    estimated_engagement: string;
    hashtags: string[];
    content_formats: string[];
  }>;
  content_calendar_ideas: Array<{
    week: number;
    theme: string;
    posts: Array<{
      type: string;
      title: string;
      best_time: string;
    }>;
  }>;
  hashtag_strategies: Array<{
    strategy: string;
    description: string;
    example_set: string[];
    expected_reach: string;
  }>;
  posting_optimization: {
    optimal_times: Array<{
      day: string;
      time: string;
      engagement_boost: string;
    }>;
    frequency_recommendation: string;
    content_mix: Record<string, string>;
  };
}

export interface GrowthStrategy {
  current_stage: string;
  growth_pillars: Array<{
    pillar: string;
    current_score: number;
    target_score: number;
    actions: string[];
    priority: string;
  }>;
  "30_day_plan": Array<{
    week: number;
    focus: string;
    goals: string[];
    metrics: string[];
  }>;
  success_metrics: {
    primary: Array<{
      metric: string;
      current: string;
      target: string;
    }>;
    secondary: Array<{
      metric: string;
      current: string;
      target: string;
    }>;
  };
  recommendations: GrowthRecommendation[];
}

// Growth Recommendations API
export const growthRecommendationsApi = {
  // Get recommendations
  async getRecommendations(
    recommendationType?: string,
    status: string = 'active'
  ): Promise<GrowthRecommendation[]> {
    const response = await api.get('/analytics/recommendations/', {
      params: {
        recommendation_type: recommendationType,
        status,
      },
    });
    return response.data;
  },

  // Generate new recommendations
  async generateRecommendations(socialAccountId?: number): Promise<{
    recommendations: GrowthRecommendation[];
    count: number;
  }> {
    const response = await api.post('/analytics/recommendations/generate', null, {
      params: socialAccountId ? { social_account_id: socialAccountId } : {},
    });
    return response.data;
  },

  // Implement a recommendation
  async implementRecommendation(recommendationId: number, notes?: string): Promise<void> {
    await api.post(`/analytics/recommendations/${recommendationId}/implement`, {
      notes,
    });
  },

  // Dismiss a recommendation
  async dismissRecommendation(recommendationId: number): Promise<void> {
    await api.post(`/analytics/recommendations/${recommendationId}/dismiss`);
  },

  // Get recommendations dashboard
  async getRecommendationsDashboard(): Promise<RecommendationsDashboard> {
    const response = await api.get('/analytics/recommendations/dashboard');
    return response.data;
  },

  // Get content suggestions
  async getContentSuggestions(contentType?: string): Promise<ContentSuggestions> {
    const response = await api.get('/analytics/recommendations/content-suggestions', {
      params: contentType ? { content_type: contentType } : {},
    });
    return response.data;
  },

  // Get growth strategy
  async getGrowthStrategy(): Promise<GrowthStrategy> {
    const response = await api.get('/analytics/recommendations/growth-strategy');
    return response.data;
  },
};