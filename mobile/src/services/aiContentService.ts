/**
 * AI Content Generation Service
 * State-of-the-art AI services for viral content creation and social media management
 */

import apiClient from './api';
import { PlatformType, ContentType } from '../types';

export interface AIGenerateRequest {
  prompt: string;
  contentType: ContentType;
  platforms: PlatformType[];
  tone?: 'professional' | 'casual' | 'friendly' | 'humorous' | 'inspiring' | 'educational';
  length?: 'short' | 'medium' | 'long';
  includeHashtags?: boolean;
  includeEmojis?: boolean;
  language?: string;
  viralOptimization?: boolean;
}

export interface AIGenerateResponse {
  title: string;
  caption: string;
  hashtags: string[];
  suggestions: string[];
  viralScore?: number;
  engagementPrediction?: number;
}

export interface AIImageGenerateRequest {
  prompt: string;
  style?: 'realistic' | 'artistic' | 'cartoon' | 'minimalist' | 'vintage' | 'modern';
  aspectRatio?: '1:1' | '16:9' | '9:16' | '4:3' | '3:4';
  quality?: 'standard' | 'hd';
}

export interface AIImageGenerateResponse {
  imageUrl: string;
  prompt: string;
  style: string;
}

// Enhanced Video AI Editing Interfaces
export interface VideoEditRequest {
  videoUrl: string;
  editStyle: 'viral' | 'educational' | 'entertainment' | 'promotional' | 'storytelling';
  targetDuration?: number;
  targetPlatform: PlatformType[];
  viralElements?: boolean;
  musicSync?: boolean;
  addCaptions?: boolean;
  addEffects?: boolean;
}

export interface VideoEditResponse {
  editedVideoUrl: string;
  thumbnailUrl: string;
  editingReport: {
    cuts: number;
    effectsApplied: string[];
    viralScore: number;
    estimatedEngagement: number;
    recommendations: string[];
  };
  processingTime: number;
}

export interface AutonomousContentRequest {
  contentLibraryUrl: string;
  frequency: 'daily' | 'weekly' | 'bi-weekly';
  platforms: PlatformType[];
  contentTypes: ContentType[];
  brandGuidelines?: {
    tone: string;
    colors: string[];
    logo: string;
    restrictions: string[];
  };
}

export interface AutonomousContentResponse {
  contentPlan: {
    date: string;
    platform: PlatformType;
    contentType: ContentType;
    title: string;
    content: string;
    media: string[];
    scheduledTime: string;
    viralPotential: number;
  }[];
  nextUpdate: string;
  processingStatus: 'active' | 'pending' | 'error';
}

export interface SocialMonitoringRequest {
  platforms: PlatformType[];
  keywords?: string[];
  autoReply?: boolean;
  replyTone?: 'professional' | 'friendly' | 'humorous' | 'supportive';
  responseTime?: number; // in minutes
}

export interface SocialMonitoringResponse {
  interactions: {
    id: string;
    platform: PlatformType;
    type: 'comment' | 'message' | 'mention' | 'review';
    author: string;
    content: string;
    timestamp: string;
    sentiment: 'positive' | 'neutral' | 'negative';
    priority: 'high' | 'medium' | 'low';
    suggestedReply?: string;
    autoReplied?: boolean;
  }[];
  analytics: {
    totalInteractions: number;
    sentimentBreakdown: Record<string, number>;
    responseRate: number;
    avgResponseTime: number;
    engagementGrowth: number;
  };
}

export interface GrowthAnalysisResponse {
  overallScore: number;
  insights: {
    category: string;
    score: number;
    recommendations: string[];
    priority: 'critical' | 'high' | 'medium' | 'low';
  }[];
  competitorAnalysis: {
    competitor: string;
    comparison: string;
    opportunities: string[];
  }[];
  actionPlan: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  };
}

export interface ContentIdea {
  title: string;
  description: string;
  contentType: ContentType;
  platforms: PlatformType[];
  trending: boolean;
  engagement_score: number;
}

export interface TrendingTopics {
  topics: string[];
  hashtags: string[];
  platform: PlatformType;
  lastUpdated: string;
}

class AIContentService {
  /**
   * Generate content using AI
   */
  async generateContent(request: AIGenerateRequest): Promise<AIGenerateResponse> {
    try {
      const response = await apiClient.post('/ai/generate-content', request);
      return response.data;
    } catch (error) {
      console.error('Failed to generate AI content:', error);
      throw new Error('Failed to generate content. Please try again.');
    }
  }

  /**
   * Generate image using AI
   */
  async generateImage(request: AIImageGenerateRequest): Promise<AIImageGenerateResponse> {
    try {
      const response = await apiClient.post('/ai/generate-image', request);
      return response.data;
    } catch (error) {
      console.error('Failed to generate AI image:', error);
      throw new Error('Failed to generate image. Please try again.');
    }
  }

