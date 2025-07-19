"use client";

import { useState } from "react";
import { format } from "date-fns";
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PencilIcon,
  TrashIcon
} from "@heroicons/react/24/outline";
import { clsx } from "clsx";

interface ScheduledPost {
  id: string;
  title: string;
  platform: string;
  scheduledDate: Date;
  status: "scheduled" | "published" | "failed";
  content: string;
  imageUrl?: string;
}

interface PostsListProps {
  scheduledPosts: ScheduledPost[];
}

const statusIcons = {
  scheduled: ClockIcon,
  published: CheckCircleIcon,
  failed: ExclamationTriangleIcon,
};

const statusColors = {
  scheduled: "text-yellow-500 bg-yellow-500/20",
  published: "text-green-500 bg-green-500/20", 
  failed: "text-red-500 bg-red-500/20",
};

const platformIcons = {
  Instagram: "IG",
  TikTok: "TT",
  YouTube: "YT",
  Twitter: "X",
  Facebook: "FB",
  LinkedIn: "LI",
};

export function PostsList({ scheduledPosts }: PostsListProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPlatform, setFilterPlatform] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Filter posts based on search and filters
  const filteredPosts = scheduledPosts.filter((post) => {
    const matchesSearch = post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         post.content.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPlatform = filterPlatform === "all" || post.platform === filterPlatform;
    const matchesStatus = filterStatus === "all" || post.status === filterStatus;
    
    return matchesSearch && matchesPlatform && matchesStatus;
  });

  // Sort by scheduled date
  const sortedPosts = filteredPosts.sort((a, b) => 
    new Date(a.scheduledDate).getTime() - new Date(b.scheduledDate).getTime()
  );

  const platforms = [...new Set(scheduledPosts.map(post => post.platform))];

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="glass rounded-xl p-6 border border-white/10">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search posts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 glass-strong rounded-lg border border-white/10 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Platform Filter */}
          <div className="relative">
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="appearance-none bg-transparent glass-strong rounded-lg border border-white/10 px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-8"
            >
              <option value="all">All Platforms</option>
              {platforms.map((platform) => (
                <option key={platform} value={platform}>{platform}</option>
              ))}
            </select>
            <FunnelIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>

          {/* Status Filter */}
          <div className="relative">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="appearance-none bg-transparent glass-strong rounded-lg border border-white/10 px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-8"
            >
              <option value="all">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="published">Published</option>
              <option value="failed">Failed</option>
            </select>
            <FunnelIcon className="absolute right-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* Posts List */}
      <div className="glass rounded-xl border border-white/10 overflow-hidden">
        {sortedPosts.length === 0 ? (
          <div className="p-12 text-center">
            <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-white mb-2">No posts found</h3>
            <p className="text-gray-400">
              {searchQuery || filterPlatform !== "all" || filterStatus !== "all"
                ? "Try adjusting your filters or search query."
                : "You haven't scheduled any posts yet. Create your first post to get started!"}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-white/10">
            {sortedPosts.map((post) => {
              const StatusIcon = statusIcons[post.status];
              
              return (
                <div key={post.id} className="p-6 hover:bg-white/5 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      {/* Header */}
                      <div className="flex items-center gap-3 mb-3">
                        {/* Platform Badge */}
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                            {platformIcons[post.platform as keyof typeof platformIcons] || post.platform[0]}
                          </div>
                          <span className="text-sm font-medium text-gray-300">{post.platform}</span>
                        </div>

                        {/* Status Badge */}
                        <div className={clsx(
                          "flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium",
                          statusColors[post.status]
                        )}>
                          <StatusIcon className="h-3 w-3" />
                          {post.status.charAt(0).toUpperCase() + post.status.slice(1)}
                        </div>

                        {/* Scheduled Time */}
                        <span className="text-sm text-gray-400">
                          {format(new Date(post.scheduledDate), "MMM d, yyyy 'at' h:mm a")}
                        </span>
                      </div>

                      {/* Title */}
                      <h3 className="text-lg font-semibold text-white mb-2 truncate">
                        {post.title}
                      </h3>

                      {/* Content Preview */}
                      <p className="text-gray-300 text-sm line-clamp-2 mb-4">
                        {post.content}
                      </p>

                      {/* Image Preview */}
                      {post.imageUrl && (
                        <div className="w-16 h-16 rounded-lg bg-gray-700 overflow-hidden">
                          <img 
                            src={post.imageUrl} 
                            alt="Post preview" 
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 ml-4">
                      <button className="p-2 rounded-lg glass-strong hover:bg-white/20 transition-colors text-gray-300 hover:text-white">
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button className="p-2 rounded-lg glass-strong hover:bg-red-500/20 transition-colors text-gray-300 hover:text-red-400">
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Results Summary */}
      {sortedPosts.length > 0 && (
        <div className="text-center text-sm text-gray-400">
          Showing {sortedPosts.length} of {scheduledPosts.length} posts
        </div>
      )}
    </div>
  );
}