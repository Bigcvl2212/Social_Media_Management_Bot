/**
 * Autonomous Content Creation Service
 * AI that creates content from user's content library with weekly updates
 */

import apiClient from './api';
import { PlatformType, ContentType } from '../types';

export interface ContentLibraryFile {
  id: string;
  filename: string;
  type: 'video' | 'image' | 'audio' | 'document' | 'text';
  size: number;
  uploadDate: string;
  lastProcessed?: string;
  metadata: {
    duration?: number;
    dimensions?: { width: number; height: number };
    tags: string[];
    description?: string;
    quality: 'high' | 'medium' | 'low';
  };
  contentExtracted: {
    topics: string[];
    keyMoments?: { timestamp: number; description: string; importance: number }[];
    transcript?: string;
    visualElements?: string[];
    brandElements?: string[];
  };
}

export interface AutonomousContentConfig {
  libraryPath: string;
  updateFrequency: 'daily' | 'weekly' | 'bi-weekly' | 'monthly';
  platforms: PlatformType[];
  contentTypes: ContentType[];
  postsPerWeek: number;
  brandGuidelines: {
    tone: string;
    style: string;
    colors: string[];
    logoUrl?: string;
    tagline?: string;
    restrictions: string[];
    mustInclude: string[];
  };
  targetAudience: {
    demographics: string[];
    interests: string[];
    behaviorPatterns: string[];
  };
  qualityStandards: {
    minViralScore: number;
    requireHumanReview: boolean;
    autoPublish: boolean;
  };
}

export interface GeneratedContent {
  id: string;
  sourceFiles: string[];
  platform: PlatformType;
  contentType: ContentType;
  generatedAt: string;
  scheduledFor?: string;
  status: 'draft' | 'pending_review' | 'approved' | 'published' | 'rejected';
  content: {
    title: string;
    body: string;
    hashtags: string[];
    media: {
      type: 'image' | 'video' | 'gif' | 'carousel';
      url: string;
      thumbnail?: string;
      alt?: string;
      duration?: number;
    }[];
    callToAction?: string;
  };
  analytics: {
    viralScore: number;
    engagementPrediction: number;
    bestPostingTime: string;
    targetReach: number;
    confidenceLevel: number;
  };
  aiInsights: {
    creationReasoning: string;
    sourceAnalysis: string;
    optimizations: string[];
    alternatives: string[];
  };
  humanFeedback?: {
    approved: boolean;
    notes: string;
    modifications: string[];
    rating: number; // 1-5
  };
}

export interface AutonomousStats {
  totalContentGenerated: number;
  publishedContent: number;
  averageViralScore: number;
  totalEngagement: number;
  libraryUtilization: number; // percentage of library content used
  successRate: number; // approved vs generated ratio
  lastLibraryUpdate: string;
  nextScheduledGeneration: string;
  performanceMetrics: {
    topPerformingContentTypes: string[];
    bestPerformingPlatforms: PlatformType[];
    averageProductionTime: number; // minutes
    contentApprovalRate: number;
  };
}

export interface ContentSuggestion {
  id: string;
  type: 'trend_based' | 'anniversary' | 'seasonal' | 'user_generated' | 'repurpose';
  title: string;
  description: string;
  suggestedPlatforms: PlatformType[];
  urgency: 'high' | 'medium' | 'low';
  potentialViralScore: number;
  requiredAssets: string[];
  estimatedCreationTime: number; // minutes
  similarSuccessfulContent?: {
    title: string;
    engagement: number;
    platform: PlatformType;
  }[];
}

class AutonomousContentService {
  private isProcessing = false;
  private config?: AutonomousContentConfig;

  /**
   * Setup autonomous content creation system
   */
  async setupAutonomousCreation(config: AutonomousContentConfig): Promise<{ 
    success: boolean; 
    systemId: string;
    initialAnalysis: {
      libraryFiles: number;
      readyToProcess: number;
      estimatedFirstBatch: string;
    };
  }> {
    try {
      const response = await apiClient.post('/autonomous/setup', config);
      this.config = config;
      return response.data;
    } catch (error) {
      console.error('Failed to setup autonomous content creation:', error);
      throw new Error('Failed to setup autonomous content creation. Please try again.');
    }
  }

  /**
   * Process content library for new material
   */
  async processContentLibrary(
    forceUpdate = false
  ): Promise<{
    processedFiles: ContentLibraryFile[];
    newContent: GeneratedContent[];
    insights: string[];
    nextProcessing: string;
  }> {
    try {
      this.isProcessing = true;
      const response = await apiClient.post('/autonomous/process-library', {
        forceUpdate
      });
      this.isProcessing = false;
      return response.data;
    } catch (error) {
      this.isProcessing = false;
      console.error('Failed to process content library:', error);
      throw new Error('Failed to process content library. Please try again.');
    }
  }

