/**
 * AI Multimodal Service for Mobile App
 * Provides access to advanced AI content generation features
 */

import { ApiClient } from './ApiClient';
import { Platform } from '../types/common';

export interface VoiceoverRequest {
  text: string;
  voice?: string;
  language?: string;
  platform?: Platform;
  speed?: number;
}

export interface ImageToVideoRequest {
  motion_prompt: string;
  platform?: Platform;
  duration?: number;
  style?: string;
}

export interface MemeRequest {
  topic: string;
  brand_voice?: string;
  platform?: Platform;
  target_audience?: string;
  include_brand_elements?: boolean;
}

export interface ShortFormVideoRequest {
  platform?: Platform;
  style?: string;
  target_duration?: number;
  add_captions?: boolean;
  add_effects?: boolean;
}

export class AIMultiModalService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Generate AI voiceover from text
   */
  async generateVoiceover(request: VoiceoverRequest): Promise<any> {
    try {
      const response = await this.apiClient.post('/ai-multimodal/ai-voiceover/generate', {
        text: request.text,
        voice: request.voice || 'alloy',
        language: request.language || 'en',
        platform: request.platform || Platform.INSTAGRAM,
        speed: request.speed || 1.0,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Voiceover generation failed: ${error.message}`);
    }
  }

  /**
   * Create video from image with AI motion
   */
  async createImageToVideo(imageUri: string, request: ImageToVideoRequest): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'image.jpg',
      } as any);
      formData.append('motion_prompt', request.motion_prompt);
      formData.append('platform', request.platform || Platform.INSTAGRAM);
      formData.append('duration', (request.duration || 15).toString());
      formData.append('style', request.style || 'cinematic');

      const response = await this.apiClient.post('/ai-multimodal/image-to-video/create', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Image to video creation failed: ${error.message}`);
    }
  }

  /**
   * Generate trending meme
   */
  async generateTrendingMeme(request: MemeRequest): Promise<any> {
    try {
      const response = await this.apiClient.post('/ai-multimodal/enhanced-memes/trending', {
        topic: request.topic,
        brand_voice: request.brand_voice || 'casual',
        platform: request.platform || Platform.INSTAGRAM,
        target_audience: request.target_audience || 'general',
        include_brand_elements: request.include_brand_elements || false,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Meme generation failed: ${error.message}`);
    }
  }

  /**
   * Create short-form video from existing video
   */
  async createShortFormVideo(videoUri: string, request: ShortFormVideoRequest): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: videoUri,
        type: 'video/mp4',
        name: 'video.mp4',
      } as any);
      formData.append('platform', request.platform || Platform.TIKTOK);
      formData.append('style', request.style || 'viral');
      formData.append('target_duration', (request.target_duration || 15).toString());
      formData.append('add_captions', (request.add_captions || true).toString());
      formData.append('add_effects', (request.add_effects || true).toString());

      const response = await this.apiClient.post('/ai-multimodal/short-form-video/create', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Short-form video creation failed: ${error.message}`);
    }
  }

  /**
   * Dub video with AI voiceover
   */
  async dubVideo(
    videoUri: string,
    targetLanguage: string,
    voice: string = 'alloy',
    platform: Platform = Platform.INSTAGRAM
  ): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: videoUri,
        type: 'video/mp4',
        name: 'video.mp4',
      } as any);
      formData.append('target_language', targetLanguage);
      formData.append('voice', voice);
      formData.append('platform', platform);
      formData.append('preserve_timing', 'true');

      const response = await this.apiClient.post('/ai-multimodal/ai-voiceover/dub-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Video dubbing failed: ${error.message}`);
    }
  }

  /**
   * Create slideshow video from multiple images
   */
  async createSlideshowVideo(
    imageUris: string[],
    transitionStyle: string = 'smooth',
    platform: Platform = Platform.INSTAGRAM,
    durationPerImage: number = 3.0,
    addMusic: boolean = true
  ): Promise<any> {
    try {
      const formData = new FormData();
      
      // Add multiple image files
      imageUris.forEach((uri, index) => {
        formData.append('files', {
          uri,
          type: 'image/jpeg',
          name: `image_${index}.jpg`,
        } as any);
      });

      formData.append('transition_style', transitionStyle);
      formData.append('platform', platform);
      formData.append('duration_per_image', durationPerImage.toString());
      formData.append('add_music', addMusic.toString());

      const response = await this.apiClient.post('/ai-multimodal/image-to-video/slideshow', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Slideshow creation failed: ${error.message}`);
    }
  }

  /**
   * Create complete content package
   */
  async createCompleteContentPackage(
    sourceFileUri: string,
    contentTheme: string,
    targetPlatforms: Platform[],
    options: {
      includeVoiceover?: boolean;
      includeMemes?: boolean;
      brandVoice?: string;
    } = {}
  ): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('source_file', {
        uri: sourceFileUri,
        type: 'video/mp4',
        name: 'source.mp4',
      } as any);
      formData.append('content_theme', contentTheme);
      targetPlatforms.forEach(platform => {
        formData.append('target_platforms', platform);
      });
      formData.append('include_voiceover', (options.includeVoiceover || true).toString());
      formData.append('include_memes', (options.includeMemes || true).toString());
      formData.append('brand_voice', options.brandVoice || 'casual');

      const response = await this.apiClient.post('/ai-multimodal/multi-modal/complete-package', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Complete package creation failed: ${error.message}`);
    }
  }

  /**
   * Analyze meme performance potential
   */
  async analyzeMemePerformance(concept: string, platform: Platform = Platform.INSTAGRAM): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('meme_concept', concept);
      formData.append('platform', platform);

      const response = await this.apiClient.post('/ai-multimodal/enhanced-memes/analyze-performance', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Meme performance analysis failed: ${error.message}`);
    }
  }

  /**
   * Generate text-to-image-video content
   */
  async generateTextToImageVideo(
    textPrompt: string,
    motionDescription: string,
    platform: Platform = Platform.INSTAGRAM,
    style: string = 'realistic',
    duration: number = 15
  ): Promise<any> {
    try {
      const response = await this.apiClient.post('/ai-multimodal/image-to-video/text-to-video', {
        text_prompt: textPrompt,
        motion_description: motionDescription,
        platform,
        style,
        duration,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Text-to-image-video creation failed: ${error.message}`);
    }
  }

  /**
   * Create trend-based video
   */
  async createTrendBasedVideo(
    contentTheme: string,
    trendingAudio: string | null = null,
    platform: Platform = Platform.TIKTOK,
    videoStyle: string = 'trending'
  ): Promise<any> {
    try {
      const response = await this.apiClient.post('/ai-multimodal/short-form-video/trend-based', {
        content_theme: contentTheme,
        trending_audio: trendingAudio,
        platform,
        video_style: videoStyle,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Trend-based video creation failed: ${error.message}`);
    }
  }
}

export default AIMultiModalService;