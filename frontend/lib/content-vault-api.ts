import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/content-vault`,
  headers: { 'Content-Type': 'application/json' },
});

export interface VaultAsset {
  id: string;
  filename: string;
  media_type: string;
  category: string;
  tags: string[];
  favorite: boolean;
  file_path: string;
  thumbnail: string | null;
  uploaded_at: string;
  metadata: Record<string, unknown>;
}

export interface VaultStats {
  total: number;
  images: number;
  videos: number;
  favorites: number;
  categories: Record<string, number>;
}

export const contentVaultApi = {
  upload: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return axios.post<{ status: string; asset: VaultAsset }>(
      `${API_BASE_URL}/api/v1/content-vault/upload`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    ).then(r => r.data);
  },

  listAssets: (params?: { category?: string; tag?: string; media_type?: string; limit?: number }) =>
    api.get<{ assets: VaultAsset[] }>('/assets', { params }).then(r => r.data),

  getAsset: (id: string) =>
    api.get<{ asset: VaultAsset }>(`/assets/${id}`).then(r => r.data),

  deleteAsset: (id: string) =>
    api.delete(`/assets/${id}`).then(r => r.data),

  updateAsset: (id: string, data: Partial<VaultAsset>) =>
    api.put<{ asset: VaultAsset }>(`/assets/${id}`, data).then(r => r.data),

  toggleFavorite: (id: string) =>
    api.post<{ asset: VaultAsset }>(`/assets/${id}/favorite`).then(r => r.data),

  retag: (id: string) =>
    api.post<{ status: string; asset: VaultAsset }>(`/assets/${id}/retag`).then(r => r.data),

  search: (q: string) =>
    api.get<{ assets: VaultAsset[] }>('/search', { params: { q } }).then(r => r.data),

  getStats: () =>
    api.get<VaultStats>('/stats').then(r => r.data),

  thumbnailUrl: (filename: string) =>
    `${API_BASE_URL}/api/v1/content-vault/thumbnail/${filename}`,
};
