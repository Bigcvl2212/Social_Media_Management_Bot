/**
 * Offline Storage Service Tests
 * Tests for offline content drafting and synchronization
 */

// import NetInfo from '@react-native-community/netinfo'; // Unused import
import offlineStorageService, { OfflineDraft } from '../../src/services/offlineStorageService';
import apiClient from '../../src/services/api';

// Mock MMKV
jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    set: jest.fn(),
    delete: jest.fn(),
  })),
}));

// Mock NetInfo
jest.mock('@react-native-community/netinfo', () => ({
  addEventListener: jest.fn(),
  fetch: jest.fn(() => Promise.resolve({ isConnected: true })),
}));

// Mock API client
jest.mock('../../src/services/api', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
  },
  API_ENDPOINTS: {
    CONTENT: '/content',
    UPLOAD_MEDIA: '/upload/media',
  },
}));

describe('OfflineStorageService', () => {
  let mockStorage: any;

  beforeEach(() => {
    jest.clearAllMocks();
    mockStorage = {
      getString: jest.fn(),
      set: jest.fn(),
      delete: jest.fn(),
    };
    require('react-native-mmkv').MMKV.mockImplementation(() => mockStorage);
  });

  describe('saveDraftOffline', () => {
    it('should save draft offline successfully', () => {
      mockStorage.getString.mockReturnValue('[]'); // Empty drafts array
      
      const draftData = {
        title: 'Test Post',
        caption: 'Test caption',
        content_type: 'post' as const,
        media_urls: [],
        platforms: ['instagram' as const],
      };

      const localId = offlineStorageService.saveDraftOffline(draftData);

      expect(localId).toBeDefined();
      expect(localId).toMatch(/^draft_\d+_/);
      expect(mockStorage.set).toHaveBeenCalledWith(
        'offline_drafts',
        expect.stringContaining('"title":"Test Post"')
      );
    });

    it('should handle storage errors', () => {
      mockStorage.set.mockImplementation(() => {
        throw new Error('Storage error');
      });

      const draftData = {
        title: 'Test Post',
        caption: 'Test caption',
        content_type: 'post' as const,
        media_urls: [],
        platforms: ['instagram' as const],
      };

      expect(() => {
        offlineStorageService.saveDraftOffline(draftData);
      }).toThrow('Failed to save draft offline');
    });
  });

  describe('getAllDrafts', () => {
    it('should return empty array when no drafts exist', () => {
      mockStorage.getString.mockReturnValue(undefined);

      const drafts = offlineStorageService.getAllDrafts();

      expect(drafts).toEqual([]);
    });

    it('should return parsed drafts', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const drafts = offlineStorageService.getAllDrafts();

      expect(drafts).toEqual(mockDrafts);
    });

    it('should handle JSON parse errors', () => {
      mockStorage.getString.mockReturnValue('invalid_json');

      const drafts = offlineStorageService.getAllDrafts();

      expect(drafts).toEqual([]);
    });
  });

  describe('updateDraftOffline', () => {
    it('should update existing draft', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const result = offlineStorageService.updateDraftOffline('draft_123', {
        title: 'Updated Title',
      });

      expect(result).toBe(true);
      expect(mockStorage.set).toHaveBeenCalled();
    });

    it('should return false for non-existent draft', () => {
      mockStorage.getString.mockReturnValue('[]');

      const result = offlineStorageService.updateDraftOffline('non_existent', {
        title: 'Updated Title',
      });

      expect(result).toBe(false);
    });
  });

  describe('deleteDraft', () => {
    it('should delete draft successfully', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const result = offlineStorageService.deleteDraft('draft_123');

      expect(result).toBe(true);
      expect(mockStorage.set).toHaveBeenCalledWith('offline_drafts', '[]');
    });
  });

  describe('getPendingDrafts', () => {
    it('should return only pending and failed drafts', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_1',
          title: 'Pending',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
        {
          id: 'synced_id',
          localId: 'draft_2',
          title: 'Synced',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: false,
          syncStatus: 'synced',
          lastModified: Date.now(),
        },
        {
          id: '',
          localId: 'draft_3',
          title: 'Failed',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'failed',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const pendingDrafts = offlineStorageService.getPendingDrafts();

      expect(pendingDrafts).toHaveLength(2);
      expect(pendingDrafts[0].syncStatus).toBe('pending');
      expect(pendingDrafts[1].syncStatus).toBe('failed');
    });
  });

  describe('getDraftById', () => {
    it('should return draft by local ID', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const draft = offlineStorageService.getDraftById('draft_123');

      expect(draft).toBeDefined();
      expect(draft?.localId).toBe('draft_123');
    });

    it('should return null for non-existent draft', () => {
      mockStorage.getString.mockReturnValue('[]');

      const draft = offlineStorageService.getDraftById('non_existent');

      expect(draft).toBeNull();
    });
  });

  describe('syncPendingDrafts', () => {
    it('should sync pending drafts successfully', async () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));
      
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: { id: 'server_id_123' },
      });

      const result = await offlineStorageService.syncPendingDrafts();

      expect(result.success).toBe(true);
      expect(result.syncedCount).toBe(1);
      expect(result.failedCount).toBe(0);
      expect(apiClient.post).toHaveBeenCalledWith(
        '/content',
        expect.objectContaining({
          title: 'Test',
          caption: 'Caption',
        })
      );
    });

    it('should return early if sync already in progress', async () => {
      // First call starts sync
      const syncPromise1 = offlineStorageService.syncPendingDrafts();
      
      // Second call should return immediately
      const result2 = await offlineStorageService.syncPendingDrafts();

      expect(result2.success).toBe(false);
      expect(result2.errors).toContain('Sync already in progress or offline');

      // Wait for first sync to complete
      await syncPromise1;
    });

    it('should handle sync errors gracefully', async () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));
      
      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Network error'));

      const result = await offlineStorageService.syncPendingDrafts();

      expect(result.success).toBe(false);
      expect(result.syncedCount).toBe(0);
      expect(result.failedCount).toBe(1);
      expect(result.errors).toHaveLength(1);
    });
  });

  describe('getSyncStats', () => {
    it('should return correct sync statistics', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_1',
          title: 'Pending',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
        {
          id: 'server_id',
          localId: 'draft_2',
          title: 'Synced',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: false,
          syncStatus: 'synced',
          lastModified: Date.now(),
        },
        {
          id: '',
          localId: 'draft_3',
          title: 'Failed',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'failed',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const stats = offlineStorageService.getSyncStats();

      expect(stats).toEqual({
        totalDrafts: 3,
        pendingDrafts: 1,
        syncedDrafts: 1,
        failedDrafts: 1,
      });
    });
  });

  describe('network status', () => {
    it('should return online status', () => {
      const isOnline = offlineStorageService.isOnlineStatus();
      
      expect(typeof isOnline).toBe('boolean');
    });

    it('should force sync', async () => {
      mockStorage.getString.mockReturnValue('[]');

      const result = await offlineStorageService.forceSync();

      expect(result).toBeDefined();
      expect(typeof result.success).toBe('boolean');
    });
  });

  describe('draft management', () => {
    it('should export drafts as JSON', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_123',
          title: 'Test',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      const exported = offlineStorageService.exportDrafts();

      expect(typeof exported).toBe('string');
      expect(() => JSON.parse(exported)).not.toThrow();
    });

    it('should import drafts from JSON', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_new',
          title: 'Imported',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue('[]'); // No existing drafts

      const result = offlineStorageService.importDrafts(JSON.stringify(mockDrafts));

      expect(result).toBe(true);
      expect(mockStorage.set).toHaveBeenCalled();
    });

    it('should handle invalid JSON during import', () => {
      const result = offlineStorageService.importDrafts('invalid_json');

      expect(result).toBe(false);
    });

    it('should clear synced drafts', () => {
      const mockDrafts: OfflineDraft[] = [
        {
          id: '',
          localId: 'draft_pending',
          title: 'Pending',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: true,
          syncStatus: 'pending',
          lastModified: Date.now(),
        },
        {
          id: 'server_id',
          localId: 'draft_synced',
          title: 'Synced',
          caption: 'Caption',
          content_type: 'post',
          media_urls: [],
          platforms: ['instagram'],
          timestamp: Date.now(),
          isOffline: false,
          syncStatus: 'synced',
          lastModified: Date.now(),
        },
      ];

      mockStorage.getString.mockReturnValue(JSON.stringify(mockDrafts));

      offlineStorageService.clearSyncedDrafts();

      expect(mockStorage.set).toHaveBeenCalledWith(
        'offline_drafts',
        expect.stringContaining('"syncStatus":"pending"')
      );
    });
  });
});