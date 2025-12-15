"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  PlayIcon,
  PauseIcon,
  ScissorsIcon,
  SpeakerWaveIcon,
  SparklesIcon,
  CheckIcon,
} from "@heroicons/react/24/outline";

interface VideoClip {
  id: string;
  startTime: number;
  endTime: number;
  title: string;
  viralScore: number;
  aspectRatio: "9:16" | "16:9" | "1:1";
  duration: number;
}

interface VideoClippingEditorProps {
  videoId?: string;
}

export function VideoClippingEditor({ videoId }: VideoClippingEditorProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedClips, setSelectedClips] = useState<string[]>([]);
  const [editingClip, setEditingClip] = useState<VideoClip | null>(null);

  // Fetch detected clips
  const { data: clips, isLoading: clipsLoading } = useQuery({
    queryKey: ["video-clips", videoId],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/content/video/${videoId}/clips`);
      if (!response.ok) throw new Error("Failed to fetch clips");
      return response.json() as Promise<VideoClip[]>;
    },
    enabled: !!videoId,
  });

  // Add branding/subtitles mutation
  const addBrandingMutation = useMutation({
    mutationFn: async (clipId: string) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiUrl}/api/v1/content/clips/${clipId}/add-branding`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            brandLogo: "logo.png",
            watermark: true,
            subtitles: true,
            captions: "auto",
          }),
        }
      );
      return response.json();
    },
  });

  // Add music mutation
  const addMusicMutation = useMutation({
    mutationFn: async (clipId: string) => {
      const response = await fetch(
        `/api/v1/content/clips/${clipId}/add-music`,
        {
          method: "POST",
        }
      );
      return response.json();
    },
  });

  return (
    <div className="space-y-6">
      {/* Video Preview */}
      <div className="bg-black rounded-2xl overflow-hidden shadow-2xl">
        <div className="aspect-video bg-gray-900 flex items-center justify-center relative group">
          {/* Placeholder video player */}
          <div className="text-center text-white">
            <PlayIcon className="h-16 w-16 mx-auto opacity-50 group-hover:opacity-100 transition-opacity cursor-pointer" />
            <p className="text-sm mt-2 opacity-50">Video Preview</p>
          </div>

          {/* Timeline/Progress Bar */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-4">
            <div className="bg-gray-700 rounded-full h-1 cursor-pointer">
              <div
                className="bg-red-600 h-1 rounded-full"
                style={{ width: `${(currentTime / 100) * 100}%` }}
              />
            </div>
            <div className="flex justify-between items-center mt-2 text-white text-xs">
              <span>{Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(0)}</span>
              <span>100:00</span>
            </div>
          </div>
        </div>

        {/* Playback Controls */}
        <div className="bg-gray-900 p-4 flex items-center justify-center gap-4">
          <button className="text-white hover:text-blue-400 transition-colors">
            {isPlaying ? (
              <PauseIcon className="h-6 w-6" />
            ) : (
              <PlayIcon className="h-6 w-6" />
            )}
          </button>
          <div className="flex-1 bg-gray-700 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full w-1/3" />
          </div>
          <span className="text-white text-xs">1:25 / 100:00</span>
        </div>
      </div>

      {/* Detected Clips Section */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <ScissorsIcon className="h-6 w-6 text-blue-600" />
            AI-Detected Clips
          </h3>
          <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-3 py-1 rounded-full text-sm font-medium">
            {clips?.length || 0} clips found
          </span>
        </div>

        {clipsLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Analyzing video...</p>
          </div>
        ) : clips && clips.length > 0 ? (
          <div className="space-y-4">
            {clips.map((clip) => (
              <ClipCard
                key={clip.id}
                clip={clip}
                isSelected={selectedClips.includes(clip.id)}
                onSelect={() => {
                  setSelectedClips((prev) =>
                    prev.includes(clip.id)
                      ? prev.filter((id) => id !== clip.id)
                      : [...prev, clip.id]
                  );
                }}
                onEdit={() => setEditingClip(clip)}
                onAddBranding={() => addBrandingMutation.mutate(clip.id)}
                onAddMusic={() => addMusicMutation.mutate(clip.id)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-600 dark:text-gray-400">
              No clips detected. Try adjusting the sensitivity settings.
            </p>
          </div>
        )}
      </div>

      {/* Editing Panel */}
      {editingClip && (
        <ClipEditingPanel clip={editingClip} onClose={() => setEditingClip(null)} />
      )}

      {/* Batch Actions */}
      {selectedClips.length > 0 && (
        <BatchActionsPanel selectedCount={selectedClips.length} />
      )}
    </div>
  );
}

/**
 * Clip Card Component
 */
interface ClipCardProps {
  clip: VideoClip;
  isSelected: boolean;
  onSelect: () => void;
  onEdit: () => void;
  onAddBranding: () => void;
  onAddMusic: () => void;
}

function ClipCard({
  clip,
  isSelected,
  onSelect,
  onEdit,
  onAddBranding,
  onAddMusic,
}: ClipCardProps) {
  const getViralColor = (score: number) => {
    if (score >= 8) return "from-green-600 to-green-400";
    if (score >= 6) return "from-blue-600 to-blue-400";
    if (score >= 4) return "from-yellow-600 to-yellow-400";
    return "from-orange-600 to-orange-400";
  };

  return (
    <div
      className={`border-2 rounded-lg p-4 transition-all ${
        isSelected
          ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20"
          : "border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        {/* Thumbnail & Selection */}
        <div className="flex items-center gap-3">
          <button
            onClick={onSelect}
            className={`flex-shrink-0 w-8 h-8 rounded border-2 flex items-center justify-center transition-all ${
              isSelected
                ? "bg-blue-600 border-blue-600"
                : "border-gray-300 dark:border-gray-600 hover:border-blue-400"
            }`}
          >
            {isSelected && <CheckIcon className="h-5 w-5 text-white" />}
          </button>

          <div className="bg-gray-900 rounded w-20 h-20 flex items-center justify-center text-white text-xs">
            {clip.aspectRatio === "9:16" ? "📱" : "📺"}
          </div>
        </div>

        {/* Clip Info */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-bold text-gray-900 dark:text-white">{clip.title}</h4>
            <div
              className={`bg-gradient-to-r ${getViralColor(
                clip.viralScore
              )} text-white px-3 py-1 rounded-full text-sm font-bold`}
            >
              {clip.viralScore}/10 Viral
            </div>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {clip.startTime.toFixed(1)}s - {clip.endTime.toFixed(1)}s ({clip.duration}s)
          </p>

          {/* Aspect Ratio Badges */}
          <div className="flex gap-2 mb-3">
            <span className="bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs px-2 py-1 rounded">
              {clip.aspectRatio}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 flex-wrap">
            <ActionButton
              icon={ScissorsIcon}
              label="Edit"
              onClick={onEdit}
              color="blue"
            />
            <ActionButton
              icon={SparklesIcon}
              label="Add Branding"
              onClick={onAddBranding}
              color="purple"
            />
            <ActionButton
              icon={SpeakerWaveIcon}
              label="Add Music"
              onClick={onAddMusic}
              color="green"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Action Button Component
 */
interface ActionButtonProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick: () => void;
  color: "blue" | "purple" | "green";
}

function ActionButton({
  icon: Icon,
  label,
  onClick,
  color,
}: ActionButtonProps) {
  const colors = {
    blue: "bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50",
    purple:
      "bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/50",
    green:
      "bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/50",
  };

  return (
    <button
      onClick={onClick}
      className={`px-3 py-1 rounded text-xs font-medium flex items-center gap-1 transition-colors ${colors[color]}`}
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </button>
  );
}

/**
 * Clip Editing Panel
 */
interface ClipEditingPanelProps {
  clip: VideoClip;
  onClose: () => void;
}

function ClipEditingPanel({ clip, onClose }: ClipEditingPanelProps) {
  const [title, setTitle] = useState(clip.title);
  const [aspectRatio, setAspectRatio] = useState<"9:16" | "16:9" | "1:1">(
    clip.aspectRatio
  );

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
          Edit Clip: {clip.title}
        </h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          ✕
        </button>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Clip Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>

        {/* Aspect Ratio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Aspect Ratio
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(["9:16", "16:9", "1:1"] as const).map((ratio) => (
              <button
                key={ratio}
                onClick={() => setAspectRatio(ratio)}
                className={`p-3 rounded-lg border-2 font-medium text-sm transition-colors ${
                  aspectRatio === ratio
                    ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20 text-blue-600"
                    : "border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-blue-300"
                }`}
              >
                {ratio}
              </button>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <button className="w-full bg-blue-600 text-white font-bold py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Save Changes
        </button>
      </div>
    </div>
  );
}

/**
 * Batch Actions Panel
 */
interface BatchActionsPanelProps {
  selectedCount: number;
}

function BatchActionsPanel({ selectedCount }: BatchActionsPanelProps) {
  return (
    <div className="fixed bottom-6 right-6 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 border border-gray-200 dark:border-gray-700 max-w-sm">
      <h3 className="font-bold text-gray-900 dark:text-white mb-4">
        {selectedCount} Clip{selectedCount !== 1 ? "s" : ""} Selected
      </h3>

      <div className="space-y-2">
        <button className="w-full bg-blue-600 text-white font-bold py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
          <SparklesIcon className="h-5 w-5" />
          Add Branding to All
        </button>
        <button className="w-full bg-purple-600 text-white font-bold py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2">
          <SpeakerWaveIcon className="h-5 w-5" />
          Add Music to All
        </button>
        <button className="w-full bg-green-600 text-white font-bold py-2 rounded-lg hover:bg-green-700 transition-colors">
          Schedule Selected
        </button>
      </div>
    </div>
  );
}
