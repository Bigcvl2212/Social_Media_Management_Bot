/**

 * AI Content Generation Service
 * Integrates with backend AI services for content creation
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
}

export interface AIGenerateResponse {
  title: string;
  caption: string;
  hashtags: string[];
  suggestions: string[];
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
}

// Export singleton instance
export const aiContentService = new AIContentService();
export default aiContentService;

