"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  PhotoIcon, 
  VideoCameraIcon, 
  DocumentTextIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  TrashIcon,
  PencilIcon,
  EyeIcon,
  CloudArrowUpIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import Image from "next/image";
import { contentApi, Content, ContentType, ContentStatus } from "@/lib/content-api";

const contentTypeIcons = {
  [ContentType.IMAGE]: PhotoIcon,
  [ContentType.VIDEO]: VideoCameraIcon,
  [ContentType.TEXT]: DocumentTextIcon,
  [ContentType.CAROUSEL]: PhotoIcon,
  [ContentType.STORY]: PhotoIcon,
  [ContentType.REEL]: VideoCameraIcon,
};

const statusColors = {
  [ContentStatus.DRAFT]: "bg-gray-100 text-gray-800",
  [ContentStatus.SCHEDULED]: "bg-blue-100 text-blue-800",
  [ContentStatus.PUBLISHED]: "bg-green-100 text-green-800",
  [ContentStatus.ARCHIVED]: "bg-yellow-100 text-yellow-800",
};

interface ContentFilters {
  search: string;
  content_type?: ContentType;
  status?: ContentStatus;
  page: number;
  size: number;
}

export default function ContentPage() {
  const [filters, setFilters] = useState<ContentFilters>({
    search: "",
    page: 1,
    size: 12,
  });
  
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const queryClient = useQueryClient();
  
  // Fetch content with filters
  const { data: contentData, isLoading, error } = useQuery({
    queryKey: ['content', filters],
    queryFn: () => contentApi.getContent(filters),
  });
  
  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ file, metadata }: { 
      file: File; 
      metadata: {
        title: string;
        description?: string;
        content_type: ContentType;
        tags?: string[];
        hashtags?: string[];
      }
    }) => {
      return contentApi.uploadFile(file, setUploadProgress);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
      setShowUploadModal(false);
      setUploadProgress(0);
    },
  });
  
  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: contentApi.deleteContent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
    },
  });
  
  const handleUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const file = formData.get('file') as File;
    const title = formData.get('title') as string;
    const description = formData.get('description') as string;
    const content_type = formData.get('content_type') as ContentType;
    const tags = (formData.get('tags') as string)?.split(',').map(t => t.trim()).filter(Boolean) || [];
    const hashtags = (formData.get('hashtags') as string)?.split(',').map(t => t.trim()).filter(Boolean) || [];
    
    if (!file || !title) return;
    
    uploadMutation.mutate({
      file,
      metadata: { title, description, content_type, tags, hashtags }
    });
  };
  
  const handleFilterChange = (newFilters: Partial<ContentFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
  };
  
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Content Library
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Manage your media content and create new posts across all platforms.
            </p>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Upload Content
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search content..."
                value={filters.search}
                onChange={(e) => handleFilterChange({ search: e.target.value })}
                className="pl-10 w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            
            {/* Content Type Filter */}
            <select
              value={filters.content_type || ""}
              onChange={(e) => handleFilterChange({ content_type: e.target.value as ContentType || undefined })}
              className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              {Object.values(ContentType).map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            
            {/* Status Filter */}
            <select
              value={filters.status || ""}
              onChange={(e) => handleFilterChange({ status: e.target.value as ContentStatus || undefined })}
              className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              {Object.values(ContentStatus).map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
            
            {/* Page Size */}
            <select
              value={filters.size}
              onChange={(e) => handleFilterChange({ size: parseInt(e.target.value) })}
              className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value={12}>12 per page</option>
              <option value={24}>24 per page</option>
              <option value={48}>48 per page</option>
            </select>
          </div>
        </div>

        {/* Content Grid */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Loading content...</p>
            </div>
          ) : error ? (
            <div className="p-8 text-center">
              <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto" />
              <p className="mt-2 text-red-600">Error loading content</p>
            </div>
          ) : !contentData?.contents.length ? (
            <div className="text-center py-12">
              <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No content yet</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Get started by uploading your first piece of content.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <CloudArrowUpIcon className="h-5 w-5 mr-2" />
                  Upload Content
                </button>
              </div>
            </div>
          ) : (
            <div className="p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {contentData.contents.map((content) => {
                  const Icon = contentTypeIcons[content.content_type];
                  return (
                    <div
                      key={content.id}
                      className="group relative bg-gray-50 dark:bg-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
                    >
                      {/* Thumbnail/Icon */}
                      <div className="aspect-video bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
                        {content.thumbnail_url ? (
                          <Image
                            src={content.thumbnail_url}
                            alt={content.title}
                            width={300}
                            height={200}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <Icon className="h-12 w-12 text-gray-400" />
                        )}
                      </div>
                      
                      {/* Content Info */}
                      <div className="p-4">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {content.title}
                        </h3>
                        {content.description && (
                          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                            {content.description}
                          </p>
                        )}
                        
                        {/* Status and Type */}
                        <div className="mt-2 flex items-center justify-between">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColors[content.status]}`}>
                            {content.status}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {content.content_type}
                          </span>
                        </div>
                        
                        {/* Actions */}
                        <div className="mt-3 flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            className="p-1 text-gray-400 hover:text-blue-600"
                            title="View"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                          <button
                            className="p-1 text-gray-400 hover:text-green-600"
                            title="Edit"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => deleteMutation.mutate(content.id)}
                            className="p-1 text-gray-400 hover:text-red-600"
                            title="Delete"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* Pagination */}
              {contentData && Math.ceil(contentData.total / filters.size) > 1 && (
                <div className="mt-6 flex items-center justify-between">
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    Showing <span className="font-medium">{(filters.page - 1) * filters.size + 1}</span> to{' '}
                    <span className="font-medium">
                      {Math.min(filters.page * filters.size, contentData.total)}
                    </span>{' '}
                    of <span className="font-medium">{contentData.total}</span> results
                  </p>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleFilterChange({ page: filters.page - 1 })}
                      disabled={filters.page <= 1}
                      className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => handleFilterChange({ page: filters.page + 1 })}
                      disabled={filters.page >= Math.ceil(contentData.total / filters.size)}
                      className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Upload Content
              </h3>
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    File
                  </label>
                  <input
                    type="file"
                    name="file"
                    required
                    accept="image/*,video/*"
                    className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Title
                  </label>
                  <input
                    type="text"
                    name="title"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Description
                  </label>
                  <textarea
                    name="description"
                    rows={3}
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Content Type
                  </label>
                  <select
                    name="content_type"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    {Object.values(ContentType).map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="tags"
                    placeholder="social media, marketing, content"
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Hashtags (comma-separated)
                  </label>
                  <input
                    type="text"
                    name="hashtags"
                    placeholder="#socialmedia, #marketing, #content"
                    className="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                
                {uploadProgress > 0 && (
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Upload Progress</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploadMutation.isPending}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
                  >
                    {uploadMutation.isPending ? 'Uploading...' : 'Upload'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}