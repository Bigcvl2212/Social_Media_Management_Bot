/**
 * Media Upload Service
 * Handles image/video picking and uploading
 */

import { Alert, Platform } from 'react-native';
import { 
  ImagePickerResponse, 
  MediaType, 
  launchImageLibrary, 
  launchCamera,
  ImageLibraryOptions,
  CameraOptions
} from 'react-native-image-picker';
import { request, PERMISSIONS, RESULTS } from 'react-native-permissions';
import apiClient, { API_ENDPOINTS } from './api';

export interface MediaFile {
  uri: string;
  type: string;
  name: string;
  size: number;
  duration?: number; // for videos
  width?: number;
  height?: number;
}

export interface MediaUploadResponse {
  url: string;
  fileId: string;
  type: 'image' | 'video';
  size: number;
  dimensions?: {
    width: number;
    height: number;
  };
}

export interface MediaPickerOptions {
  mediaType: 'photo' | 'video' | 'mixed';
  quality: number; // 0-1
  allowsEditing?: boolean;
  aspect?: [number, number];
  multiple?: boolean;
  maxDuration?: number; // for videos in seconds
}

class MediaUploadService {
  private readonly MAX_IMAGE_SIZE = 10 * 1024 * 1024; // 10MB
  private readonly MAX_VIDEO_SIZE = 100 * 1024 * 1024; // 100MB
  private readonly SUPPORTED_IMAGE_FORMATS = ['jpeg', 'jpg', 'png', 'gif', 'webp'];
  private readonly SUPPORTED_VIDEO_FORMATS = ['mp4', 'mov', 'avi', 'mkv'];

  /**
   * Request camera permission
   */
  private async requestCameraPermission(): Promise<boolean> {
    try {
      const permission = Platform.OS === 'ios' 
        ? PERMISSIONS.IOS.CAMERA 
        : PERMISSIONS.ANDROID.CAMERA;
      
      const result = await request(permission);
      return result === RESULTS.GRANTED;
    } catch (error) {
      console.error('Failed to request camera permission:', error);
      return false;
    }
  }

  /**
   * Request photo library permission
   */
  private async requestPhotoLibraryPermission(): Promise<boolean> {
    try {
      const permission = Platform.OS === 'ios' 
        ? PERMISSIONS.IOS.PHOTO_LIBRARY 
        : PERMISSIONS.ANDROID.READ_EXTERNAL_STORAGE;
      
      const result = await request(permission);
      return result === RESULTS.GRANTED;
    } catch (error) {
      console.error('Failed to request photo library permission:', error);
      return false;
    }
  }

