"use client";

import { useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useDropzone } from "react-dropzone";
import {
  ArchiveBoxIcon,
  PhotoIcon,
  VideoCameraIcon,
  HeartIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  TrashIcon,
  StarIcon,
  TagIcon,
} from "@heroicons/react/24/outline";
import { HeartIcon as HeartSolid, StarIcon as StarSolid } from "@heroicons/react/24/solid";
import { contentVaultApi, type VaultAsset } from "@/lib/content-vault-api";

export function VaultDashboard() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("");

  const { data: statsData } = useQuery({
    queryKey: ["vault-stats"],
    queryFn: contentVaultApi.getStats,
  });

  const { data: assetsData, isLoading } = useQuery({
    queryKey: ["vault-assets", filterType],
    queryFn: () => contentVaultApi.listAssets(filterType ? { media_type: filterType } : undefined),
  });

  const { data: searchData } = useQuery({
    queryKey: ["vault-search", searchQuery],
    queryFn: () => contentVaultApi.search(searchQuery),
    enabled: searchQuery.length > 0,
  });

  const uploadMutation = useMutation({
    mutationFn: contentVaultApi.upload,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vault-assets"] });
      queryClient.invalidateQueries({ queryKey: ["vault-stats"] });
    },
  });

  const favMutation = useMutation({
    mutationFn: contentVaultApi.toggleFavorite,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["vault-assets"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: contentVaultApi.deleteAsset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vault-assets"] });
      queryClient.invalidateQueries({ queryKey: ["vault-stats"] });
    },
  });

  const retagMutation = useMutation({
    mutationFn: contentVaultApi.retag,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["vault-assets"] }),
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(file => uploadMutation.mutate(file));
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [], "video/*": [] },
  });

  const displayAssets = searchQuery.length > 0 ? searchData?.assets : assetsData?.assets;
  const stats = statsData;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Content Vault</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">Your AI-tagged media library. Upload, search, and organize all your content.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard icon={ArchiveBoxIcon} label="Total Assets" value={String(stats?.total || 0)} color="blue" />
        <KpiCard icon={PhotoIcon} label="Images" value={String(stats?.images || 0)} color="green" />
        <KpiCard icon={VideoCameraIcon} label="Videos" value={String(stats?.videos || 0)} color="purple" />
        <KpiCard icon={HeartIcon} label="Favorites" value={String(stats?.favorites || 0)} color="pink" />
      </div>

      {/* Upload Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
            : "border-gray-300 dark:border-gray-600 hover:border-purple-400"
        }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="h-12 w-12 mx-auto text-gray-400 mb-3" />
        {uploadMutation.isPending ? (
          <p className="text-sm text-purple-600 dark:text-purple-400">Uploading & AI-tagging...</p>
        ) : isDragActive ? (
          <p className="text-sm text-purple-600 dark:text-purple-400">Drop files here...</p>
        ) : (
          <p className="text-sm text-gray-500 dark:text-gray-400">Drag & drop images or videos, or click to browse</p>
        )}
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm text-gray-900 dark:text-white"
            placeholder="Search by tags, description, or filename..."
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm text-gray-900 dark:text-white"
        >
          <option value="">All Types</option>
          <option value="image">Images</option>
          <option value="video">Videos</option>
        </select>
      </div>

      {/* Asset Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <ArrowPathIcon className="h-8 w-8 animate-spin text-purple-500" />
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {(displayAssets || []).map((asset) => (
            <AssetCard
              key={asset.id}
              asset={asset}
              onFavorite={() => favMutation.mutate(asset.id)}
              onDelete={() => deleteMutation.mutate(asset.id)}
              onRetag={() => retagMutation.mutate(asset.id)}
            />
          ))}
          {(displayAssets || []).length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
              No assets yet. Upload some content to get started!
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function AssetCard({ asset, onFavorite, onDelete, onRetag }: { asset: VaultAsset; onFavorite: () => void; onDelete: () => void; onRetag: () => void }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const thumbUrl = asset.thumbnail
    ? `${apiUrl}/api/v1/content-vault/thumbnail/${asset.thumbnail}`
    : undefined;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden group">
      {/* Thumbnail */}
      <div className="aspect-square bg-gray-100 dark:bg-gray-700 relative">
        {thumbUrl ? (
          <img src={thumbUrl} alt={asset.filename} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {asset.media_type === "video" ? (
              <VideoCameraIcon className="h-12 w-12 text-gray-400" />
            ) : (
              <PhotoIcon className="h-12 w-12 text-gray-400" />
            )}
          </div>
        )}
        {/* Overlay actions */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button onClick={onFavorite} className="p-2 bg-white/20 rounded-full hover:bg-white/40">
            {asset.favorite ? <StarSolid className="h-5 w-5 text-yellow-400" /> : <StarIcon className="h-5 w-5 text-white" />}
          </button>
          <button onClick={onRetag} className="p-2 bg-white/20 rounded-full hover:bg-white/40">
            <TagIcon className="h-5 w-5 text-white" />
          </button>
          <button onClick={onDelete} className="p-2 bg-white/20 rounded-full hover:bg-red-500/60">
            <TrashIcon className="h-5 w-5 text-white" />
          </button>
        </div>
      </div>
      {/* Info */}
      <div className="p-3">
        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{asset.filename}</p>
        <div className="flex flex-wrap gap-1 mt-2">
          {(asset.tags || []).slice(0, 3).map((tag, i) => (
            <span key={i} className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string; color: "blue" | "green" | "purple" | "pink" }) {
  const colors = {
    blue: "from-blue-600 to-blue-400",
    green: "from-green-600 to-green-400",
    purple: "from-purple-600 to-purple-400",
    pink: "from-pink-600 to-pink-400",
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-5 text-white shadow-lg`}>
      <Icon className="h-7 w-7 mb-2 opacity-80" />
      <p className="text-xs opacity-80">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
    </div>
  );
}
