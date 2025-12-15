"use client";

import { useState } from "react";
import {
  DocumentArrowUpIcon,
  SparklesIcon,
  PhotoIcon,
  VideoCameraIcon,
  FilmIcon,
  PlusIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { useMutation } from "@tanstack/react-query";

type CreationMode = "upload-video" | "upload-image" | "ai-generate" | null;

interface UploadProgress {
  fileName: string;
  progress: number;
  status: "uploading" | "processing" | "complete" | "error";
  message: string;
}

export function ContentCreationHub() {
  const [selectedMode, setSelectedMode] = useState<CreationMode>(null);
  const [uploads, setUploads] = useState<UploadProgress[]>([]);

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/content/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Upload failed");
      }
      return response.json();
    },
    onSuccess: (data) => {
      // Handle success - show success message
      console.log("Upload successful:", data);
      // You might want to refresh the content library here
    },
    onError: (error) => {
      console.error("Upload error:", error);
    },
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>, type: "video" | "image") => {
    const files = event.currentTarget.files;
    if (!files) return;

    Array.from(files).forEach((file) => {
      const fileProgress: UploadProgress = {
        fileName: file.name,
        progress: 0,
        status: "uploading",
        message: "Uploading...",
      };

      setUploads((prev) => [...prev, fileProgress]);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("content_type", type);

      uploadMutation.mutate(formData);
    });
  };

  return (
    <div className="space-y-6">
      {/* Creation Mode Selection */}
      {!selectedMode && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <CreationModeCard
            icon={DocumentArrowUpIcon}
            title="Upload Video"
            description="Import and process long-form videos into viral clips"
            color="from-blue-600 to-blue-400"
            onClick={() => setSelectedMode("upload-video")}
          />
          <CreationModeCard
            icon={PhotoIcon}
            title="Upload Image"
            description="Transform images with AI editing and trending effects"
            color="from-purple-600 to-purple-400"
            onClick={() => setSelectedMode("upload-image")}
          />
          <CreationModeCard
            icon={SparklesIcon}
            title="Generate from Text"
            description="Create videos or images from prompts and scripts"
            color="from-pink-600 to-pink-400"
            onClick={() => setSelectedMode("ai-generate")}
          />
          <CreationModeCard
            icon={FilmIcon}
            title="Generate from Audio"
            description="Convert podcasts, voiceovers, or music to videos"
            color="from-green-600 to-green-400"
            onClick={() => setSelectedMode("ai-generate")}
          />
        </div>
      )}

      {/* Video Upload */}
      {selectedMode === "upload-video" && (
        <VideoUploadPanel onFileSelect={handleFileUpload} />
      )}

      {/* Image Upload */}
      {selectedMode === "upload-image" && (
        <ImageUploadPanel onFileSelect={handleFileUpload} />
      )}

      {/* AI Generation */}
      {selectedMode === "ai-generate" && (
        <AIGenerationPanel onClose={() => setSelectedMode(null)} />
      )}

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <UploadProgressPanel uploads={uploads} />
      )}
    </div>
  );
}

/**
 * Creation Mode Card Component
 */
interface CreationModeCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  color: string;
  onClick: () => void;
}

function CreationModeCard({
  icon: Icon,
  title,
  description,
  color,
  onClick,
}: CreationModeCardProps) {
  return (
    <button
      onClick={onClick}
      className={`group relative bg-gradient-to-br ${color} p-6 rounded-2xl text-white shadow-lg hover:shadow-2xl transition-all hover:scale-105 cursor-pointer overflow-hidden`}
    >
      <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity" />
      <div className="relative z-10">
        <Icon className="h-12 w-12 mb-3 group-hover:scale-110 transition-transform" />
        <h3 className="font-bold text-lg text-left">{title}</h3>
        <p className="text-sm text-white/80 text-left mt-2">{description}</p>
      </div>
    </button>
  );
}

