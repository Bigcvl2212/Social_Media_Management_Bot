/**
 * Offline Storage Service for Social Media Management Bot
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { PostStatus } from '../types/post';

interface PostDraft {
  id: string;
  content: string;
  status: PostStatus;
  createdAt: string;
}

class OfflineStorageService {
  private static instance: OfflineStorageService;

  public static getInstance(): OfflineStorageService {
    if (!OfflineStorageService.instance) {
      OfflineStorageService.instance = new OfflineStorageService();
    }
    return OfflineStorageService.instance;
  }

  async saveDraft(draft: PostDraft): Promise<void> {
    try {
      const drafts = await this.getDrafts();
      drafts.push(draft);
      await AsyncStorage.setItem('post_drafts', JSON.stringify(drafts));
    } catch (error) {
      console.error('Error saving draft:', error);
    }
  }

  async getDrafts(): Promise<PostDraft[]> {
    try {
      const draftsString = await AsyncStorage.getItem('post_drafts');
      return draftsString ? JSON.parse(draftsString) : [];
    } catch (error) {
      console.error('Error loading drafts:', error);
      return [];
    }
  }

  async clearDrafts(): Promise<void> {
    try {
      await AsyncStorage.removeItem('post_drafts');
    } catch (error) {
      console.error('Error clearing drafts:', error);
    }
  }
}

export default OfflineStorageService;