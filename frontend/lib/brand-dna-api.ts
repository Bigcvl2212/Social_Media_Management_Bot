import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/brand-dna`,
  headers: { 'Content-Type': 'application/json' },
});

export interface BrandProfile {
  voice: string;
  pillars: string[];
  dos: string[];
  donts: string[];
  style: Record<string, unknown>;
  confidence: number;
  last_analyzed: string | null;
}

export interface BrandBriefUpdate {
  voice: string;
  pillars: string[];
  dos: string[];
  donts: string[];
}

export interface AnalyzePostsRequest {
  posts: Array<{ text: string; engagement?: number; platform?: string }>;
}

export interface ChatRequest {
  message: string;
}

export const brandDnaApi = {
  getProfile: () => api.get<{ profile: BrandProfile }>('/').then(r => r.data),

  updateBrief: (brief: BrandBriefUpdate) =>
    api.put<{ profile: BrandProfile }>('/brief', brief).then(r => r.data),

  updateStyle: (style: Record<string, unknown>) =>
    api.put<{ profile: BrandProfile }>('/style', style).then(r => r.data),

  analyzePosts: (data: AnalyzePostsRequest) =>
    api.post('/analyze', data).then(r => r.data),

  chat: (data: ChatRequest) =>
    api.post('/chat', data).then(r => r.data),

  getStylePrompt: () =>
    api.get<{ prompt: string }>('/style-prompt').then(r => r.data),

  reset: () => api.post<{ profile: BrandProfile }>('/reset').then(r => r.data),
};