  /**
   * Get generated content queue
   */
  async getGeneratedContent(
    status?: GeneratedContent['status'],
    limit = 50,
    offset = 0
  ): Promise<{
    content: GeneratedContent[];
    total: number;
    hasMore: boolean;
  }> {
    try {
      const response = await apiClient.get('/autonomous/generated-content', {
        params: { status, limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get generated content:', error);
      throw new Error('Failed to get generated content. Please try again.');
    }
  }

  /**
   * Review and approve/reject generated content
   */
  async reviewContent(
    contentId: string,
    decision: 'approve' | 'reject' | 'request_changes',
    feedback?: {
      notes: string;
      modifications: string[];
      rating: number;
    }
  ): Promise<{ success: boolean; updatedContent?: GeneratedContent }> {
    try {
      const response = await apiClient.post('/autonomous/review-content', {
        contentId,
        decision,
        feedback
      });
      return response.data;
    } catch (error) {
      console.error('Failed to review content:', error);
      throw new Error('Failed to review content. Please try again.');
    }
  }

  /**
   * Request specific content generation
   */
  async generateSpecificContent(
    prompt: string,
    sourceFiles: string[],
    platforms: PlatformType[],
    contentType: ContentType,
    urgency: 'high' | 'medium' | 'low' = 'medium'
  ): Promise<GeneratedContent> {
    try {
      const response = await apiClient.post('/autonomous/generate-specific', {
        prompt,
        sourceFiles,
        platforms,
        contentType,
        urgency
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate specific content:', error);
      throw new Error('Failed to generate content. Please try again.');
    }
  }

  /**
   * Get content library status
   */
  async getLibraryStatus(): Promise<{
    totalFiles: number;
    processedFiles: number;
    lastUpdate: string;
    availableFiles: ContentLibraryFile[];
    processingQueue: number;
    storageUsed: number; // in MB
    recommendations: string[];
  }> {
    try {
      const response = await apiClient.get('/autonomous/library-status');
      return response.data;
    } catch (error) {
      console.error('Failed to get library status:', error);
      throw new Error('Failed to get library status. Please try again.');
    }
  }

  /**
   * Upload new files to content library
   */
  async uploadToLibrary(
    files: File[],
    metadata?: {
      tags: string[];
      description: string;
      priority: 'high' | 'medium' | 'low';
    }
  ): Promise<{
    uploaded: ContentLibraryFile[];
    failed: { filename: string; error: string }[];
    processingStarted: boolean;
  }> {
    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`files[${index}]`, file);
      });
      
      if (metadata) {
        formData.append('metadata', JSON.stringify(metadata));
      }

      const response = await apiClient.post('/autonomous/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to upload to library:', error);
      throw new Error('Failed to upload files. Please try again.');
    }
  }

  /**
   * Get autonomous content statistics
   */
  async getStats(timeframe: '7d' | '30d' | '90d' | 'all' = '30d'): Promise<AutonomousStats> {
    try {
      const response = await apiClient.get('/autonomous/stats', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get autonomous stats:', error);
      throw new Error('Failed to get statistics. Please try again.');
    }
  }

  /**
   * Get content suggestions based on trends and library
   */
  async getContentSuggestions(limit = 10): Promise<ContentSuggestion[]> {
    try {
      const response = await apiClient.get('/autonomous/suggestions', {
        params: { limit }
      });
      return response.data.suggestions;
    } catch (error) {
      console.error('Failed to get content suggestions:', error);
      throw new Error('Failed to get suggestions. Please try again.');
    }
  }

  /**
   * Schedule content for automatic posting
   */
  async scheduleContent(
    contentId: string,
    scheduledTime: string,
    platforms: PlatformType[]
  ): Promise<{ success: boolean; scheduledIds: string[] }> {
    try {
      const response = await apiClient.post('/autonomous/schedule', {
        contentId,
        scheduledTime,
        platforms
      });
      return response.data;
    } catch (error) {
      console.error('Failed to schedule content:', error);
      throw new Error('Failed to schedule content. Please try again.');
    }
  }

  /**
   * Update autonomous content configuration
   */
  async updateConfiguration(updates: Partial<AutonomousContentConfig>): Promise<{ success: boolean }> {
    try {
      const response = await apiClient.put('/autonomous/config', updates);
      if (updates) {
        this.config = { ...this.config, ...updates } as AutonomousContentConfig;
      }
      return response.data;
    } catch (error) {
      console.error('Failed to update configuration:', error);
      throw new Error('Failed to update configuration. Please try again.');
    }
  }

  /**
   * Get configuration
   */
  getConfiguration(): AutonomousContentConfig | undefined {
    return this.config;
  }

  /**
   * Check if system is currently processing
   */
  isCurrentlyProcessing(): boolean {
    return this.isProcessing;
  }

  /**
   * Force content generation from specific library files
   */
  async forceGeneration(
    fileIds: string[],
    targetCount: number,
    platforms: PlatformType[]
  ): Promise<{
    generated: GeneratedContent[];
    processingTime: number;
    insights: string[];
  }> {
    try {
      const response = await apiClient.post('/autonomous/force-generate', {
        fileIds,
        targetCount,
        platforms
      });
      return response.data;
    } catch (error) {
      console.error('Failed to force generation:', error);
      throw new Error('Failed to generate content. Please try again.');
    }
  }

  /**
   * Analyze content performance and update AI model
   */
  async updateAIModel(
    performanceData: {
      contentId: string;
      actualEngagement: number;
      userFeedback: string;
      performanceRating: number;
    }[]
  ): Promise<{ success: boolean; modelVersion: string; improvements: string[] }> {
    try {
      const response = await apiClient.post('/autonomous/update-model', {
        performanceData
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update AI model:', error);
      throw new Error('Failed to update AI model. Please try again.');
    }
  }
}

// Export singleton instance
export const autonomousContentService = new AutonomousContentService();
export default autonomousContentService;