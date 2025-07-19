/**
 * Media Upload Service Tests
 * Tests for image/video picking and uploading functionality
 */

import { Alert, Platform } from 'react-native';
import { 
  launchImageLibrary, 
  launchCamera,
  ImagePickerResponse
} from 'react-native-image-picker';
import { request, RESULTS } from 'react-native-permissions';
import mediaUploadService, { MediaFile } from '../../src/services/mediaUploadService';
import apiClient from '../../src/services/api';

// Mock React Native modules
jest.mock('react-native', () => ({
  Alert: {
    alert: jest.fn(),
  },
  Platform: {
    OS: 'ios',
  },
}));

// Mock React Native Image Picker
jest.mock('react-native-image-picker', () => ({
  launchImageLibrary: jest.fn(),
  launchCamera: jest.fn(),
}));

// Mock React Native Permissions
jest.mock('react-native-permissions', () => ({
  request: jest.fn(),
  PERMISSIONS: {
    IOS: {
      CAMERA: 'ios.permission.CAMERA',
      PHOTO_LIBRARY: 'ios.permission.PHOTO_LIBRARY',
    },
    ANDROID: {
      CAMERA: 'android.permission.CAMERA',
      READ_EXTERNAL_STORAGE: 'android.permission.READ_EXTERNAL_STORAGE',
    },
  },
  RESULTS: {
    GRANTED: 'granted',
    DENIED: 'denied',
  },
}));

// Mock API client
jest.mock('../../src/services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
  },
  API_ENDPOINTS: {
    UPLOAD_MEDIA: '/upload/media',
  },
}));