/**
 * Video Upload Panel
 */
interface UploadPanelProps {
  onFileSelect: (event: React.ChangeEvent<HTMLInputElement>, type: "video" | "image") => void;
}

function VideoUploadPanel({ onFileSelect }: UploadPanelProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border-2 border-dashed border-blue-300 dark:border-blue-700">
      <div className="text-center mb-6">
        <VideoCameraIcon className="h-16 w-16 mx-auto text-blue-600 dark:text-blue-400 mb-4" />
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Your Video</h3>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Drag and drop your video file, or click to select
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <FileInputArea
          accept="video/*"
          label="Main Video"
          onChange={(e) => onFileSelect(e, "video")}
        />
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">Processing will:</h4>
          <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
            <li>✓ Auto-detect high-energy scenes</li>
            <li>✓ Extract viral clips (9:16, 16:9)</li>
            <li>✓ Add subtitles & captions</li>
            <li>✓ Score for virality</li>
            <li>✓ Suggest music & effects</li>
          </ul>
        </div>
      </div>

      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
        <p className="text-sm text-purple-900 dark:text-purple-200">
          <strong>Pro Tip:</strong> Upload videos 2-30 minutes long for best results. We'll automatically
          detect transitions, cuts, and high-engagement moments.
        </p>
      </div>
    </div>
  );
}

/**
 * Image Upload Panel
 */
function ImageUploadPanel({ onFileSelect }: UploadPanelProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border-2 border-dashed border-purple-300 dark:border-purple-700">
      <div className="text-center mb-6">
        <PhotoIcon className="h-16 w-16 mx-auto text-purple-600 dark:text-purple-400 mb-4" />
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Your Image</h3>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Upload and transform images with AI editing
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FileInputArea
          accept="image/*"
          label="Image to Edit"
          onChange={(e) => onFileSelect(e, "image")}
        />
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
          <h4 className="font-semibold text-purple-900 dark:text-purple-200 mb-2">AI will apply:</h4>
          <ul className="text-sm text-purple-800 dark:text-purple-300 space-y-1">
            <li>✓ Trending filters & effects</li>
            <li>✓ Brand overlay & branding</li>
            <li>✓ Dynamic text & captions</li>
            <li>✓ Optimized for each platform</li>
            <li>✓ Meme templates on demand</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

/**
 * AI Generation Panel
 */
interface AIGenerationPanelProps {
  onClose: () => void;
}

function AIGenerationPanel({ onClose }: AIGenerationPanelProps) {
  const [generationType, setGenerationType] = useState<"text-to-video" | "audio-to-video" | "text-to-image" | null>(null);

  if (!generationType) {
    return (
      <div className="space-y-4">
        <button
          onClick={onClose}
          className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 mb-4"
        >
          ← Back
        </button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <AIGenerationCard
            title="Text/Script → Video"
            description="Generate videos from text prompts or scripts"
            icon={DocumentArrowUpIcon}
            onClick={() => setGenerationType("text-to-video")}
          />
          <AIGenerationCard
            title="Audio/Podcast → Video"
            description="Create videos from audio files or voice content"
            icon={FilmIcon}
            onClick={() => setGenerationType("audio-to-video")}
          />
          <AIGenerationCard
            title="Prompt → Image"
            description="Generate images with AI from text descriptions"
            icon={PhotoIcon}
            onClick={() => setGenerationType("text-to-image")}
          />
        </div>
      </div>
    );
  }

  return (
    <GenerationWorkflow
      type={generationType}
      onBack={() => setGenerationType(null)}
    />
  );
}

/**
 * AI Generation Card
 */
interface AIGenerationCardProps {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  onClick: () => void;
}

function AIGenerationCard({
  title,
  description,
  icon: Icon,
  onClick,
}: AIGenerationCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-gradient-to-br from-pink-600 to-orange-600 p-6 rounded-2xl text-white text-left shadow-lg hover:shadow-xl transition-all hover:scale-105"
    >
      <Icon className="h-10 w-10 mb-3" />
      <h3 className="font-bold text-lg">{title}</h3>
      <p className="text-sm text-white/80 mt-2">{description}</p>
    </button>
  );
}

