/**
 * Offline Storage Service
 * Handles offline content drafting and synchronization
 */

import { MMKV } from 'react-native-mmkv';
import NetInfo from '@react-native-community/netinfo';
import { ContentCreate, Content } from '../types';
import apiClient, { API_ENDPOINTS } from './api';

export interface OfflineDraft extends ContentCreate {
  id: string;
  localId: string;
  timestamp: number;
  isOffline: boolean;
  syncStatus: 'pending' | 'syncing' | 'synced' | 'failed';
  lastModified: number;
  mediaLocalPaths?: string[]; // Local paths to media files
}

export interface SyncResult {
  success: boolean;
  syncedCount: number;
  failedCount: number;
  errors: string[];
}

class OfflineStorageService {
  private storage = new MMKV();
  private isOnline = true;
  private syncInProgress = false;

  constructor() {
    this.initializeNetworkListener();
  }

  /**
   * Initialize network state listener
   */
  private initializeNetworkListener(): void {
    NetInfo.addEventListener(state => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected ?? false;
      
      // Auto-sync when coming back online
      if (wasOffline && this.isOnline) {
        this.syncPendingDrafts();
      }
    });
  }

  /**
   * Save content draft offline
   */
  saveDraftOffline(draft: Omit<OfflineDraft, 'id' | 'localId' | 'timestamp' | 'isOffline' | 'syncStatus' | 'lastModified'>): string {
    const localId = `draft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const offlineDraft: OfflineDraft = {
      ...draft,
      id: '', // Will be set after sync
      localId,
      timestamp: Date.now(),
      isOffline: true,
      syncStatus: 'pending',
      lastModified: Date.now(),
    };

    try {
      const drafts = this.getAllDrafts();
      drafts.push(offlineDraft);
      this.storage.set('offline_drafts', JSON.stringify(drafts));
      
      console.log('Draft saved offline:', localId);
      return localId;
    } catch (error) {
      console.error('Failed to save draft offline:', error);
      throw new Error('Failed to save draft offline');
    }
  }

  /**
   * Update existing draft
   */
  updateDraftOffline(localId: string, updates: Partial<OfflineDraft>): boolean {
    try {
      const drafts = this.getAllDrafts();
      const draftIndex = drafts.findIndex(d => d.localId === localId);
      
      if (draftIndex === -1) {
        return false;
      }

      drafts[draftIndex] = {
        ...drafts[draftIndex],
        ...updates,
        lastModified: Date.now(),
        syncStatus: drafts[draftIndex].syncStatus === 'synced' ? 'pending' : drafts[draftIndex].syncStatus,
      };

      this.storage.set('offline_drafts', JSON.stringify(drafts));
      console.log('Draft updated offline:', localId);
      return true;
    } catch (error) {
      console.error('Failed to update draft offline:', error);
      return false;
    }
  }

  /**
   * Delete draft
   */
  deleteDraft(localId: string): boolean {
    try {
      const drafts = this.getAllDrafts();
      const filteredDrafts = drafts.filter(d => d.localId !== localId);
      this.storage.set('offline_drafts', JSON.stringify(filteredDrafts));
      
      console.log('Draft deleted:', localId);
      return true;
    } catch (error) {
      console.error('Failed to delete draft:', error);
      return false;
    }
  }

  /**
   * Get all drafts
   */
  getAllDrafts(): OfflineDraft[] {
    try {
      const stored = this.storage.getString('offline_drafts');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to get drafts:', error);
      return [];
    }
  }

  /**
   * Get pending drafts (not synced)
   */
  getPendingDrafts(): OfflineDraft[] {
    return this.getAllDrafts().filter(draft => 
      draft.syncStatus === 'pending' || draft.syncStatus === 'failed'
    );
  }

  /**
   * Get draft by local ID
   */
  getDraftById(localId: string): OfflineDraft | null {
    const drafts = this.getAllDrafts();
    return drafts.find(d => d.localId === localId) || null;
  }

  /**
   * Sync pending drafts with server
   */
  async syncPendingDrafts(): Promise<SyncResult> {
    if (this.syncInProgress || !this.isOnline) {
      return {
        success: false,
        syncedCount: 0,
        failedCount: 0,
        errors: ['Sync already in progress or offline'],
      };
    }

    this.syncInProgress = true;
    
    try {
      const pendingDrafts = this.getPendingDrafts();
      
      if (pendingDrafts.length === 0) {
        return {
          success: true,
          syncedCount: 0,
          failedCount: 0,
          errors: [],
        };
      }

      let syncedCount = 0;
      let failedCount = 0;
      const errors: string[] = [];

      for (const draft of pendingDrafts) {
        try {
          // Update sync status to syncing
          this.updateDraftSyncStatus(draft.localId, 'syncing');

          // Prepare content for sync
          const contentData: ContentCreate = {
            title: draft.title,
            caption: draft.caption,
            content_type: draft.content_type,
            media_urls: draft.media_urls,
            platforms: draft.platforms,
            scheduled_time: draft.scheduled_time,
          };

          // Upload media files if they exist locally
          if (draft.mediaLocalPaths && draft.mediaLocalPaths.length > 0) {
            const uploadedUrls = await this.uploadMediaFiles(draft.mediaLocalPaths);
            contentData.media_urls = uploadedUrls;
          }

          // Sync with server
          const response = await apiClient.post(API_ENDPOINTS.CONTENT, contentData);
          const syncedContent: Content = response.data;

          // Update draft with server ID and mark as synced
          this.updateDraftOffline(draft.localId, {
            id: syncedContent.id,
            syncStatus: 'synced',
            isOffline: false,
          });

          syncedCount++;
          console.log('Draft synced successfully:', draft.localId);

        } catch (error) {
          console.error('Failed to sync draft:', draft.localId, error);
          
          // Mark as failed
          this.updateDraftSyncStatus(draft.localId, 'failed');
          
          failedCount++;
          errors.push(`Failed to sync draft "${draft.title}": ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }

      console.log(`Sync completed: ${syncedCount} synced, ${failedCount} failed`);

      return {
        success: failedCount === 0,
        syncedCount,
        failedCount,
        errors,
      };

    } catch (error) {
      console.error('Sync process failed:', error);
      return {
        success: false,
        syncedCount: 0,
        failedCount: 0,
        errors: ['Sync process failed'],
      };
    } finally {
      this.syncInProgress = false;
    }
  }

  /**
   * Upload media files to server
   */
  private async uploadMediaFiles(localPaths: string[]): Promise<string[]> {
    const uploadedUrls: string[] = [];

    for (const localPath of localPaths) {
      try {
        const formData = new FormData();
        formData.append('file', {
          uri: localPath,
          type: 'image/jpeg', // This should be determined dynamically
          name: localPath.split('/').pop() || 'media',
        } as any);

        const response = await apiClient.post(API_ENDPOINTS.UPLOAD_MEDIA, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        uploadedUrls.push(response.data.url);
      } catch (error) {
        console.error('Failed to upload media file:', localPath, error);
        throw new Error(`Failed to upload media: ${localPath}`);
      }
    }

    return uploadedUrls;
  }

  /**
   * Update draft sync status
   */
  private updateDraftSyncStatus(localId: string, syncStatus: OfflineDraft['syncStatus']): void {
    this.updateDraftOffline(localId, { syncStatus });
  }

  /**
   * Clear synced drafts
   */
  clearSyncedDrafts(): void {
    try {
      const drafts = this.getAllDrafts();
      const unsyncedDrafts = drafts.filter(draft => draft.syncStatus !== 'synced');
      this.storage.set('offline_drafts', JSON.stringify(unsyncedDrafts));
      
      console.log('Synced drafts cleared');
    } catch (error) {
      console.error('Failed to clear synced drafts:', error);
    }
  }

  /**
   * Get sync statistics
   */
  getSyncStats(): {
    totalDrafts: number;
    pendingDrafts: number;
    syncedDrafts: number;
    failedDrafts: number;
  } {
    const drafts = this.getAllDrafts();
    
    return {
      totalDrafts: drafts.length,
      pendingDrafts: drafts.filter(d => d.syncStatus === 'pending').length,
      syncedDrafts: drafts.filter(d => d.syncStatus === 'synced').length,
      failedDrafts: drafts.filter(d => d.syncStatus === 'failed').length,
    };
  }

  /**
   * Check if online
   */
  isOnlineStatus(): boolean {
    return this.isOnline;
  }

  /**
   * Force sync (manual trigger)
   */
  async forcSync(): Promise<SyncResult> {
    console.log('Force sync triggered');
    return this.syncPendingDrafts();
  }

  /**
   * Export drafts for backup
   */
  exportDrafts(): string {
    const drafts = this.getAllDrafts();
    return JSON.stringify(drafts, null, 2);
  }

  /**
   * Import drafts from backup
   */
  importDrafts(draftsJson: string): boolean {
    try {
      const importedDrafts: OfflineDraft[] = JSON.parse(draftsJson);
      
      // Validate structure
      if (!Array.isArray(importedDrafts)) {
        throw new Error('Invalid drafts format');
      }

      // Merge with existing drafts (avoid duplicates by localId)
      const existingDrafts = this.getAllDrafts();
      const existingLocalIds = new Set(existingDrafts.map(d => d.localId));
      
      const newDrafts = importedDrafts.filter(d => !existingLocalIds.has(d.localId));
      const allDrafts = [...existingDrafts, ...newDrafts];
      
      this.storage.set('offline_drafts', JSON.stringify(allDrafts));
      
      console.log(`Imported ${newDrafts.length} new drafts`);
      return true;
    } catch (error) {
      console.error('Failed to import drafts:', error);
      return false;
    }
  }
}

// Export singleton instance
export const offlineStorageService = new OfflineStorageService();
export default offlineStorageService;