describe('MediaUploadService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock launchCamera to call callback with success response
    (launchCamera as jest.Mock).mockImplementation((options, callback) => {
      callback({
        didCancel: false,
        errorMessage: null,
        assets: [{
          uri: 'file://test.jpg',
          type: 'image/jpeg',
          fileName: 'test.jpg',
          fileSize: 1024,
          width: 100,
          height: 100,
        }],
      });
    });
    
    // Mock launchImageLibrary to call callback with success response
    (launchImageLibrary as jest.Mock).mockImplementation((options, callback) => {
      callback({
        didCancel: false,
        errorMessage: null,
        assets: [{
          uri: 'file://test.jpg',
          type: 'image/jpeg',
          fileName: 'test.jpg',
          fileSize: 1024,
          width: 100,
          height: 100,
        }],
      });
    });
  });

  describe('permission handling', () => {
    it('should request camera permission successfully', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);

      // const result = await mediaUploadService.openCamera({
      await mediaUploadService.openCamera({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(request).toHaveBeenCalledWith('ios.permission.CAMERA');
    });

    it('should handle camera permission denial', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.DENIED);

      await expect(
        mediaUploadService.openCamera({ mediaType: 'photo', quality: 0.8 })
      ).rejects.toThrow('Camera permission denied');
    });

    it('should request photo library permission successfully', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);

      await mediaUploadService.openGallery({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(request).toHaveBeenCalledWith('ios.permission.PHOTO_LIBRARY');
    });

    it('should handle different platforms for permissions', async () => {
      Platform.OS = 'android';
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);

      await mediaUploadService.openCamera({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(request).toHaveBeenCalledWith('android.permission.CAMERA');
    });
  });

  describe('showMediaPicker', () => {
    it('should show media picker alert', async () => {
      const mockAlert = Alert.alert as jest.Mock;
      mockAlert.mockImplementation((title, message, buttons) => {
        // Simulate pressing "Cancel"
        buttons[2].onPress();
      });

      const result = await mediaUploadService.showMediaPicker();

      expect(Alert.alert).toHaveBeenCalledWith(
        'Select Media',
        'Choose how you want to add media',
        expect.arrayContaining([
          expect.objectContaining({ text: 'Camera' }),
          expect.objectContaining({ text: 'Gallery' }),
          expect.objectContaining({ text: 'Cancel' }),
        ])
      );

      expect(result).toEqual([]);
    });
  });

  describe('openCamera', () => {
    it('should open camera and process response', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        assets: [
          {
            uri: 'file://test-image.jpg',
            type: 'image/jpeg',
            fileName: 'test-image.jpg',
            fileSize: 1024 * 1024, // 1MB
            width: 1920,
            height: 1080,
          },
        ],
      };

      (launchCamera as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      const result = await mediaUploadService.openCamera({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(launchCamera).toHaveBeenCalled();
      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        uri: 'file://test-image.jpg',
        type: 'image/jpeg',
        name: 'test-image.jpg',
        size: 1024 * 1024,
      });
    });

    it('should handle camera cancellation', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        didCancel: true,
      };

      (launchCamera as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      const result = await mediaUploadService.openCamera({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(result).toEqual([]);
    });

    it('should handle camera errors', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        errorMessage: 'Camera error',
      };

      (launchCamera as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      const result = await mediaUploadService.openCamera({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(result).toEqual([]);
    });
  });

  describe('openGallery', () => {
    it('should open gallery and process response', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        assets: [
          {
            uri: 'file://gallery-image.jpg',
            type: 'image/jpeg',
            fileName: 'gallery-image.jpg',
            fileSize: 2 * 1024 * 1024, // 2MB
            width: 1080,
            height: 1080,
          },
        ],
      };

      (launchImageLibrary as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      const result = await mediaUploadService.openGallery({
        mediaType: 'photo',
        quality: 0.8,
        multiple: false,
      });

      expect(launchImageLibrary).toHaveBeenCalled();
      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        uri: 'file://gallery-image.jpg',
        type: 'image/jpeg',
        name: 'gallery-image.jpg',
        size: 2 * 1024 * 1024,
      });
    });

    it('should handle multiple file selection', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        assets: [
          {
            uri: 'file://image1.jpg',
            type: 'image/jpeg',
            fileName: 'image1.jpg',
            fileSize: 1024 * 1024,
          },
          {
            uri: 'file://image2.jpg',
            type: 'image/jpeg',
            fileName: 'image2.jpg',
            fileSize: 1024 * 1024,
          },
        ],
      };

      (launchImageLibrary as jest.Mock).mockImplementation((options, callback) => {
        expect(options.selectionLimit).toBe(10);
        callback(mockResponse);
      });

      const result = await mediaUploadService.openGallery({
        mediaType: 'photo',
        quality: 0.8,
        multiple: true,
      });

      expect(result).toHaveLength(2);
    });
  });

  describe('file validation', () => {
    it('should validate file size for images', () => {
      const mockFile: MediaFile = {
        uri: 'file://test.jpg',
        type: 'image/jpeg',
        name: 'test.jpg',
        size: 15 * 1024 * 1024, // 15MB (too large)
      };

      const validation = mediaUploadService.validateMediaFile(mockFile);

      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('File size too large. Maximum 10MB allowed.');
    });

    it('should validate file size for videos', () => {
      const mockFile: MediaFile = {
        uri: 'file://test.mp4',
        type: 'video/mp4',
        name: 'test.mp4',
        size: 150 * 1024 * 1024, // 150MB (too large)
        duration: 120,
      };

      const validation = mediaUploadService.validateMediaFile(mockFile);

      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('File size too large. Maximum 100MB allowed.');
    });

    it('should validate file format', () => {
      const mockFile: MediaFile = {
        uri: 'file://test.bmp',
        type: 'image/bmp',
        name: 'test.bmp',
        size: 1024 * 1024,
      };

      const validation = mediaUploadService.validateMediaFile(mockFile);

      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('Unsupported file format: bmp');
    });

    it('should validate video duration', () => {
      const mockFile: MediaFile = {
        uri: 'file://long-video.mp4',
        type: 'video/mp4',
        name: 'long-video.mp4',
        size: 50 * 1024 * 1024,
        duration: 700, // 11+ minutes (too long)
      };

      const validation = mediaUploadService.validateMediaFile(mockFile);

      expect(validation.isValid).toBe(false);
      expect(validation.errors).toContain('Video duration too long. Maximum 10 minutes allowed.');
    });

    it('should pass validation for valid files', () => {
      const mockFile: MediaFile = {
        uri: 'file://valid.jpg',
        type: 'image/jpeg',
        name: 'valid.jpg',
        size: 5 * 1024 * 1024, // 5MB
      };

      const validation = mediaUploadService.validateMediaFile(mockFile);

      expect(validation.isValid).toBe(true);
      expect(validation.errors).toHaveLength(0);
    });
  });

  describe('processPickerResponse', () => {
    it('should reject files that are too large', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        assets: [
          {
            uri: 'file://large-image.jpg',
            type: 'image/jpeg',
            fileName: 'large-image.jpg',
            fileSize: 15 * 1024 * 1024, // 15MB (too large)
          },
        ],
      };

      (launchCamera as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      await expect(
        mediaUploadService.openCamera({ mediaType: 'photo', quality: 0.8 })
      ).rejects.toThrow('File size too large. Maximum 10MB allowed.');
    });

    it('should reject unsupported file formats', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        assets: [
          {
            uri: 'file://unsupported.bmp',
            type: 'image/bmp',
            fileName: 'unsupported.bmp',
            fileSize: 1024 * 1024,
          },
        ],
      };

      (launchCamera as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      await expect(
        mediaUploadService.openCamera({ mediaType: 'photo', quality: 0.8 })
      ).rejects.toThrow('Unsupported file format: bmp');
    });

    it('should handle incomplete asset data', async () => {
      (request as jest.Mock).mockResolvedValue(RESULTS.GRANTED);
      
      const mockResponse: ImagePickerResponse = {
        assets: [
          {
            // Missing required properties
            uri: undefined,
            type: undefined,
            fileName: undefined,
          },
        ],
      };

      (launchCamera as jest.Mock).mockImplementation((options, callback) => {
        callback(mockResponse);
      });

      const result = await mediaUploadService.openCamera({
        mediaType: 'photo',
        quality: 0.8,
      });

      expect(result).toEqual([]);
    });
  });

  describe('uploadMedia', () => {
    it('should upload media successfully', async () => {
      const mockFile: MediaFile = {
        uri: 'file://test.jpg',
        type: 'image/jpeg',
        name: 'test.jpg',
        size: 1024 * 1024,
      };

      const mockResponse = {
        url: 'https://example.com/uploaded-image.jpg',
        fileId: 'file123',
        type: 'image',
        size: 1024 * 1024,
      };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: mockResponse });

      const result = await mediaUploadService.uploadMedia(mockFile);

      expect(result).toEqual(mockResponse);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/upload/media',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000,
        })
      );
    });

    it('should handle upload errors', async () => {
      const mockFile: MediaFile = {
        uri: 'file://test.jpg',
        type: 'image/jpeg',
        name: 'test.jpg',
        size: 1024 * 1024,
      };

      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Upload failed'));

      await expect(mediaUploadService.uploadMedia(mockFile))
        .rejects.toThrow('Failed to upload media. Please try again.');
    });
  });

  describe('uploadMultipleMedia', () => {
    it('should upload multiple files successfully', async () => {
      const mockFiles: MediaFile[] = [
        {
          uri: 'file://test1.jpg',
          type: 'image/jpeg',
          name: 'test1.jpg',
          size: 1024 * 1024,
        },
        {
          uri: 'file://test2.jpg',
          type: 'image/jpeg',
          name: 'test2.jpg',
          size: 1024 * 1024,
        },
      ];

      const mockResponses = [
        {
          url: 'https://example.com/uploaded-image1.jpg',
          fileId: 'file123',
          type: 'image',
          size: 1024 * 1024,
        },
        {
          url: 'https://example.com/uploaded-image2.jpg',
          fileId: 'file124',
          type: 'image',
          size: 1024 * 1024,
        },
      ];

      (apiClient.post as jest.Mock)
        .mockResolvedValueOnce({ data: mockResponses[0] })
        .mockResolvedValueOnce({ data: mockResponses[1] });

      const result = await mediaUploadService.uploadMultipleMedia(mockFiles);

      expect(result).toEqual(mockResponses);
      expect(apiClient.post).toHaveBeenCalledTimes(2);
    });

    it('should handle partial upload failures', async () => {
      const mockFiles: MediaFile[] = [
        {
          uri: 'file://test1.jpg',
          type: 'image/jpeg',
          name: 'test1.jpg',
          size: 1024 * 1024,
        },
        {
          uri: 'file://test2.jpg',
          type: 'image/jpeg',
          name: 'test2.jpg',
          size: 1024 * 1024,
        },
      ];

      const mockResponse = {
        url: 'https://example.com/uploaded-image1.jpg',
        fileId: 'file123',
        type: 'image',
        size: 1024 * 1024,
      };

      (apiClient.post as jest.Mock)
        .mockResolvedValueOnce({ data: mockResponse })
        .mockRejectedValueOnce(new Error('Upload failed'));

      const result = await mediaUploadService.uploadMultipleMedia(mockFiles);

      expect(result).toHaveLength(1);
      expect(result[0]).toEqual(mockResponse);
    });
  });

  describe('utility methods', () => {
    it('should get media info correctly', () => {
      const mockFile: MediaFile = {
        uri: 'file://test-video.mp4',
        type: 'video/mp4',
        name: 'test-video.mp4',
        size: 5 * 1024 * 1024, // 5MB
        width: 1920,
        height: 1080,
        duration: 125, // 2:05
      };

      const info = mediaUploadService.getMediaInfo(mockFile);

      expect(info).toEqual({
        isImage: false,
        isVideo: true,
        sizeInMB: 5,
        dimensions: '1920x1080',
        duration: '2:05',
      });
    });

    it('should get supported formats', () => {
      const formats = mediaUploadService.getSupportedFormats();

      expect(formats.images).toContain('jpeg');
      expect(formats.images).toContain('png');
      expect(formats.videos).toContain('mp4');
      expect(formats.videos).toContain('mov');
    });

    it('should get file size limits', () => {
      const limits = mediaUploadService.getFileSizeLimits();

      expect(limits.maxImageSizeMB).toBe(10);
      expect(limits.maxVideoSizeMB).toBe(100);
      expect(typeof limits.maxImageSize).toBe('number');
      expect(typeof limits.maxVideoSize).toBe('number');
    });
  });
});