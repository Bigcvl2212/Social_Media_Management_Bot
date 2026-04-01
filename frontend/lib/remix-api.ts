import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/remix`,
  headers: { 'Content-Type': 'application/json' },
});

export interface RemixFormat {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface OriginalPost {
  id: string;
  post_text: string;
  platform: string;
  engagement_score: number;
  media_url: string | null;
  added_at: string;
}

export interface Remix {
  id: string;
  original_id: string;
  target_format: string;
  remixed_text: string;
  created_at: string;
}

export interface DiscoverTopRequest {
  posts: Array<{ text: string; engagement?: number; platform?: string }>;
  min_score?: number;
}

export interface RemixRequest {
  original_id: string;
  target_format: string;
  brand_prompt?: string;
}

export interface BatchRemixRequest {
  formats: string[];
  top_n?: number;
  brand_prompt?: string;
}

export const remixApi = {
  getFormats: () =>
    api.get<{ formats: RemixFormat[] }>('/formats').then(r => r.data),

  listOriginals: () =>
    api.get<{ originals: OriginalPost[] }>('/originals').then(r => r.data),

  addOriginal: (data: { post_text: string; platform?: string; engagement_score?: number; media_url?: string }) =>
    api.post<{ original: OriginalPost }>('/originals', data).then(r => r.data),

  deleteOriginal: (id: string) =>
    api.delete(`/originals/${id}`).then(r => r.data),

  discoverTop: (data: DiscoverTopRequest) =>
    api.post('/discover-top', data).then(r => r.data),

  remix: (data: RemixRequest) =>
    api.post('/remix', data).then(r => r.data),

  batchRemix: (data: BatchRemixRequest) =>
    api.post('/batch-remix', data).then(r => r.data),

  listRemixes: (params?: { original_id?: string; target_format?: string }) =>
    api.get<{ remixes: Remix[] }>('/remixes', { params }).then(r => r.data),

  deleteRemix: (id: string) =>
    api.delete(`/remixes/${id}`).then(r => r.data),
};
