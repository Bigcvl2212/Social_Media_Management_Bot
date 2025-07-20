import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export enum ContentType {
  IMAGE = 'image',
  VIDEO = 'video',
  TEXT = 'text',
  CAROUSEL = 'carousel',
  STORY = 'story',
  REEL = 'reel',
}

export enum ContentStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  SCHEDULED = 'scheduled',
  ARCHIVED = 'archived',
}

export enum ScheduleStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface Content {
  id: string;
  title: string;
  description?: string;
  content_type: ContentType;
  file_path?: string;
  thumbnail_url?: string;
  status: ContentStatus;
  ai_metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CalendarEvent {
  id: string;
  content_id: string;
  title: string;
  content_type: ContentType;
  platform: string;
  scheduled_time: string;
  status: ScheduleStatus;
  caption?: string;
  results?: Record<string, unknown>;
}

export interface ContentUploadResponse {
  success: boolean;
  content: Content;
  message?: string;
}

export interface CalendarEventsResponse {
  success: boolean;
  events: CalendarEvent[];
  total: number;
}

export interface ContentStats {
  total: number;
  by_status: Record<ContentStatus, number>;
  by_type: Record<ContentType, number>;
  recent_uploads: number;
}

// API functions
export const contentApi = {
  // Content CRUD
  async getContent(params?: {
    page?: number;
    limit?: number;
    search?: string;
    content_type?: ContentType;
    status?: ContentStatus;
  }): Promise<{ contents: Content[]; total: number }> {
    try {
      const response = await api.get('/content', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching content:', error);
      return { contents: [], total: 0 };
    }
  },

  async getContentById(id: string): Promise<Content | null> {
    try {
      const response = await api.get(`/content/${id}`);
      return response.data.content;
    } catch (error) {
      console.error('Error fetching content by ID:', error);
      return null;
    }
  },

  async createContent(data: Partial<Content>): Promise<ContentUploadResponse> {
    try {
      const response = await api.post('/content', data);
      return response.data;
    } catch (error) {
      console.error('Error creating content:', error);
      return { success: false, content: {} as Content, message: 'Failed to create content' };
    }
  },

  async updateContent(id: string, data: Partial<Content>): Promise<ContentUploadResponse> {
    try {
      const response = await api.put(`/content/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating content:', error);
      return { success: false, content: {} as Content, message: 'Failed to update content' };
    }
  },

  async deleteContent(id: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await api.delete(`/content/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting content:', error);
      return { success: false, message: 'Failed to delete content' };
    }
  },

  // File upload
  async uploadFile(file: File, onProgress?: (progress: number) => void): Promise<ContentUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/content/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      });

      return response.data;
    } catch (error) {
      console.error('Error uploading file:', error);
      return { success: false, content: {} as Content, message: 'Failed to upload file' };
    }
  },

  // Calendar and scheduling
  async getCalendarEvents(startDate: Date, endDate: Date): Promise<CalendarEventsResponse> {
    try {
      const response = await api.get('/content/schedule/calendar', {
        params: {
          start_date: startDate.toISOString(),
          end_date: endDate.toISOString(),
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching calendar events:', error);
      return { success: false, events: [], total: 0 };
    }
  },

  async scheduleContent(data: {
    content_id: string;
    platform: string;
    scheduled_time: string;
    caption?: string;
  }): Promise<{ success: boolean; schedule?: CalendarEvent; message?: string }> {
    try {
      const response = await api.post('/content/schedule', data);
      return response.data;
    } catch (error) {
      console.error('Error scheduling content:', error);
      return { success: false, message: 'Failed to schedule content' };
    }
  },

  async updateSchedule(id: string, data: {
    scheduled_time?: string;
    caption?: string;
    status?: ScheduleStatus;
  }): Promise<{ success: boolean; schedule?: CalendarEvent; message?: string }> {
    try {
      const response = await api.put(`/content/schedule/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating schedule:', error);
      return { success: false, message: 'Failed to update schedule' };
    }
  },

  async deleteSchedule(id: string): Promise<{ success: boolean; message?: string }> {
    try {
      const response = await api.delete(`/content/schedule/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting schedule:', error);
      return { success: false, message: 'Failed to delete schedule' };
    }
  },

  // Stats
  async getContentStats(): Promise<ContentStats> {
    try {
      const response = await api.get('/content/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching content stats:', error);
      return {
        total: 0,
        by_status: {} as Record<ContentStatus, number>,
        by_type: {} as Record<ContentType, number>,
        recent_uploads: 0,
      };
    }
  },
};