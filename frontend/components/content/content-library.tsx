"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  MagnifyingGlassIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon,
  StarIcon,
  TrashIcon,
  PencilIcon,
  CheckIcon,
} from "@heroicons/react/24/outline";

export function ContentLibrary() {
  const [filters, setFilters] = useState({
    search: "",
    type: "all" as "all" | "image" | "video" | "text",
    status: "all" as "all" | "draft" | "scheduled" | "published",
    page: 1,
  });

  const { data: library, isLoading } = useQuery({
    queryKey: ["content-library", filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: filters.page.toString(),
        type: filters.type,
        status: filters.status,
        ...(filters.search && { search: filters.search }),
      });
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/content/library?${params}`);
      if (!response.ok) throw new Error("Failed to fetch library");
      return response.json();
    },
  });

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search content..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              className="pl-10 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Type Filter */}
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value as any, page: 1 })}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="all">All Types</option>
            <option value="image">Images</option>
            <option value="video">Videos</option>
            <option value="text">Text</option>
          </select>

          {/* Status Filter */}
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value as any, page: 1 })}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="published">Published</option>
          </select>
        </div>
      </div>

      {/* Library Grid */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {library?.items?.map((item: any) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface ContentCardProps {
  item: {
    id: string;
    title: string;
    type: string;
    thumbnail?: string;
    status: string;
    viralScore?: number;
  };
}

function ContentCard({ item }: ContentCardProps) {
  const getIcon = (type: string) => {
    if (type === "video") return VideoCameraIcon;
    if (type === "image") return PhotoIcon;
    return DocumentTextIcon;
  };

  const Icon = getIcon(item.type);

  return (
    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden group hover:shadow-lg transition-shadow">
      <div className="aspect-square bg-gray-200 dark:bg-gray-600 flex items-center justify-center relative">
        {item.thumbnail ? (
          <img src={item.thumbnail} alt={item.title} className="w-full h-full object-cover" />
        ) : (
          <Icon className="h-12 w-12 text-gray-400" />
        )}
        
        {/* Status Badge */}
        <div className="absolute top-2 right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
          {item.status}
        </div>

        {/* Viral Score */}
        {item.viralScore && (
          <div className="absolute bottom-2 left-2 bg-gradient-to-r from-orange-600 to-pink-600 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
            <StarIcon className="h-3 w-3" />
            {item.viralScore}/10
          </div>
        )}

        {/* Hover Actions */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button className="bg-white text-gray-900 p-2 rounded-lg hover:bg-gray-100">
            <PencilIcon className="h-5 w-5" />
          </button>
          <button className="bg-white text-gray-900 p-2 rounded-lg hover:bg-gray-100">
            <CheckIcon className="h-5 w-5" />
          </button>
          <button className="bg-white text-gray-900 p-2 rounded-lg hover:bg-gray-100">
            <TrashIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
      <div className="p-3">
        <p className="font-medium text-gray-900 dark:text-white text-sm truncate">
          {item.title}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">{item.type}</p>
      </div>
    </div>
  );
}
