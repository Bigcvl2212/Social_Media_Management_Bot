import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const growthApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/growth`,
  headers: { 'Content-Type': 'application/json' },
});

const spyApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/competitor-spy`,
  headers: { 'Content-Type': 'application/json' },
});

// ── Growth Types ──
export interface GrowthSnapshot {
  followers: number;
  engagement_rate: number;
  reach: number;
  impressions: number;
  [key: string]: unknown;
}

export interface GrowthDashboard {
  latest: GrowthSnapshot | null;
  milestones_hit: number;
  trend_direction: string;
}

export interface TrendPoint {
  date: string;
  followers: number;
  engagement_rate: number;
  reach: number;
}

export interface WeeklyReport {
  period: string;
  current: Record<string, number>;
  previous: Record<string, number>;
  changes: Record<string, number>;
  highlights: string[];
}

export interface Milestone {
  id: string;
  metric: string;
  target: number;
  achieved: boolean;
  achieved_at: string | null;
}

export interface GrowthGoals {
  [key: string]: unknown;
}

// ── Competitor Types ──
export interface Competitor {
  id: string;
  name: string;
  platform_url: string;
  notes: string;
  scans: Array<{ timestamp: string; insights: Record<string, unknown> }>;
  added_at: string;
}

export interface SpyDashboard {
  total_competitors: number;
  recent_scans: number;
  insights_summary: string;
}

// ── Growth API ──
export const growthTrackerApi = {
  recordSnapshot: (data: GrowthSnapshot) =>
    growthApi.post('/snapshot', data).then(r => r.data),

  getDashboard: () =>
    growthApi.get<GrowthDashboard>('/dashboard').then(r => r.data),

  getTrend: (days = 30) =>
    growthApi.get<{ trend: TrendPoint[] }>('/trend', { params: { days } }).then(r => r.data),

  getReport: () =>
    growthApi.get<{ report: WeeklyReport }>('/report').then(r => r.data),

  getMilestones: () =>
    growthApi.get<{ milestones: Milestone[] }>('/milestones').then(r => r.data),

  getGoals: () =>
    growthApi.get<{ goals: GrowthGoals }>('/goals').then(r => r.data),

  updateGoals: (goals: GrowthGoals) =>
    growthApi.put<{ goals: GrowthGoals }>('/goals', goals).then(r => r.data),
};

// ── Competitor Spy API ──
export const competitorSpyApi = {
  listCompetitors: () =>
    spyApi.get<{ competitors: Competitor[] }>('/competitors').then(r => r.data),

  addCompetitor: (data: { name: string; platform_url?: string; notes?: string }) =>
    spyApi.post<{ competitor: Competitor }>('/competitors', data).then(r => r.data),

  getCompetitor: (id: string) =>
    spyApi.get<{ competitor: Competitor }>(`/competitors/${id}`).then(r => r.data),

  updateCompetitor: (id: string, data: Partial<Competitor>) =>
    spyApi.put<{ competitor: Competitor }>(`/competitors/${id}`, data).then(r => r.data),

  deleteCompetitor: (id: string) =>
    spyApi.delete(`/competitors/${id}`).then(r => r.data),

  scanCompetitor: (id: string, posts: Array<{ text: string; engagement?: number }>) =>
    spyApi.post(`/competitors/${id}/scan`, { posts }).then(r => r.data),

  generateCounterPost: (id: string, brandPrompt?: string) =>
    spyApi.post(`/competitors/${id}/counter-post`, { brand_prompt: brandPrompt }).then(r => r.data),

  getDashboard: () =>
    spyApi.get<SpyDashboard>('/dashboard').then(r => r.data),

  getInsights: () =>
    spyApi.get('/insights').then(r => r.data),
};
