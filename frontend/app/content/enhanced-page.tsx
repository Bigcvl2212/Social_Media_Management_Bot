"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  SparklesIcon,
  VideoCameraIcon,
  PhotoIcon,
  CalendarIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  RocketLaunchIcon,
} from "@heroicons/react/24/outline";

// Import content management components
import { ContentCreationHub } from "@/components/content/creation-hub";
import { ContentLibrary } from "@/components/content/content-library";
import { ContentScheduler } from "@/components/content/content-scheduler";
import { GrowthAnalytics } from "@/components/content/growth-analytics";
import { PlatformManager } from "@/components/content/platform-manager";

type ContentTab = 
  | "create" 
  | "library" 
  | "scheduler" 
  | "analytics" 
  | "platforms" 
  | "settings";

interface QuickStats {
  total_videos_processed: number;
  videos_scheduled: number;
  total_reach: number;
  avg_engagement_rate: number;
  viral_scores: number[];
}

export default function EnhancedContentPage() {
  const [activeTab, setActiveTab] = useState<ContentTab>("create");
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Fetch quick stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["content-stats"],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/content/stats`);
      if (!response.ok) throw new Error("Failed to fetch stats");
      return response.json() as Promise<QuickStats>;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const tabs = [
    {
      id: "create" as ContentTab,
      label: "Create Content",
      icon: SparklesIcon,
      description: "Upload, generate, and edit content",
    },
    {
      id: "library" as ContentTab,
      label: "Content Library",
      icon: PhotoIcon,
      description: "Manage all your content",
    },
    {
      id: "scheduler" as ContentTab,
      label: "Schedule & Post",
      icon: CalendarIcon,
      description: "Plan and automate posting",
    },
    {
      id: "analytics" as ContentTab,
      label: "Analytics",
      icon: ChartBarIcon,
      description: "Track performance and growth",
    },
    {
      id: "platforms" as ContentTab,
      label: "Platforms",
      icon: Cog6ToothIcon,
      description: "Manage social accounts",
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header with Quick Access */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Main Title */}
          <div className="lg:col-span-3">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white shadow-lg">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-4xl font-bold mb-2">Content Studio</h1>
                  <p className="text-blue-100">
                    Create, edit, and grow viral content across all platforms
                  </p>
                </div>
                <RocketLaunchIcon className="h-12 w-12 opacity-80" />
              </div>
            </div>
          </div>

          {/* Quick Stats Card */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-md border border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-300 mb-4">
              Quick Stats
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {statsLoading ? "—" : stats?.total_videos_processed || 0}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Videos Created</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {statsLoading ? "—" : stats?.videos_scheduled || 0}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Scheduled</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Action Buttons */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <QuickActionButton
            icon={VideoCameraIcon}
            label="Upload Video"
            onClick={() => setActiveTab("create")}
            color="blue"
          />
          <QuickActionButton
            icon={PhotoIcon}
            label="Upload Image"
            onClick={() => setActiveTab("create")}
            color="purple"
          />
          <QuickActionButton
            icon={SparklesIcon}
            label="Generate Content"
            onClick={() => setActiveTab("create")}
            color="pink"
          />
          <QuickActionButton
            icon={CalendarIcon}
            label="Schedule"
            onClick={() => setActiveTab("scheduler")}
            color="green"
          />
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 overflow-x-auto" aria-label="Content tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors flex items-center gap-2 ${
                    isActive
                      ? "border-blue-600 text-blue-600 dark:text-blue-400"
                      : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="animate-fade-in">
          {activeTab === "create" && <ContentCreationHub />}
          {activeTab === "library" && <ContentLibrary />}
          {activeTab === "scheduler" && <ContentScheduler />}
          {activeTab === "analytics" && <GrowthAnalytics />}
          {activeTab === "platforms" && <PlatformManager />}
        </div>
      </div>
    </DashboardLayout>
  );
}

/**
 * Quick action button component
 */
interface QuickActionButtonProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick: () => void;
  color: "blue" | "purple" | "pink" | "green";
}

function QuickActionButton({
  icon: Icon,
  label,
  onClick,
  color,
}: QuickActionButtonProps) {
  const colorClasses = {
    blue: "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30",
    purple:
      "bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30",
    pink: "bg-pink-50 dark:bg-pink-900/20 text-pink-600 dark:text-pink-400 hover:bg-pink-100 dark:hover:bg-pink-900/30",
    green:
      "bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/30",
  };

  return (
    <button
      onClick={onClick}
      className={`p-4 rounded-xl border-2 border-transparent transition-all ${colorClasses[color]} hover:shadow-md`}
    >
      <Icon className="h-6 w-6 mb-2 mx-auto" />
      <p className="text-xs font-semibold text-center">{label}</p>
    </button>
  );
}
