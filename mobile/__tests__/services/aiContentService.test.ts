/**
 * AI Content Service Tests
 * Tests for AI-powered content generation and optimization
 */

import aiContentService from '../../src/services/aiContentService';
import apiClient from '../../src/services/api';
import { PlatformType, ContentType } from '../../src/types';

// Mock API client
jest.mock('../../src/services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
  },
}));

describe('AIContentService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('generateContent', () => {
    it('should generate content successfully', async () => {
      const mockResponse = {
        title: 'AI Generated Title',
        caption: 'AI generated caption with hashtags',
        hashtags: ['#ai', '#content', '#socialmedia'],
        suggestions: ['Add more emojis', 'Include call-to-action'],
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockResponse });

      const request = {
        prompt: 'Create a post about AI technology',
        contentType: 'post' as ContentType,
        platforms: ['instagram' as PlatformType],
        tone: 'professional' as const,
        length: 'medium' as const,
        includeHashtags: true,
        includeEmojis: false,
        language: 'en',
      };

      const result = await aiContentService.generateContent(request);

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/generate-content', request);
    });

    it('should handle generation errors', async () => {
      (apiClient.post as jest.Mock).mockRejectedValue(new Error('API Error'));

      const request = {
        prompt: 'Test prompt',
        contentType: 'post' as ContentType,
        platforms: ['instagram' as PlatformType],
      };

      await expect(aiContentService.generateContent(request))
        .rejects.toThrow('Failed to generate content. Please try again.');
    });
  });

  describe('generateImage', () => {
    it('should generate image successfully', async () => {
      const mockResponse = {
        imageUrl: 'https://example.com/generated-image.jpg',
        prompt: 'A futuristic AI workspace',
        style: 'modern',
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockResponse });

      const request = {
        prompt: 'A futuristic AI workspace',
        style: 'modern' as const,
        aspectRatio: '1:1' as const,
        quality: 'hd' as const,
      };

      const result = await aiContentService.generateImage(request);

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/generate-image', request);
    });

    it('should handle image generation errors', async () => {
      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Generation failed'));

      const request = {
        prompt: 'Test image',
      };

      await expect(aiContentService.generateImage(request))
        .rejects.toThrow('Failed to generate image. Please try again.');
    });
  });

  describe('getContentIdeas', () => {
    it('should get content ideas successfully', async () => {
      const mockIdeas = [
        {
          title: 'Tech Trends 2024',
          description: 'Explore the latest technology trends',
          contentType: 'post' as ContentType,
          platforms: ['instagram' as PlatformType],
          trending: true,
          engagement_score: 8.5,
        },
        {
          title: 'AI in Daily Life',
          description: 'How AI is changing our daily routines',
          contentType: 'reel' as ContentType,
          platforms: ['instagram' as PlatformType, 'tiktok' as PlatformType],
          trending: false,
          engagement_score: 7.2,
        },
      ];

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockIdeas });

      const result = await aiContentService.getContentIdeas('technology', ['instagram']);

      expect(result).toEqual(mockIdeas);
      expect(apiClient.get).toHaveBeenCalledWith('/ai/content-ideas', {
        params: { topic: 'technology', platforms: 'instagram' }
      });
    });

    it('should handle empty platforms array', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({ data: [] });

      await aiContentService.getContentIdeas('test topic');

      expect(apiClient.get).toHaveBeenCalledWith('/ai/content-ideas', {
        params: { topic: 'test topic', platforms: '' }
      });
    });
  });

  describe('getTrendingTopics', () => {
    it('should get trending topics successfully', async () => {
      const mockTrending = [
        {
          topics: ['AI', 'Technology', 'Innovation'],
          hashtags: ['#ai', '#tech', '#innovation'],
          platform: 'instagram' as PlatformType,
          lastUpdated: '2024-01-01T00:00:00Z',
        },
      ];

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockTrending });

      const result = await aiContentService.getTrendingTopics(['instagram']);

      expect(result).toEqual(mockTrending);
      expect(apiClient.get).toHaveBeenCalledWith('/ai/trending-topics', {
        params: { platforms: 'instagram' }
      });
    });
  });

  describe('improveContent', () => {
    it('should improve content successfully', async () => {
      const mockImprovement = {
        title: 'Improved Title',
        caption: 'Improved caption with better engagement',
        hashtags: ['#improved', '#content'],
        suggestions: ['Great improvement!'],
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockImprovement });

      const result = await aiContentService.improveContent(
        'Original content',
        ['engagement', 'hashtags']
      );

      expect(result).toEqual(mockImprovement);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/improve-content', {
        content: 'Original content',
        improvements: ['engagement', 'hashtags']
      });
    });
  });

  describe('generateHashtags', () => {
    it('should generate hashtags successfully', async () => {
      const mockHashtags = ['#tech', '#ai', '#innovation', '#future'];

      (apiClient.post as jest.Mock).mockResolvedValue({ 
        data: { hashtags: mockHashtags } 
      });

      const result = await aiContentService.generateHashtags(
        'Content about AI technology',
        ['instagram'],
        5
      );

      expect(result).toEqual(mockHashtags);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/generate-hashtags', {
        content: 'Content about AI technology',
        platforms: ['instagram'],
        count: 5
      });
    });

    it('should use default count when not specified', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ 
        data: { hashtags: [] } 
      });

      await aiContentService.generateHashtags('test content', ['instagram']);

      expect(apiClient.post).toHaveBeenCalledWith('/ai/generate-hashtags', {
        content: 'test content',
        platforms: ['instagram'],
        count: 10
      });
    });
  });

  describe('analyzeContent', () => {
    it('should analyze content successfully', async () => {
      const mockAnalysis = {
        sentiment: 'positive' as const,
        engagement_score: 8.5,
        readability_score: 7.8,
        suggestions: ['Add more visual elements', 'Include trending hashtags'],
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockAnalysis });

      const result = await aiContentService.analyzeContent('Test content for analysis');

      expect(result).toEqual(mockAnalysis);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/analyze-content', {
        content: 'Test content for analysis'
      });
    });
  });

  describe('generateContentCalendar', () => {
    it('should generate content calendar successfully', async () => {
      const mockCalendar = [
        {
          date: '2024-01-01',
          suggestions: [
            {
              title: 'New Year Tech Predictions',
              description: 'Predict tech trends for the new year',
              contentType: 'post' as ContentType,
              platforms: ['instagram' as PlatformType],
              trending: true,
              engagement_score: 9.0,
            },
          ],
        },
      ];

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockCalendar });

      const result = await aiContentService.generateContentCalendar(
        7,
        ['instagram'],
        ['technology', 'ai']
      );

      expect(result).toEqual(mockCalendar);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/content-calendar', {
        days: 7,
        platforms: ['instagram'],
        topics: ['technology', 'ai']
      });
    });

    it('should use default parameters', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ data: [] });

      await aiContentService.generateContentCalendar(undefined, ['instagram']);

      expect(apiClient.post).toHaveBeenCalledWith('/ai/content-calendar', {
        days: 7,
        platforms: ['instagram'],
        topics: []
      });
    });
  });

  describe('getOptimalPostingTimes', () => {
    it('should get optimal posting times successfully', async () => {
      const mockTimes = [
        {
          platform: 'instagram' as PlatformType,
          optimal_times: [
            {
              day: 'Monday',
              hours: [9, 12, 18],
            },
          ],
          engagement_boost: 1.25,
        },
      ];

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockTimes });

      const result = await aiContentService.getOptimalPostingTimes(['instagram']);

      expect(result).toEqual(mockTimes);
      expect(apiClient.get).toHaveBeenCalledWith('/ai/optimal-posting-times', {
        params: { platforms: 'instagram' }
      });
    });
  });

  describe('generateContentVariations', () => {
    it('should generate content variations successfully', async () => {
      const mockVariations = {
        original: 'Original content',
        variations: [
          {
            content: 'Variation 1 with different tone',
            changes: ['Changed tone to casual', 'Added emojis'],
          },
          {
            content: 'Variation 2 with more engagement',
            changes: ['Added call-to-action', 'Included trending hashtags'],
          },
        ],
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockVariations });

      const result = await aiContentService.generateContentVariations(
        'Original content',
        2
      );

      expect(result).toEqual(mockVariations);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/content-variations', {
        content: 'Original content',
        count: 2
      });
    });

    it('should use default variation count', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ 
        data: { original: 'test', variations: [] } 
      });

      await aiContentService.generateContentVariations('test content');

      expect(apiClient.post).toHaveBeenCalledWith('/ai/content-variations', {
        content: 'test content',
        count: 3
      });
    });
  });

  describe('getContentTemplate', () => {
    it('should get content template successfully', async () => {
      const mockTemplate = {
        template: 'Check out this amazing {product}! {emoji}',
        placeholders: ['{product}', '{emoji}'],
        tips: ['Use high-quality images', 'Include relevant hashtags'],
      };

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockTemplate });

      const result = await aiContentService.getContentTemplate(
        'post',
        'instagram',
        'product'
      );

      expect(result).toEqual(mockTemplate);
      expect(apiClient.get).toHaveBeenCalledWith('/ai/content-template', {
        params: { 
          content_type: 'post', 
          platform: 'instagram', 
          category: 'product' 
        }
      });
    });
  });

  describe('generateVideoScript', () => {
    it('should generate video script successfully', async () => {
      const mockScript = {
        script: 'Complete video script...',
        scenes: [
          {
            timestamp: '00:00',
            description: 'Opening scene',
            dialogue: 'Welcome to our channel!',
            visual_notes: 'Show logo and intro animation',
          },
        ],
        estimated_duration: 60,
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockScript });

      const result = await aiContentService.generateVideoScript(
        'AI technology overview',
        60,
        'educational'
      );

      expect(result).toEqual(mockScript);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/generate-video-script', {
        topic: 'AI technology overview',
        duration: 60,
        style: 'educational'
      });
    });

    it('should use default style', async () => {
      (apiClient.post as jest.Mock).mockResolvedValue({ 
        data: { script: '', scenes: [], estimated_duration: 0 } 
      });

      await aiContentService.generateVideoScript('test topic', 30);

      expect(apiClient.post).toHaveBeenCalledWith('/ai/generate-video-script', {
        topic: 'test topic',
        duration: 30,
        style: 'educational'
      });
    });
  });

  describe('getPersonalizedRecommendations', () => {
    it('should get personalized recommendations successfully', async () => {
      const mockRecommendations = [
        {
          title: 'Tech Tutorial for Beginners',
          description: 'Easy-to-follow tech tutorial',
          contentType: 'video' as ContentType,
          platforms: ['youtube' as PlatformType],
          trending: false,
          engagement_score: 8.0,
        },
      ];

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockRecommendations });

      const result = await aiContentService.getPersonalizedRecommendations(
        ['technology', 'education'],
        ['youtube']
      );

      expect(result).toEqual(mockRecommendations);
      expect(apiClient.post).toHaveBeenCalledWith('/ai/personalized-recommendations', {
        interests: ['technology', 'education'],
        platforms: ['youtube']
      });
    });
  });

  describe('error handling', () => {
    it('should handle network errors consistently', async () => {
      const networkError = new Error('Network error');
      (apiClient.post as jest.Mock).mockRejectedValue(networkError);

      const methods = [
        () => aiContentService.generateContent({
          prompt: 'test',
          contentType: 'post',
          platforms: ['instagram']
        }),
        () => aiContentService.generateImage({ prompt: 'test' }),
        () => aiContentService.improveContent('test', ['engagement']),
        () => aiContentService.generateHashtags('test', ['instagram']),
        () => aiContentService.analyzeContent('test'),
        () => aiContentService.generateContentCalendar(7, ['instagram']),
        () => aiContentService.generateContentVariations('test'),
        () => aiContentService.generateVideoScript('test', 30),
        () => aiContentService.getPersonalizedRecommendations(['tech'], ['instagram']),
      ];

      for (const method of methods) {
        await expect(method()).rejects.toThrow();
      }
    });

    it('should handle API errors for GET requests', async () => {
      (apiClient.get as jest.Mock).mockRejectedValue(new Error('API Error'));

      await expect(aiContentService.getContentIdeas('test'))
        .rejects.toThrow('Failed to get content ideas. Please try again.');

      await expect(aiContentService.getTrendingTopics(['instagram']))
        .rejects.toThrow('Failed to get trending topics. Please try again.');
    });
  });
});