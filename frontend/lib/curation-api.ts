/**
 * Content Curation API Client
 * Handles communication with the backend curation endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CurationCollection {
  id: number;
  name: string;
  description?: string;
  collection_type: 'inspiration_board' | 'template_collection' | 'trend_watchlist' | 'content_ideas';
  is_public: boolean;
  color_theme?: string;
  tags?: string[];
  auto_curate_trends: boolean;
  auto_curate_keywords?: string[];
  user_id: number;
  created_at: string;
  updated_at?: string;
  items_count: number;
}

export interface CurationItem {
  id: number;
  collection_id: number;
  item_type: 'trend' | 'hashtag' | 'audio_track' | 'content_idea' | 'template' | 'inspiration_post' | 'competitor_content';
  title: string;
  description?: string;
  status: 'saved' | 'in_progress' | 'used' | 'archived';
  source_url?: string;
  source_platform?: string;
  thumbnail_url?: string;
  item_data?: any;
  user_notes?: string;
  user_rating?: number;
  user_tags?: string[];
  ai_insights?: any;
  viral_potential_score?: number;
  times_used: number;
  last_used_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface TrendWatch {
  id: number;
  name: string;
  description?: string;
  keywords: string[];
  platforms: string[];
  regions?: string[];
  is_active: boolean;
  alert_threshold: number;
  notification_frequency: 'hourly' | 'daily' | 'weekly';
  auto_save_to_collection_id?: number;
  auto_save_threshold: number;
  user_id: number;
  last_check_at?: string;
  total_alerts_sent: number;
  created_at: string;
  updated_at?: string;
}

export interface TrendAlert {
  id: number;
  trend_watch_id: number;
  trend_name: string;
  platform: string;
  alert_type: string;
  current_volume?: number;
  growth_rate?: string;
  trend_data?: any;
  is_read: boolean;
  is_dismissed: boolean;
  auto_saved_to_collection: boolean;
  created_at: string;
  read_at?: string;
}

export interface InspirationBoardSummary {
  total_collections: number;
  total_items: number;
  trending_items: CurationItem[];
  recent_additions: CurationItem[];
  active_trend_watches: number;
  unread_alerts: number;
  collections_by_type: Record<string, number>;
}

class CurationAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/v1/curation`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authentication token if available
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        };
      }
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  // Collection Management
  async createCollection(data: {
    name: string;
    description?: string;
    collection_type: string;
    is_public?: boolean;
    color_theme?: string;
    tags?: string[];
    auto_curate_trends?: boolean;
    auto_curate_keywords?: string[];
  }): Promise<CurationCollection> {
    return this.request('/collections', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCollections(params?: {
    collection_type?: string;
    page?: number;
    size?: number;
  }): Promise<CurationCollection[]> {
    const queryParams = new URLSearchParams();
    if (params?.collection_type) queryParams.set('collection_type', params.collection_type);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.size) queryParams.set('size', params.size.toString());

    const endpoint = queryParams.toString() ? `/collections?${queryParams}` : '/collections';
    return this.request(endpoint);
  }

  async getCollection(id: number): Promise<CurationCollection> {
    return this.request(`/collections/${id}`);
  }

  async updateCollection(id: number, data: Partial<CurationCollection>): Promise<CurationCollection> {
    return this.request(`/collections/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteCollection(id: number): Promise<void> {
    return this.request(`/collections/${id}`, {
      method: 'DELETE',
    });
  }

  // Item Management
  async addItem(data: {
    collection_id: number;
    item_type: string;
    title: string;
    description?: string;
    source_url?: string;
    source_platform?: string;
    thumbnail_url?: string;
    item_data?: any;
    user_notes?: string;
    user_rating?: number;
    user_tags?: string[];
  }): Promise<CurationItem> {
    return this.request('/items', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getCollectionItems(
    collectionId: number,
    params?: {
      item_type?: string;
      status?: string;
      search?: string;
      page?: number;
      size?: number;
    }
  ): Promise<CurationItem[]> {
    const queryParams = new URLSearchParams();
    if (params?.item_type) queryParams.set('item_type', params.item_type);
    if (params?.status) queryParams.set('status', params.status);
    if (params?.search) queryParams.set('search', params.search);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.size) queryParams.set('size', params.size.toString());

    const endpoint = queryParams.toString() 
      ? `/collections/${collectionId}/items?${queryParams}` 
      : `/collections/${collectionId}/items`;
    
    return this.request(endpoint);
  }

  async updateItem(id: number, data: Partial<CurationItem>): Promise<CurationItem> {
    return this.request(`/items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteItem(id: number): Promise<void> {
    return this.request(`/items/${id}`, {
      method: 'DELETE',
    });
  }

  async markItemAsUsed(id: number): Promise<CurationItem> {
    return this.request(`/items/${id}/mark-used`, {
      method: 'POST',
    });
  }

  // Quick Save
  async quickSave(data: {
    url: string;
    collection_id: number;
    title?: string;
    notes?: string;
    tags?: string[];
  }): Promise<{ success: boolean; item_id?: number; message: string }> {
    return this.request('/quick-save', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Trend Monitoring
  async createTrendWatch(data: {
    name: string;
    description?: string;
    keywords: string[];
    platforms: string[];
    regions?: string[];
    is_active?: boolean;
    alert_threshold?: number;
    notification_frequency?: string;
    auto_save_to_collection_id?: number;
    auto_save_threshold?: number;
  }): Promise<TrendWatch> {
    return this.request('/trend-watches', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTrendWatches(activeOnly?: boolean): Promise<TrendWatch[]> {
    const endpoint = activeOnly ? '/trend-watches?active_only=true' : '/trend-watches';
    return this.request(endpoint);
  }

  async getTrendAlerts(params?: {
    unread_only?: boolean;
    page?: number;
    size?: number;
  }): Promise<TrendAlert[]> {
    const queryParams = new URLSearchParams();
    if (params?.unread_only) queryParams.set('unread_only', 'true');
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.size) queryParams.set('size', params.size.toString());

    const endpoint = queryParams.toString() ? `/trend-alerts?${queryParams}` : '/trend-alerts';
    return this.request(endpoint);
  }

  async markAlertAsRead(id: number): Promise<void> {
    return this.request(`/trend-alerts/${id}/mark-read`, {
      method: 'POST',
    });
  }

  // Real-time Monitoring
  async getRealtimeHashtags(platforms: string[]): Promise<any> {
    const queryParams = new URLSearchParams();
    platforms.forEach(platform => queryParams.append('platforms', platform));
    
    return this.request(`/realtime/hashtags?${queryParams}`);
  }

  async getRealtimeSounds(platforms: string[]): Promise<any> {
    const queryParams = new URLSearchParams();
    platforms.forEach(platform => queryParams.append('platforms', platform));
    
    return this.request(`/realtime/sounds?${queryParams}`);
  }

  async getViralSpikes(platform: string, threshold?: number): Promise<any> {
    const queryParams = new URLSearchParams();
    queryParams.set('platform', platform);
    if (threshold) queryParams.set('threshold', threshold.toString());
    
    return this.request(`/realtime/viral-spikes?${queryParams}`);
  }

  async getPlatformInsights(platform: string): Promise<any> {
    return this.request(`/realtime/platform-insights?platform=${platform}`);
  }

  async createSmartAlerts(keywords: string[], platforms: string[]): Promise<any> {
    const queryParams = new URLSearchParams();
    keywords.forEach(keyword => queryParams.append('keywords', keyword));
    platforms.forEach(platform => queryParams.append('platforms', platform));
    
    return this.request(`/realtime/smart-alerts?${queryParams}`, {
      method: 'POST',
    });
  }

  // Dashboard Summary
  async getInspirationBoardSummary(): Promise<InspirationBoardSummary> {
    return this.request('/inspiration-board/summary');
  }

  // Content Discovery
  async discoverTrendingContent(data: {
    platforms: string[];
    keywords?: string[];
    content_types?: string[];
    region?: string;
    time_range?: string;
  }): Promise<any[]> {
    return this.request('/discover-trending', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Bulk Operations
  async bulkOperationItems(data: {
    item_ids: number[];
    operation: 'move' | 'delete' | 'update_status' | 'tag';
    target_collection_id?: number;
    new_status?: string;
    tags_to_add?: string[];
    tags_to_remove?: string[];
  }): Promise<{ success: boolean; processed_items: number; failed_items: number; errors?: string[] }> {
    return this.request('/items/bulk-operation', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const curationAPI = new CurationAPI();