  /**
   * Show media picker options
   */
  showMediaPicker(options: MediaPickerOptions = { mediaType: 'mixed', quality: 0.8 }): Promise<MediaFile[]> {
    return new Promise((resolve, reject) => {
      Alert.alert(
        'Select Media',
        'Choose how you want to add media',
        [
          {
            text: 'Camera',
            onPress: () => this.openCamera(options).then(resolve).catch(reject),
          },
          {
            text: 'Gallery',
            onPress: () => this.openGallery(options).then(resolve).catch(reject),
          },
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => resolve([]),
          },
        ]
      );
    });
  }

  /**
   * Open camera to capture media
   */
  async openCamera(options: MediaPickerOptions): Promise<MediaFile[]> {
    const hasPermission = await this.requestCameraPermission();
    if (!hasPermission) {
      throw new Error('Camera permission denied');
    }

    return new Promise((resolve, reject) => {
      const cameraOptions: CameraOptions = {
        mediaType: options.mediaType as MediaType,
        quality: (options.quality as any), // Cast to handle type compatibility
        includeBase64: false,
        includeExtra: true,
      };

      if (options.maxDuration && options.mediaType === 'video') {
        cameraOptions.durationLimit = options.maxDuration;
      }

      launchCamera(cameraOptions, (response: ImagePickerResponse) => {
        if (response.didCancel || response.errorMessage) {
          resolve([]);
          return;
        }

        if (response.assets && response.assets.length > 0) {
          try {
            const mediaFiles = this.processPickerResponse(response);
            resolve(mediaFiles);
          } catch (error) {
            reject(error);
          }
        } else {
          resolve([]);
        }
      });
    });
  }

  /**
   * Open gallery to select media
   */
  async openGallery(options: MediaPickerOptions): Promise<MediaFile[]> {
    const hasPermission = await this.requestPhotoLibraryPermission();
    if (!hasPermission) {
      throw new Error('Photo library permission denied');
    }

    return new Promise((resolve, reject) => {
      const libraryOptions: ImageLibraryOptions = {
        mediaType: options.mediaType as MediaType,
        quality: (options.quality as any), // Cast to handle type compatibility
        includeBase64: false,
        includeExtra: true,
        selectionLimit: options.multiple ? 10 : 1,
      };

      launchImageLibrary(libraryOptions, (response: ImagePickerResponse) => {
        if (response.didCancel || response.errorMessage) {
          resolve([]);
          return;
        }

        if (response.assets && response.assets.length > 0) {
          try {
            const mediaFiles = this.processPickerResponse(response);
            resolve(mediaFiles);
          } catch (error) {
            reject(error);
          }
        } else {
          resolve([]);
        }
      });
    });
  }

  /**
   * Process picker response and validate files
   */
  private processPickerResponse(response: ImagePickerResponse): MediaFile[] {
    if (!response.assets) return [];

    const mediaFiles: MediaFile[] = [];

    for (const asset of response.assets) {
      if (!asset.uri || !asset.type || !asset.fileName) {
        continue;
      }

      // Validate file size
      const isVideo = asset.type.startsWith('video/');
      const maxSize = isVideo ? this.MAX_VIDEO_SIZE : this.MAX_IMAGE_SIZE;
      
      if (asset.fileSize && asset.fileSize > maxSize) {
        throw new Error(`File size too large. Maximum ${isVideo ? '100MB' : '10MB'} allowed.`);
      }

      // Validate file format
      const extension = asset.fileName.split('.').pop()?.toLowerCase() || '';
      const supportedFormats = isVideo ? this.SUPPORTED_VIDEO_FORMATS : this.SUPPORTED_IMAGE_FORMATS;
      
      if (!supportedFormats.includes(extension)) {
        throw new Error(`Unsupported file format: ${extension}`);
      }

      const mediaFile: MediaFile = {
        uri: asset.uri,
        type: asset.type,
        name: asset.fileName,
        size: asset.fileSize || 0,
        width: asset.width,
        height: asset.height,
      };

      if (isVideo && asset.duration) {
        mediaFile.duration = asset.duration;
      }

      mediaFiles.push(mediaFile);
    }

    return mediaFiles;
  }

  /**
   * Upload media file to server
   */
  async uploadMedia(mediaFile: MediaFile): Promise<MediaUploadResponse> {
    try {
      const formData = new FormData();
      
      formData.append('file', {
        uri: mediaFile.uri,
        type: mediaFile.type,
        name: mediaFile.name,
      } as any);

      const response = await apiClient.post(API_ENDPOINTS.UPLOAD_MEDIA, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds for large files
      });

      return response.data;
    } catch (error) {
      console.error('Failed to upload media:', error);
      throw new Error('Failed to upload media. Please try again.');
    }
  }

  /**
   * Upload multiple media files
   */
  async uploadMultipleMedia(mediaFiles: MediaFile[]): Promise<MediaUploadResponse[]> {
    const uploadPromises = mediaFiles.map(file => this.uploadMedia(file));
    
    try {
      const results = await Promise.allSettled(uploadPromises);
      const successfulUploads: MediaUploadResponse[] = [];
      const errors: string[] = [];

      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          successfulUploads.push(result.value);
        } else {
          errors.push(`Failed to upload ${mediaFiles[index].name}: ${result.reason.message}`);
        }
      });

      if (errors.length > 0) {
        console.warn('Some uploads failed:', errors);
      }

      return successfulUploads;
    } catch (error) {
      console.error('Failed to upload multiple media:', error);
      throw new Error('Failed to upload media files. Please try again.');
    }
  }

  /**
   * Get media info without uploading
   */
  getMediaInfo(mediaFile: MediaFile): {
    isImage: boolean;
    isVideo: boolean;
    sizeInMB: number;
    dimensions?: string;
    duration?: string;
  } {
    const isVideo = mediaFile.type.startsWith('video/');
    const isImage = mediaFile.type.startsWith('image/');
    const sizeInMB = mediaFile.size / (1024 * 1024);

    const info: any = {
      isImage,
      isVideo,
      sizeInMB: Math.round(sizeInMB * 100) / 100,
    };

    if (mediaFile.width && mediaFile.height) {
      info.dimensions = `${mediaFile.width}x${mediaFile.height}`;
    }

    if (mediaFile.duration) {
      const minutes = Math.floor(mediaFile.duration / 60);
      const seconds = Math.floor(mediaFile.duration % 60);
      info.duration = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    return info;
  }

  /**
   * Validate media file
   */
  validateMediaFile(mediaFile: MediaFile): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    const isVideo = mediaFile.type.startsWith('video/');

    // Check file size
    const maxSize = isVideo ? this.MAX_VIDEO_SIZE : this.MAX_IMAGE_SIZE;
    if (mediaFile.size > maxSize) {
      errors.push(`File size too large. Maximum ${isVideo ? '100MB' : '10MB'} allowed.`);
    }

    // Check file format
    const extension = mediaFile.name.split('.').pop()?.toLowerCase() || '';
    const supportedFormats = isVideo ? this.SUPPORTED_VIDEO_FORMATS : this.SUPPORTED_IMAGE_FORMATS;
    
    if (!supportedFormats.includes(extension)) {
      errors.push(`Unsupported file format: ${extension}`);
    }

    // Check video duration (max 10 minutes)
    if (isVideo && mediaFile.duration && mediaFile.duration > 600) {
      errors.push('Video duration too long. Maximum 10 minutes allowed.');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get supported formats
   */
  getSupportedFormats(): {
    images: string[];
    videos: string[];
  } {
    return {
      images: this.SUPPORTED_IMAGE_FORMATS,
      videos: this.SUPPORTED_VIDEO_FORMATS,
    };
  }

  /**
   * Get file size limits
   */
  getFileSizeLimits(): {
    maxImageSize: number;
    maxVideoSize: number;
    maxImageSizeMB: number;
    maxVideoSizeMB: number;
  } {
    return {
      maxImageSize: this.MAX_IMAGE_SIZE,
      maxVideoSize: this.MAX_VIDEO_SIZE,
      maxImageSizeMB: this.MAX_IMAGE_SIZE / (1024 * 1024),
      maxVideoSizeMB: this.MAX_VIDEO_SIZE / (1024 * 1024),
    };
  }
}

// Export singleton instance
export const mediaUploadService = new MediaUploadService();
export default mediaUploadService;