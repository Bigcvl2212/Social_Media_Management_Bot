/**
 * Social Media Monitoring and Autonomous Interaction Service
 * Advanced AI-powered social media management with human-level interaction
 */

import apiClient from './api';
import { PlatformType } from '../types';

export interface MonitoringConfiguration {
  platforms: PlatformType[];
  keywords: string[];
  autoReplyEnabled: boolean;
  replyTone: 'professional' | 'friendly' | 'humorous' | 'supportive' | 'brand_voice';
  responseTimeMinutes: number;
  businessHours?: {
    start: string; // "09:00"
    end: string;   // "17:00"
    timezone: string;
  };
  escalationKeywords: string[];
  priorityUsers: string[];
}

export interface SocialInteraction {
  id: string;
  platform: PlatformType;
  type: 'comment' | 'message' | 'mention' | 'review' | 'share';
  author: {
    username: string;
    displayName: string;
    followers: number;
    isVerified: boolean;
    influence_score: number;
  };
  content: string;
  timestamp: string;
  postUrl?: string;
  sentiment: 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative';
  priority: 'critical' | 'high' | 'medium' | 'low';
  context: {
    originalPost?: string;
    conversationHistory?: string[];
    relatedInteractions?: string[];
  };
  aiAnalysis: {
    intent: string;
    emotion: string;
    topics: string[];
    requiresResponse: boolean;
    urgency: number; // 1-10
    suggestedActions: string[];
  };
  suggestedReply?: string;
  autoReplied: boolean;
  replied: boolean;
  replyContent?: string;
  replyTimestamp?: string;
}

export interface EngagementAnalytics {
  totalInteractions: number;
  responseRate: number;
  avgResponseTime: number; // in minutes
  sentimentTrend: {
    date: string;
    positive: number;
    neutral: number;
    negative: number;
  }[];
  engagementGrowth: {
    comments: number;
    messages: number;
    mentions: number;
    shares: number;
    totalGrowth: number;
  };
  topInteractors: {
    username: string;
    interactions: number;
    sentiment: string;
    influence: number;
  }[];
  performanceMetrics: {
    autoReplySuccess: number;
    escalationRate: number;
    satisfactionScore: number;
    conversionRate: number;
  };
}

export interface GrowthInsights {
  overallGrowthScore: number;
  insights: {
    category: 'content' | 'engagement' | 'timing' | 'audience' | 'competition';
    title: string;
    description: string;
    impact: 'high' | 'medium' | 'low';
    effort: 'easy' | 'moderate' | 'complex';
    recommendations: string[];
    estimatedGrowth: string;
  }[];
  competitorAnalysis: {
    competitor: string;
    platform: PlatformType;
    theirAdvantages: string[];
    opportunities: string[];
    benchmarkMetrics: Record<string, number>;
  }[];
  contentOptimization: {
    bestPerformingTypes: string[];
    optimalPostingTimes: Record<PlatformType, string[]>;
    hashtagRecommendations: Record<PlatformType, string[]>;
    audiencePreferences: string[];
  };
  actionPlan: {
    immediate: { task: string; priority: number; estimatedImpact: string }[];
    thisWeek: { task: string; priority: number; estimatedImpact: string }[];
    thisMonth: { task: string; priority: number; estimatedImpact: string }[];
  };
}

class SocialMonitoringService {
  private monitoringActive = false;
  private pollingInterval?: NodeJS.Timeout;

  /**
   * Setup and activate social media monitoring
   */
  async setupMonitoring(config: MonitoringConfiguration): Promise<{ success: boolean; monitoringId: string }> {
    try {
      const response = await apiClient.post('/monitoring/setup', config);
      this.monitoringActive = true;
      this.startPolling();
      return response.data;
    } catch (error) {
      console.error('Failed to setup monitoring:', error);
      throw new Error('Failed to setup social media monitoring. Please try again.');
    }
  }

