import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types for Audience Insights
export interface AudienceSegment {
  id: number;
  name: string;
  description?: string;
  segment_type: string;
  audience_size: number;
  percentage_of_total: number;
  avg_engagement_rate: number;
  most_active_hours?: Array<{
    hour: number;
    activity_score: number;
  }>;
  top_interests?: Array<{
    interest: string;
    score: number;
  }>;
  created_at: string;
}

export interface AudienceInsight {
  id: number;
  segment_id: number;
  insight_type: string;
  title: string;
  description?: string;
  confidence_score: number;
  impact_score: number;
  actionable: boolean;
  recommended_actions?: Array<{
    action: string;
    params?: Record<string, unknown>;
  }>;
  created_at: string;
}

export interface EngagementPattern {
  id: number;
  pattern_type: string;
  pattern_name: string;
  pattern_data: Record<string, unknown>;
  strength: number;
  avg_engagement_rate: number;
  confidence_level: number;
  trend_direction?: string;
}

export interface AudienceOverview {
  summary: {
    total_audience_size: number;
    total_segments: number;
    avg_engagement_rate: number;
    analysis_date: string;
  };
  top_segments: Array<{
    id: number;
    name: string;
    size: number;
    percentage: number;
    engagement_rate: number;
    segment_type: string;
  }>;
  demographics: {
    age_distribution: Array<{
      age_range: string;
      percentage: number;
    }>;
    gender_distribution: Array<{
      gender: string;
      percentage: number;
    }>;
    location_distribution: Array<{
      location: string;
      percentage: number;
    }>;
    interests: Array<{
      interest: string;
      score: number;
    }>;
  };
  engagement_patterns: EngagementPattern[];
  actionable_insights: Array<{
    type: string;
    title: string;
    description: string;
    actionable: boolean;
    recommended_action: string;
    impact_score: number;
    confidence_score: number;
  }>;
  recommendations: string[];
}

export interface AudienceDashboard {
  summary: {
    total_audience_size: number;
    total_segments: number;
    avg_engagement_rate: number;
    analysis_date: string;
  };
  top_segments: Array<{
    id: number;
    name: string;
    size: number;
    percentage: number;
    engagement_rate: number;
    segment_type: string;
  }>;
  demographics: {
    age_distribution: Array<{
      age_range: string;
      percentage: number;
    }>;
    gender_distribution: Array<{
      gender: string;
      percentage: number;
    }>;
    top_locations: Array<{
      location: string;
      percentage: number;
    }>;
    top_interests: Array<{
      interest: string;
      score: number;
    }>;
  };
  engagement_insights: {
    optimal_posting_times: Array<{
      hour: number;
      day: string;
      engagement_score: number;
    }>;
    content_preferences: Array<{
      content_type: string;
      preference_score: number;
      avg_engagement: number;
    }>;
    engagement_patterns: EngagementPattern[];
  };
  actionable_insights: Array<{
    type: string;
    title: string;
    description: string;
    actionable: boolean;
    recommended_action: string;
    impact_score: number;
    confidence_score: number;
  }>;
  recommendations: Array<{
    title: string;
    description: string;
    priority: string;
    estimated_impact: string;
  }>;
}

export interface DetailedDemographics {
  age_distribution: Array<{
    age_range: string;
    percentage: number;
  }>;
  gender_distribution: Array<{
    gender: string;
    percentage: number;
  }>;
  location_distribution: Array<{
    location: string;
    percentage: number;
  }>;
  interests: Array<{
    interest: string;
    score: number;
  }>;
  behavioral_insights: {
    most_active_hours: Array<{
      hour: number;
      percentage: number;
    }>;
    most_active_days: Array<{
      day: string;
      percentage: number;
    }>;
    device_usage: Array<{
      device: string;
      percentage: number;
    }>;
  };
  engagement_by_demographic: {
    age_engagement: Array<{
      age_range: string;
      avg_engagement_rate: number;
    }>;
    gender_engagement: Array<{
      gender: string;
      avg_engagement_rate: number;
    }>;
  };
}

export interface BehaviorAnalysis {
  analysis_period: string;
  content_interaction_patterns: {
    likes_pattern: {
      peak_hours: number[];
      peak_days: string[];
      average_response_time: string;
    };
    comments_pattern: {
      peak_hours: number[];
      peak_days: string[];
      average_response_time: string;
    };
    shares_pattern: {
      peak_hours: number[];
      peak_days: string[];
      average_response_time: string;
    };
  };
  content_preferences: {
    by_type: Array<{
      content_type: string;
      engagement_rate: number;
      completion_rate?: number;
      swipe_rate?: number;
      dwell_time?: string;
    }>;
    by_theme: Array<{
      theme: string;
      engagement_rate: number;
      save_rate?: number;
      share_rate?: number;
      comment_rate?: number;
    }>;
  };
  engagement_journey: {
    discovery_sources: Array<{
      source: string;
      percentage: number;
    }>;
    conversion_funnel: Array<{
      stage: string;
      rate: number;
    }>;
  };
  loyalty_metrics: {
    repeat_engagement_rate: number;
    average_session_duration: string;
    return_visitor_rate: number;
    brand_mention_frequency: number;
  };
}

// Audience Insights API
export const audienceInsightsApi = {
  // Get audience segments
  async getAudienceSegments(socialAccountId?: number): Promise<{ segments: AudienceSegment[] }> {
    const response = await api.get('/analytics/audience/segments', {
      params: socialAccountId ? { social_account_id: socialAccountId } : {},
    });
    return response.data;
  },

  // Get audience insights
  async getAudienceInsights(segmentId?: number): Promise<{ insights: AudienceInsight[] }> {
    const response = await api.get('/analytics/audience/insights', {
      params: segmentId ? { segment_id: segmentId } : {},
    });
    return response.data;
  },

  // Get engagement patterns
  async getEngagementPatterns(socialAccountId?: number): Promise<{ patterns: EngagementPattern[] }> {
    const response = await api.get('/analytics/audience/patterns', {
      params: socialAccountId ? { social_account_id: socialAccountId } : {},
    });
    return response.data;
  },

  // Get audience overview
  async getAudienceOverview(): Promise<AudienceOverview> {
    const response = await api.get('/analytics/audience/overview');
    return response.data;
  },

  // Get audience dashboard
  async getAudienceDashboard(): Promise<AudienceDashboard> {
    const response = await api.get('/analytics/audience/dashboard');
    return response.data;
  },

  // Get detailed demographics
  async getDetailedDemographics(socialAccountId?: number): Promise<DetailedDemographics> {
    const response = await api.get('/analytics/audience/demographics', {
      params: socialAccountId ? { social_account_id: socialAccountId } : {},
    });
    return response.data;
  },

  // Get behavior analysis
  async getBehaviorAnalysis(days: number = 30): Promise<BehaviorAnalysis> {
    const response = await api.get('/analytics/audience/behavior-analysis', {
      params: { days },
    });
    return response.data;
  },
};