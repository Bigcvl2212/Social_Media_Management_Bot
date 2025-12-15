"use client";

import { useQuery } from "@tanstack/react-query";
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  HeartIcon,
  ChatBubbleLeftIcon,
  ShareIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";

export function GrowthAnalytics() {
  const { data: analytics } = useQuery({
    queryKey: ["growth-analytics"],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/analytics/growth`);
      if (!response.ok) throw new Error("Failed to fetch analytics");
      return response.json();
    },
  });

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={EyeIcon}
          label="Total Reach"
          value="1.2M"
          trend="+12%"
          color="blue"
        />
        <MetricCard
          icon={HeartIcon}
          label="Engagements"
          value="45.3K"
          trend="+8%"
          color="pink"
        />
        <MetricCard
          icon={ArrowTrendingUpIcon}
          label="Avg Engagement"
          value="8.5%"
          trend="+2%"
          color="green"
        />
        <MetricCard
          icon={SparklesIcon}
          label="Viral Videos"
          value="23"
          trend="+5"
          color="purple"
        />
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartPlaceholder title="Performance Over Time" />
        <ChartPlaceholder title="Platform Breakdown" />
      </div>

      {/* Recommendations */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white">
        <h3 className="text-lg font-bold mb-3">AI Growth Recommendations</h3>
        <ul className="space-y-2 text-sm">
          <li>✓ Post more short-form videos - they're getting 3x more engagement</li>
          <li>✓ Best posting time: 7-9 PM (post next content then)</li>
          <li>✓ Trending topic: Try fitness challenges content</li>
          <li>✓ Collaborate with 3 accounts in your niche for growth</li>
        </ul>
      </div>
    </div>
  );
}

interface MetricCardProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  trend: string;
  color: "blue" | "pink" | "green" | "purple";
}

function MetricCard({ icon: Icon, label, value, trend, color }: MetricCardProps) {
  const colors = {
    blue: "from-blue-600 to-blue-400",
    pink: "from-pink-600 to-pink-400",
    green: "from-green-600 to-green-400",
    purple: "from-purple-600 to-purple-400",
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} rounded-2xl p-6 text-white shadow-lg`}>
      <Icon className="h-8 w-8 mb-2 opacity-80" />
      <p className="text-sm opacity-80">{label}</p>
      <div className="flex items-end justify-between mt-2">
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs font-bold opacity-80">{trend}</p>
      </div>
    </div>
  );
}

function ChartPlaceholder({ title }: { title: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="font-bold text-gray-900 dark:text-white mb-4">{title}</h3>
      <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
        <p className="text-gray-500 dark:text-gray-400">Chart visualization here</p>
      </div>
    </div>
  );
}