  /**
   * Get all pending social media interactions
   */
  async getInteractions(limit = 50, offset = 0): Promise<{
    interactions: SocialInteraction[];
    total: number;
    hasMore: boolean;
  }> {
    try {
      const response = await apiClient.get('/monitoring/interactions', {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get interactions:', error);
      throw new Error('Failed to get interactions. Please try again.');
    }
  }

  /**
   * Get real-time analytics and engagement metrics
   */
  async getAnalytics(timeframe: '1h' | '24h' | '7d' | '30d' = '24h'): Promise<EngagementAnalytics> {
    try {
      const response = await apiClient.get('/monitoring/analytics', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get analytics:', error);
      throw new Error('Failed to get analytics. Please try again.');
    }
  }

  /**
   * Reply to a specific interaction (manual or AI-generated)
   */
  async replyToInteraction(
    interactionId: string, 
    reply: string, 
    useAI = false
  ): Promise<{ success: boolean; replyId: string }> {
    try {
      const response = await apiClient.post('/monitoring/reply', {
        interactionId,
        reply,
        useAI
      });
      return response.data;
    } catch (error) {
      console.error('Failed to reply to interaction:', error);
      throw new Error('Failed to send reply. Please try again.');
    }
  }

  /**
   * Generate AI reply for interaction
   */
  async generateAIReply(
    interactionId: string,
    customTone?: string
  ): Promise<{ suggestedReply: string; confidence: number; alternatives: string[] }> {
    try {
      const response = await apiClient.post('/monitoring/generate-reply', {
        interactionId,
        customTone
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate AI reply:', error);
      throw new Error('Failed to generate reply. Please try again.');
    }
  }

  /**
   * Bulk process interactions with AI
   */
  async bulkProcessInteractions(
    interactionIds: string[],
    action: 'auto_reply' | 'mark_read' | 'escalate' | 'ignore'
  ): Promise<{ processed: number; failed: number; results: Record<string, boolean> }> {
    try {
      const response = await apiClient.post('/monitoring/bulk-process', {
        interactionIds,
        action
      });
      return response.data;
    } catch (error) {
      console.error('Failed to bulk process interactions:', error);
      throw new Error('Failed to process interactions. Please try again.');
    }
  }

  /**
   * Get comprehensive growth insights and recommendations
   */
  async getGrowthInsights(): Promise<GrowthInsights> {
    try {
      const response = await apiClient.get('/monitoring/growth-insights');
      return response.data;
    } catch (error) {
      console.error('Failed to get growth insights:', error);
      throw new Error('Failed to get growth insights. Please try again.');
    }
  }

  /**
   * Update monitoring configuration
   */
  async updateConfiguration(config: Partial<MonitoringConfiguration>): Promise<{ success: boolean }> {
    try {
      const response = await apiClient.put('/monitoring/config', config);
      return response.data;
    } catch (error) {
      console.error('Failed to update configuration:', error);
      throw new Error('Failed to update monitoring configuration. Please try again.');
    }
  }

  /**
   * Get monitoring status and health
   */
  async getMonitoringStatus(): Promise<{
    active: boolean;
    lastUpdate: string;
    platforms: Record<PlatformType, { connected: boolean; lastSync: string; errors?: string[] }>;
    queueSize: number;
    processedToday: number;
  }> {
    try {
      const response = await apiClient.get('/monitoring/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get monitoring status:', error);
      throw new Error('Failed to get monitoring status. Please try again.');
    }
  }

  /**
   * Train AI on brand voice and response style
   */
  async trainBrandVoice(
    examples: { situation: string; response: string; tone: string }[],
    brandGuidelines: string
  ): Promise<{ success: boolean; modelId: string }> {
    try {
      const response = await apiClient.post('/monitoring/train-voice', {
        examples,
        brandGuidelines
      });
      return response.data;
    } catch (error) {
      console.error('Failed to train brand voice:', error);
      throw new Error('Failed to train brand voice. Please try again.');
    }
  }

  /**
   * Export interaction data for analysis
   */
  async exportData(
    format: 'csv' | 'json' | 'xlsx',
    timeframe: '7d' | '30d' | '90d',
    includeAnalytics = true
  ): Promise<{ downloadUrl: string; expiresAt: string }> {
    try {
      const response = await apiClient.post('/monitoring/export', {
        format,
        timeframe,
        includeAnalytics
      });
      return response.data;
    } catch (error) {
      console.error('Failed to export data:', error);
      throw new Error('Failed to export data. Please try again.');
    }
  }

  /**
   * Start real-time polling for new interactions
   */
  private startPolling(intervalMs = 30000) {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }

    this.pollingInterval = setInterval(async () => {
      try {
        await this.checkForNewInteractions();
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, intervalMs);
  }

  /**
   * Check for new interactions (internal)
   */
  private async checkForNewInteractions(): Promise<void> {
    try {
      const response = await apiClient.get('/monitoring/new-interactions');
      const newInteractions = response.data.interactions;
      
      if (newInteractions.length > 0) {
        // Emit event or trigger callback for new interactions
        console.log(`Found ${newInteractions.length} new interactions`);
      }
    } catch (error) {
      console.error('Failed to check for new interactions:', error);
    }
  }

  /**
   * Stop monitoring and cleanup
   */
  async stopMonitoring(): Promise<void> {
    try {
      await apiClient.post('/monitoring/stop');
      this.monitoringActive = false;
      
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = undefined;
      }
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
      throw new Error('Failed to stop monitoring. Please try again.');
    }
  }

  /**
   * Get service status
   */
  isActive(): boolean {
    return this.monitoringActive;
  }
}

// Export singleton instance
export const socialMonitoringService = new SocialMonitoringService();
export default socialMonitoringService;