  /**
   * Get content ideas based on topic
   */
  async getContentIdeas(topic: string, platforms: PlatformType[] = []): Promise<ContentIdea[]> {
    try {
      const response = await apiClient.get('/ai/content-ideas', {
        params: { topic, platforms: platforms.join(',') }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get content ideas:', error);
      throw new Error('Failed to get content ideas. Please try again.');
    }
  }

  /**
   * Get trending topics for platforms
   */
  async getTrendingTopics(platforms: PlatformType[]): Promise<TrendingTopics[]> {
    try {
      const response = await apiClient.get('/ai/trending-topics', {
        params: { platforms: platforms.join(',') }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get trending topics:', error);
      throw new Error('Failed to get trending topics. Please try again.');
    }
  }

  /**
   * Improve existing content
   */
  async improveContent(
    content: string, 
    improvements: ('engagement' | 'clarity' | 'hashtags' | 'emojis' | 'call_to_action')[]
  ): Promise<AIGenerateResponse> {
    try {
      const response = await apiClient.post('/ai/improve-content', {
        content,
        improvements
      });
      return response.data;
    } catch (error) {
      console.error('Failed to improve content:', error);
      throw new Error('Failed to improve content. Please try again.');
    }
  }

  /**
   * Generate hashtags for content
   */
  async generateHashtags(content: string, platforms: PlatformType[], count: number = 10): Promise<string[]> {
    try {
      const response = await apiClient.post('/ai/generate-hashtags', {
        content,
        platforms,
        count
      });
      return response.data.hashtags;
    } catch (error) {
      console.error('Failed to generate hashtags:', error);
      throw new Error('Failed to generate hashtags. Please try again.');
    }
  }

  /**
   * Analyze content sentiment and engagement potential
   */
  async analyzeContent(content: string): Promise<{
    sentiment: 'positive' | 'neutral' | 'negative';
    engagement_score: number;
    readability_score: number;
    suggestions: string[];
  }> {
    try {
      const response = await apiClient.post('/ai/analyze-content', { content });
      return response.data;
    } catch (error) {
      console.error('Failed to analyze content:', error);
      throw new Error('Failed to analyze content. Please try again.');
    }
  }

  /**
   * Generate content calendar suggestions
   */
  async generateContentCalendar(
    days: number = 7,
    platforms: PlatformType[],
    topics: string[] = []
  ): Promise<{
    date: string;
    suggestions: ContentIdea[];
  }[]> {
    try {
      const response = await apiClient.post('/ai/content-calendar', {
        days,
        platforms,
        topics
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate content calendar:', error);
      throw new Error('Failed to generate content calendar. Please try again.');
    }
  }

  /**
   * Get optimal posting times based on AI analysis
   */
  async getOptimalPostingTimes(platforms: PlatformType[]): Promise<{
    platform: PlatformType;
    optimal_times: {
      day: string;
      hours: number[];
    }[];
    engagement_boost: number;
  }[]> {
    try {
      const response = await apiClient.get('/ai/optimal-posting-times', {
        params: { platforms: platforms.join(',') }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get optimal posting times:', error);
      throw new Error('Failed to get optimal posting times. Please try again.');
    }
  }

  /**
   * Generate content variations for A/B testing
   */
  async generateContentVariations(
    originalContent: string,
    variationCount: number = 3
  ): Promise<{
    original: string;
    variations: {
      content: string;
      changes: string[];
    }[];
  }> {
    try {
      const response = await apiClient.post('/ai/content-variations', {
        content: originalContent,
        count: variationCount
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate content variations:', error);
      throw new Error('Failed to generate content variations. Please try again.');
    }
  }

  /**
   * Get content template based on type and platform
   */
  async getContentTemplate(
    contentType: ContentType,
    platform: PlatformType,
    category?: string
  ): Promise<{
    template: string;
    placeholders: string[];
    tips: string[];
  }> {
    try {
      const response = await apiClient.get('/ai/content-template', {
        params: { content_type: contentType, platform, category }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get content template:', error);
      throw new Error('Failed to get content template. Please try again.');
    }
  }

  /**
   * Generate video script for content
   */
  async generateVideoScript(
    topic: string,
    duration: number, // in seconds
    style: 'educational' | 'entertaining' | 'promotional' | 'storytelling' = 'educational'
  ): Promise<{
    script: string;
    scenes: {
      timestamp: string;
      description: string;
      dialogue: string;
      visual_notes: string;
    }[];
    estimated_duration: number;
  }> {
    try {
      const response = await apiClient.post('/ai/generate-video-script', {
        topic,
        duration,
        style
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate video script:', error);
      throw new Error('Failed to generate video script. Please try again.');
    }
  }

  /**
   * Get personalized content recommendations
   */
  async getPersonalizedRecommendations(
    userInterests: string[],
    platforms: PlatformType[]
  ): Promise<ContentIdea[]> {
    try {
      const response = await apiClient.post('/ai/personalized-recommendations', {
        interests: userInterests,
        platforms
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get personalized recommendations:', error);
      throw new Error('Failed to get personalized recommendations. Please try again.');
    }
  }

  // ===== ADVANCED AI FEATURES =====
  
  /**
   * Advanced Video AI Editing for Viral Content
   * State-of-the-art video editing with human-level quality
   */
  async editVideoForViral(request: VideoEditRequest): Promise<VideoEditResponse> {
    try {
      const response = await apiClient.post('/ai/video-edit-viral', request);
      return response.data;
    } catch (error) {
      console.error('Failed to edit video for viral content:', error);
      throw new Error('Failed to edit video. Please try again.');
    }
  }

  /**
   * Autonomous Content Creation from User Content Library
   * Processes weekly updated content files to create new content
   */
  async setupAutonomousContent(request: AutonomousContentRequest): Promise<AutonomousContentResponse> {
    try {
      const response = await apiClient.post('/ai/autonomous-content-setup', request);
      return response.data;
    } catch (error) {
      console.error('Failed to setup autonomous content:', error);
      throw new Error('Failed to setup autonomous content creation. Please try again.');
    }
  }

  /**
   * Get Autonomous Content Status and Next Batch
   */
  async getAutonomousContentStatus(): Promise<AutonomousContentResponse> {
    try {
      const response = await apiClient.get('/ai/autonomous-content-status');
      return response.data;
    } catch (error) {
      console.error('Failed to get autonomous content status:', error);
      throw new Error('Failed to get autonomous content status. Please try again.');
    }
  }

  /**
   * Social Media Monitoring and Autonomous Interaction
   */
  async setupSocialMonitoring(request: SocialMonitoringRequest): Promise<{ success: boolean; monitoringId: string }> {
    try {
      const response = await apiClient.post('/ai/social-monitoring-setup', request);
      return response.data;
    } catch (error) {
      console.error('Failed to setup social monitoring:', error);
      throw new Error('Failed to setup social monitoring. Please try again.');
    }
  }

  /**
   * Get Social Media Interactions and Analytics
   */
  async getSocialMonitoring(): Promise<SocialMonitoringResponse> {
    try {
      const response = await apiClient.get('/ai/social-monitoring');
      return response.data;
    } catch (error) {
      console.error('Failed to get social monitoring data:', error);
      throw new Error('Failed to get social monitoring data. Please try again.');
    }
  }

  /**
   * Reply to Social Media Interaction
   */
  async replyToInteraction(interactionId: string, reply: string, auto: boolean = false): Promise<{ success: boolean }> {
    try {
      const response = await apiClient.post('/ai/social-reply', {
        interactionId,
        reply,
        auto
      });
      return response.data;
    } catch (error) {
      console.error('Failed to reply to interaction:', error);
      throw new Error('Failed to send reply. Please try again.');
    }
  }

  /**
   * Comprehensive Growth Analysis and Recommendations
   */
  async getGrowthAnalysis(): Promise<GrowthAnalysisResponse> {
    try {
      const response = await apiClient.get('/ai/growth-analysis');
      return response.data;
    } catch (error) {
      console.error('Failed to get growth analysis:', error);
      throw new Error('Failed to get growth analysis. Please try again.');
    }
  }

  /**
   * AI-Powered Multi-Format Content Creation
   * Creates content across video, picture, graphic, post, forum formats
   */
  async createMultiFormatContent(
    topic: string,
    formats: ('video' | 'image' | 'graphic' | 'post' | 'forum')[],
    platforms: PlatformType[],
    viralOptimization: boolean = true
  ): Promise<{
    video?: { url: string; thumbnail: string; duration: number };
    image?: { url: string; alt: string };
    graphic?: { url: string; type: string };
    post?: { title: string; content: string; hashtags: string[] };
    forum?: { title: string; content: string; category: string };
    viralScore: number;
  }> {
    try {
      const response = await apiClient.post('/ai/multi-format-content', {
        topic,
        formats,
        platforms,
        viralOptimization
      });
      return response.data;
    } catch (error) {
      console.error('Failed to create multi-format content:', error);
      throw new Error('Failed to create multi-format content. Please try again.');
    }
  }

  /**
   * Batch Process User Content Library for Autonomous Creation
   */
  async processContentLibrary(libraryPath: string): Promise<{
    processedFiles: number;
    contentGenerated: number;
    nextProcessing: string;
    insights: string[];
  }> {
    try {
      const response = await apiClient.post('/ai/process-content-library', {
        libraryPath
      });
      return response.data;
    } catch (error) {
      console.error('Failed to process content library:', error);
      throw new Error('Failed to process content library. Please try again.');
    }
  }

  /**
   * Real-time Viral Content Optimization
   */
  async optimizeForViral(
    content: string,
    contentType: ContentType,
    platform: PlatformType
  ): Promise<{
    optimizedContent: string;
    viralScore: number;
    improvements: string[];
    hashtags: string[];
    postingTime: string;
  }> {
    try {
      const response = await apiClient.post('/ai/viral-optimization', {
        content,
        contentType,
        platform
      });
      return response.data;
    } catch (error) {
      console.error('Failed to optimize content for viral:', error);
      throw new Error('Failed to optimize content. Please try again.');
    }
  }
}
}

// Export singleton instance
export const aiContentService = new AIContentService();
export default aiContentService;

