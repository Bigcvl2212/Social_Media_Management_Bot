"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  PhotoIcon,
  SparklesIcon,
  AdjustmentsHorizontalIcon,
  SwatchIcon,
  PlusIcon,
  ChevronDownIcon,
  PencilIcon,
} from "@heroicons/react/24/outline";

interface EditingOptions {
  filter: string;
  brightness: number;
  contrast: number;
  saturation: number;
  blur: number;
}

export function ImageEditor() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [options, setOptions] = useState<EditingOptions>({
    filter: "original",
    brightness: 100,
    contrast: 100,
    saturation: 100,
    blur: 0,
  });
  const [addingText, setAddingText] = useState(false);
  const [textContent, setTextContent] = useState("");

  const applyEditsMutation = useMutation({
    mutationFn: async (imageData: EditingOptions) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/content/image/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          imageId: selectedImage,
          edits: imageData,
        }),
      });
      if (!response.ok) throw new Error("Failed to apply edits");
      return response.json();
    },
  });

  const addTextMutation = useMutation({
    mutationFn: async (text: string) => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/content/image/add-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          imageId: selectedImage,
          text,
          position: "center",
          fontSize: 48,
          color: "#ffffff",
        }),
      });
      return response.json();
    },
  });

  if (!selectedImage) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <PhotoIcon className="h-16 w-16 mx-auto text-purple-600 dark:text-purple-400 mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
            Image Editor
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Upload an image to get started with AI-powered editing
          </p>

          <label className="inline-block mt-6 cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = (e) => {
                    setSelectedImage(e.target?.result as string);
                  };
                  reader.readAsDataURL(file);
                }
              }}
              className="hidden"
            />
            <div className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-bold hover:shadow-lg transition-all">
              <PlusIcon className="h-5 w-5 inline mr-2" />
              Select Image
            </div>
          </label>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Image Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-lg border border-gray-200 dark:border-gray-700">
        <div className="bg-gray-900 flex items-center justify-center p-8 aspect-video">
          <div
            style={{
              filter: `brightness(${options.brightness}%) contrast(${options.contrast}%) saturate(${options.saturation}%) blur(${options.blur}px)`,
            }}
          >
            <img
              src={selectedImage}
              alt="Edited"
              className="max-h-96 max-w-full"
            />
          </div>
        </div>
      </div>

      {/* Editing Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Filters & Adjustments */}
        <div className="lg:col-span-2 space-y-6">
          {/* Trending Filters */}
          <FilterPanel currentFilter={options.filter} onChange={(f) => setOptions({ ...options, filter: f })} />

          {/* Adjustments */}
          <AdjustmentsPanel options={options} setOptions={setOptions} />

          {/* Text & Overlays */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <PencilIcon className="h-5 w-5 text-blue-600" />
              Add Text & Overlays
            </h3>

            {!addingText ? (
              <button
                onClick={() => setAddingText(true)}
                className="w-full bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-lg p-4 text-center text-blue-600 dark:text-blue-400 font-medium hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              >
                <PlusIcon className="h-5 w-5 inline mr-2" />
                Add Text
              </button>
            ) : (
              <div className="space-y-3">
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Enter text to add..."
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  rows={3}
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      addTextMutation.mutate(textContent);
                      setAddingText(false);
                      setTextContent("");
                    }}
                    className="flex-1 bg-blue-600 text-white font-bold py-2 rounded-lg hover:bg-blue-700"
                  >
                    Add Text
                  </button>
                  <button
                    onClick={() => {
                      setAddingText(false);
                      setTextContent("");
                    }}
                    className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-bold py-2 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Quick Actions & Presets */}
        <div className="space-y-4">
          {/* Format Presets */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Format for Platform
            </h3>

            <div className="space-y-2">
              {[
                { name: "Instagram Post", aspect: "1:1" },
                { name: "Instagram Story", aspect: "9:16" },
                { name: "TikTok", aspect: "9:16" },
                { name: "Facebook", aspect: "4:5" },
              ].map((format) => (
                <button
                  key={format.name}
                  className="w-full text-left px-4 py-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <p className="font-medium text-gray-900 dark:text-white">
                    {format.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {format.aspect}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Meme Templates */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
              Meme Templates
            </h3>

            <div className="grid grid-cols-2 gap-2">
              {["Drake", "Distracted Boyfriend", "Woman Yelling", "Coffin Dance"].map(
                (template) => (
                  <button
                    key={template}
                    className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center justify-center text-xs text-center font-medium text-gray-700 dark:text-gray-300 p-2 transition-colors"
                  >
                    {template}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <button className="w-full bg-green-600 text-white font-bold py-2 rounded-lg hover:bg-green-700 transition-colors">
              Save & Export
            </button>
            <button className="w-full bg-blue-600 text-white font-bold py-2 rounded-lg hover:bg-blue-700 transition-colors">
              Schedule Post
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Filter Panel Component
 */
interface FilterPanelProps {
  currentFilter: string;
  onChange: (filter: string) => void;
}

function FilterPanel({ currentFilter, onChange }: FilterPanelProps) {
  const trendingFilters = [
    "Original",
    "Vintage",
    "Neon",
    "Cinematic",
    "Warm",
    "Cool",
    "High Contrast",
    "Black & White",
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <SwatchIcon className="h-5 w-5 text-pink-600" />
        Trending Filters
      </h3>

      <div className="grid grid-cols-4 gap-2">
        {trendingFilters.map((filter) => (
          <button
            key={filter}
            onClick={() => onChange(filter.toLowerCase())}
            className={`aspect-square rounded-lg font-medium text-xs transition-all ${
              currentFilter === filter.toLowerCase()
                ? "bg-pink-600 text-white shadow-lg scale-105"
                : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
            }`}
          >
            {filter}
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * Adjustments Panel Component
 */
interface AdjustmentsPanelProps {
  options: EditingOptions;
  setOptions: (options: EditingOptions) => void;
}

function AdjustmentsPanel({ options, setOptions }: AdjustmentsPanelProps) {
  const adjustments = [
    { label: "Brightness", key: "brightness" as keyof EditingOptions, min: 0, max: 200 },
    { label: "Contrast", key: "contrast" as keyof EditingOptions, min: 0, max: 200 },
    { label: "Saturation", key: "saturation" as keyof EditingOptions, min: 0, max: 200 },
    { label: "Blur", key: "blur" as keyof EditingOptions, min: 0, max: 50 },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <AdjustmentsHorizontalIcon className="h-5 w-5 text-purple-600" />
        Adjustments
      </h3>

      <div className="space-y-4">
        {adjustments.map((adj) => (
          <div key={adj.key}>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {adj.label}
              </label>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {options[adj.key]}
              </span>
            </div>
            <input
              type="range"
              min={adj.min}
              max={adj.max}
              value={options[adj.key]}
              onChange={(e) =>
                setOptions({
                  ...options,
                  [adj.key]: parseInt(e.target.value),
                })
              }
              className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
