'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  PlusIcon, 
  MagnifyingGlassIcon,
  FolderIcon,
  BookmarkIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  TagIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { curationAPI, CurationCollection, CurationItem, InspirationBoardSummary } from '@/lib/curation-api';

interface CreateCollectionData {
  name: string;
  description?: string;
  collection_type: string;
  is_public?: boolean;
  color_theme?: string;
  tags?: string[];
  auto_curate_trends?: boolean;
  auto_curate_keywords?: string[];
}

export default function InspirationBoardPage() {
  const [collections, setCollections] = useState<CurationCollection[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<CurationCollection | null>(null);
  const [items, setItems] = useState<CurationItem[]>([]);
  const [summary, setSummary] = useState<InspirationBoardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateCollection, setShowCreateCollection] = useState(false);

  const loadCollectionItems = useCallback(async (collectionId: number) => {
    try {
      const itemsData = await curationAPI.getCollectionItems(collectionId, {
        search: searchTerm || undefined
      });
      setItems(itemsData);
    } catch (error) {
      console.error('Error loading collection items:', error);
    }
  }, [searchTerm]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [collectionsData, summaryData] = await Promise.all([
        curationAPI.getCollections(),
        curationAPI.getInspirationBoardSummary()
      ]);
      
      setCollections(collectionsData);
      setSummary(summaryData);
      
      if (collectionsData.length > 0 && !selectedCollection) {
        setSelectedCollection(collectionsData[0]);
        loadCollectionItems(collectionsData[0].id);
      }
    } catch (error) {
      console.error('Error loading inspiration board data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedCollection, loadCollectionItems]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCollectionSelect = (collection: CurationCollection) => {
    setSelectedCollection(collection);
    loadCollectionItems(collection.id);
  };

  const handleCreateCollection = async (collectionData: CreateCollectionData) => {
    try {
      const newCollection = await curationAPI.createCollection(collectionData);
      setCollections([...collections, newCollection]);
      setShowCreateCollection(false);
    } catch (error) {
      console.error('Error creating collection:', error);
    }
  };

  const getCollectionTypeIcon = (type: string) => {
    switch (type) {
      case 'inspiration_board':
        return BookmarkIcon;
      case 'template_collection':
        return FolderIcon;
      case 'trend_watchlist':
        return ArrowTrendingUpIcon;
      case 'content_ideas':
        return EyeIcon;
      default:
        return FolderIcon;
    }
  };

  const getItemTypeColor = (type: string) => {
    const colors = {
      trend: 'bg-red-100 text-red-800',
      hashtag: 'bg-blue-100 text-blue-800',
      audio_track: 'bg-purple-100 text-purple-800',
      content_idea: 'bg-green-100 text-green-800',
      template: 'bg-yellow-100 text-yellow-800',
      inspiration_post: 'bg-pink-100 text-pink-800',
      competitor_content: 'bg-gray-100 text-gray-800'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Inspiration Board</h1>
              <p className="mt-2 text-gray-600">Curate and organize your content ideas</p>
            </div>
            <button
              onClick={() => setShowCreateCollection(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              New Collection
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <FolderIcon className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Collections</p>
                  <p className="text-2xl font-semibold text-gray-900">{summary.total_collections}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <BookmarkIcon className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Items</p>
                  <p className="text-2xl font-semibold text-gray-900">{summary.total_items}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <ArrowTrendingUpIcon className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Trend Watches</p>
                  <p className="text-2xl font-semibold text-gray-900">{summary.active_trend_watches}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <ClockIcon className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Unread Alerts</p>
                  <p className="text-2xl font-semibold text-gray-900">{summary.unread_alerts}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Collections Sidebar */}
          <div className="w-full lg:w-1/4">
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Collections</h3>
                <div className="space-y-2">
                  {collections.map((collection) => {
                    const IconComponent = getCollectionTypeIcon(collection.collection_type);
                    return (
                      <button
                        key={collection.id}
                        onClick={() => handleCollectionSelect(collection)}
                        className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          selectedCollection?.id === collection.id
                            ? 'bg-blue-100 text-blue-700'
                            : 'text-gray-600 hover:bg-gray-100'
                        }`}
                      >
                        <div className="flex items-center">
                          <IconComponent className="h-5 w-5 mr-3" />
                          <div className="flex-1">
                            <p className="font-medium">{collection.name}</p>
                            <p className="text-xs text-gray-500">{collection.items_count} items</p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Items Grid */}
          <div className="flex-1">
            {selectedCollection && (
              <div className="bg-white rounded-lg shadow">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900">
                      {selectedCollection.name}
                    </h3>
                    <div className="flex items-center space-x-4">
                      <div className="relative">
                        <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                          type="text"
                          placeholder="Search items..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <button
                        onClick={() => {/* Handle add item */}}
                        className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-blue-600 bg-blue-100 hover:bg-blue-200"
                      >
                        <PlusIcon className="h-4 w-4 mr-1" />
                        Add Item
                      </button>
                    </div>
                  </div>

                  {items.length === 0 ? (
                    <div className="text-center py-12">
                      <BookmarkIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No items yet</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Start curating content by adding your first item.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {items.map((item) => (
                        <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start mb-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getItemTypeColor(item.item_type)}`}>
                              {item.item_type.replace('_', ' ')}
                            </span>
                            {item.viral_potential_score && (
                              <span className="text-xs font-medium text-green-600">
                                {item.viral_potential_score}/10 viral score
                              </span>
                            )}
                          </div>
                          
                          <h4 className="text-sm font-medium text-gray-900 mb-2">{item.title}</h4>
                          
                          {item.description && (
                            <p className="text-xs text-gray-600 mb-2 line-clamp-2">{item.description}</p>
                          )}
                          
                          {item.user_tags && item.user_tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {item.user_tags.slice(0, 3).map((tag, index) => (
                                <span key={index} className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                                  <TagIcon className="h-3 w-3 mr-1" />
                                  {tag}
                                </span>
                              ))}
                              {item.user_tags.length > 3 && (
                                <span className="text-xs text-gray-500">+{item.user_tags.length - 3} more</span>
                              )}
                            </div>
                          )}
                          
                          <div className="flex justify-between items-center text-xs text-gray-500">
                            <span>Used {item.times_used} times</span>
                            <span>{new Date(item.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Collection Modal */}
      {showCreateCollection && (
        <CreateCollectionModal
          onClose={() => setShowCreateCollection(false)}
          onSubmit={handleCreateCollection}
        />
      )}
    </div>
  );
}

function CreateCollectionModal({ 
  onClose, 
  onSubmit 
}: { 
  onClose: () => void; 
  onSubmit: (data: CreateCollectionData) => void; 
}) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    collection_type: 'inspiration_board',
    is_public: false,
    color_theme: '',
    tags: '',
    auto_curate_trends: false,
    auto_curate_keywords: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      ...formData,
      tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : [],
      auto_curate_keywords: formData.auto_curate_keywords ? 
        formData.auto_curate_keywords.split(',').map(keyword => keyword.trim()) : []
    };
    onSubmit(data);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Collection</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Type</label>
              <select
                value={formData.collection_type}
                onChange={(e) => setFormData({ ...formData, collection_type: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="inspiration_board">Inspiration Board</option>
                <option value="template_collection">Template Collection</option>
                <option value="trend_watchlist">Trend Watchlist</option>
                <option value="content_ideas">Content Ideas</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Tags (comma-separated)</label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                placeholder="viral, trending, tech"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.auto_curate_trends}
                onChange={(e) => setFormData({ ...formData, auto_curate_trends: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Auto-curate trending content
              </label>
            </div>
            
            {formData.auto_curate_trends && (
              <div>
                <label className="block text-sm font-medium text-gray-700">Auto-curate Keywords</label>
                <input
                  type="text"
                  value={formData.auto_curate_keywords}
                  onChange={(e) => setFormData({ ...formData, auto_curate_keywords: e.target.value })}
                  placeholder="AI, technology, viral"
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            )}
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Create Collection
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}