/**
 * File Input Area
 */
interface FileInputAreaProps {
  accept: string;
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

function FileInputArea({ accept, label, onChange }: FileInputAreaProps) {
  return (
    <label className="block cursor-pointer group">
      <input
        type="file"
        accept={accept}
        onChange={onChange}
        className="hidden"
        multiple
      />
      <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-blue-400 dark:hover:border-blue-500 transition-colors bg-gray-50 dark:bg-gray-700/50 group-hover:bg-blue-50 dark:group-hover:bg-blue-900/10">
        <PlusIcon className="h-8 w-8 mx-auto text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 mb-2 transition-colors" />
        <p className="font-semibold text-gray-700 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">
          Click or drag {label}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">or drop files here</p>
      </div>
    </label>
  );
}

/**
 * Upload Progress Panel
 */
interface UploadProgressPanelProps {
  uploads: UploadProgress[];
}

function UploadProgressPanel({ uploads }: UploadProgressPanelProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-4">Processing Files</h3>
      <div className="space-y-3">
        {uploads.map((upload, index) => (
          <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div className="flex-1">
              <p className="font-medium text-gray-900 dark:text-white">{upload.fileName}</p>
              <div className="mt-2 w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${upload.progress}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{upload.message}</p>
            </div>
            <div className="ml-4">
              {upload.status === "complete" && (
                <CheckCircleIcon className="h-6 w-6 text-green-600" />
              )}
              {upload.status === "error" && (
                <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Generation Workflow Component
 */
interface GenerationWorkflowProps {
  type: "text-to-video" | "audio-to-video" | "text-to-image";
  onBack: () => void;
}

function GenerationWorkflow({ type, onBack }: GenerationWorkflowProps) {
  const [formData, setFormData] = useState({
    prompt: "",
    duration: "15",
    style: "professional",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle generation
  };

  const typeLabels = {
    "text-to-video": "Generate Video from Text",
    "audio-to-video": "Generate Video from Audio",
    "text-to-image": "Generate Image",
  };

  return (
    <div className="space-y-4">
      <button
        onClick={onBack}
        className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 mb-4"
      >
        ← Back
      </button>

      <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          {typeLabels[type]}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Prompt/Script Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {type === "text-to-video" ? "Script or Prompt" : type === "audio-to-video" ? "Audio File" : "Image Description"}
            </label>
            {type === "text-to-image" || type === "text-to-video" ? (
              <textarea
                value={formData.prompt}
                onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                placeholder="Describe what you want to create..."
                rows={6}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            ) : (
              <FileInputArea
                accept="audio/*"
                label="Audio File"
                onChange={() => {}}
              />
            )}
          </div>

          {/* Duration Selector (for video generation) */}
          {type !== "text-to-image" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Video Duration
              </label>
              <div className="flex gap-2">
                {["15", "30", "60", "120"].map((duration) => (
                  <button
                    key={duration}
                    type="button"
                    onClick={() => setFormData({ ...formData, duration })}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      formData.duration === duration
                        ? "bg-blue-600 text-white"
                        : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
                    }`}
                  >
                    {duration}s
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Style/Format Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Style
            </label>
            <select
              value={formData.style}
              onChange={(e) => setFormData({ ...formData, style: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="viral">Viral/Trendy</option>
              <option value="educational">Educational</option>
              <option value="humorous">Humorous</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-pink-600 to-orange-600 text-white font-bold py-3 rounded-lg hover:shadow-lg transition-all"
          >
            <SparklesIcon className="h-5 w-5 inline mr-2" />
            Generate Content
          </button>
        </form>
      </div>
    </div>
  );
}
