import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/engagement`,
  headers: { 'Content-Type': 'application/json' },
});

export interface EngagementConfig {
  auto_reply_enabled: boolean;
  auto_dm_enabled: boolean;
  auto_like_enabled: boolean;
  sentiment_threshold: number;
  reply_delay_seconds: number;
}

export interface EngagementRule {
  id: string;
  keyword: string;
  response_template: string;
  enabled: boolean;
  created_at: string;
}

export interface EngagementStats {
  total_replies: number;
  total_dms: number;
  total_flagged: number;
  avg_sentiment: number;
}

export interface HistoryItem {
  id: string;
  type: string;
  comment_text: string;
  reply_text: string;
  sentiment: number;
  timestamp: string;
}

export interface FlaggedComment {
  id: string;
  text: string;
  sentiment: number;
  reason: string;
  timestamp: string;
}

export interface ProcessCommentsRequest {
  comments: Array<{ id: string; text: string; author: string }>;
  brand_prompt?: string;
}

export interface WelcomeDmRequest {
  follower_name: string;
  brand_prompt?: string;
}

export const engagementApi = {
  getConfig: () =>
    api.get<{ config: EngagementConfig }>('/config').then(r => r.data),

  updateConfig: (config: Partial<EngagementConfig>) =>
    api.put<{ config: EngagementConfig }>('/config', config).then(r => r.data),

  getRules: () =>
    api.get<{ rules: EngagementRule[] }>('/rules').then(r => r.data),

  addRule: (rule: { keyword: string; response_template: string }) =>
    api.post<{ rule: EngagementRule }>('/rules', rule).then(r => r.data),

  deleteRule: (id: string) =>
    api.delete(`/rules/${id}`).then(r => r.data),

  toggleRule: (id: string) =>
    api.post<{ rule: EngagementRule }>(`/rules/${id}/toggle`).then(r => r.data),

  processComments: (data: ProcessCommentsRequest) =>
    api.post('/process-comments', data).then(r => r.data),

  generateWelcomeDm: (data: WelcomeDmRequest) =>
    api.post('/welcome-dm', data).then(r => r.data),

  getStats: () =>
    api.get<{ stats: EngagementStats }>('/stats').then(r => r.data),

  getHistory: (limit = 50) =>
    api.get<{ history: HistoryItem[] }>('/history', { params: { limit } }).then(r => r.data),

  getFlagged: (limit = 50) =>
    api.get<{ flagged: FlaggedComment[] }>('/flagged', { params: { limit } }).then(r => r.data),

  dismissFlagged: (commentId: string) =>
    api.delete(`/flagged/${commentId}`).then(r => r.data),
};
