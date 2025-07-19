/**
 * Post related types for Social Media Management Bot
 */

export enum PostStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  PUBLISHED = 'published',
  FAILED = 'failed',
  DELETED = 'deleted'
}

export interface Post {
  id: string;
  content: string;
  status: PostStatus;
  scheduledDate?: string;
  publishedDate?: string;
  platforms: string[];
  mediaUrls?: string[];
  createdAt: string;
  updatedAt: string;
}