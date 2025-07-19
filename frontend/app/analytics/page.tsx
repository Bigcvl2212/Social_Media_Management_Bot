"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  EyeIcon,
  HeartIcon,
  ChatBubbleLeftIcon,
  ShareIcon,
  UsersIcon,
  DocumentTextIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { analyticsApi, AnalyticsDashboard } from "@/lib/analytics-api";

interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  color: string;
}

function MetricCard({ title, value, change, changeType, icon: Icon, color }: MetricCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`p-3 rounded-lg ${color}`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <div className="flex items-baseline">
            <p className="text-2xl font-semibold text-gray-900 dark:text-white">{value}</p>
            {change && (
              <p className={`ml-2 flex items-baseline text-sm font-semibold ${
                changeType === 'increase' 
                  ? 'text-green-600' 
                  : changeType === 'decrease' 
                  ? 'text-red-600' 
                  : 'text-gray-500'
              }`}>
                {changeType === 'increase' && <ArrowUpIcon className="h-4 w-4 mr-1" />}
                {changeType === 'decrease' && <ArrowDownIcon className="h-4 w-4 mr-1" />}
                {change}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  // Fetch analytics data
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['analytics', selectedPeriod],
    queryFn: () => analyticsApi.getAnalytics(selectedPeriod),
  });

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading analytics...</span>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto" />
          <p className="mt-2 text-red-600">Error loading analytics data</p>
        </div>
      </DashboardLayout>
    );
  }

  if (!analytics) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto" />
          <p className="mt-2 text-gray-600 dark:text-gray-400">No analytics data available</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Analytics Dashboard
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Track your social media performance and engagement metrics.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value as '7d' | '30d' | '90d' | '1y')}
              className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 3 months</option>
              <option value="1y">Last year</option>
            </select>
          </div>
        </div>

        {/* Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Posts"
            value={analytics?.data?.overview?.total_posts?.value?.toLocaleString() || '0'}
            icon={DocumentTextIcon}
            color="bg-blue-500"
          />
          <MetricCard
            title="Total Impressions"
            value={analytics?.data?.overview?.total_reach?.value?.toLocaleString() || '0'}
            icon={EyeIcon}
            color="bg-green-500"
          />
          <MetricCard
            title="Total Engagements"
            value={analytics?.data?.overview?.total_engagement?.value?.toLocaleString() || '0'}
            icon={HeartIcon}
            color="bg-purple-500"
          />
          <MetricCard
            title="Engagement Rate"
            value={`${analytics?.data?.overview?.total_engagement?.change || 0}%`}
            icon={ChartBarIcon}
            color="bg-orange-500"
          />
        </div>

        {/* Secondary Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Platform Metrics"
            value={analytics?.data?.platform_metrics?.length?.toString() || '0'}
            icon={CalendarIcon}
            color="bg-yellow-500"
          />
          <MetricCard
            title="Top Content"
            value={analytics?.data?.top_content?.length?.toString() || '0'}
            icon={DocumentTextIcon}
            color="bg-green-500"
          />
          <MetricCard
            title="Engagement Trend"
            value={analytics?.data?.engagement_trend?.length?.toString() || '0'}
            icon={UsersIcon}
            color="bg-blue-500"
          />
          <MetricCard
            title="Follower Growth"
            value={analytics?.data?.follower_growth?.length?.toString() || '0'}
            icon={ExclamationTriangleIcon}
            color="bg-red-500"
          />
        </div>

        {/* Platform Performance */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
            Platform Performance
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {analytics?.data?.platform_metrics?.map((platform) => (
              <div
                key={platform.platform}
                className="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                    {platform.platform}
                  </h4>
                  <span className={`text-sm font-medium ${
                    platform.engagement >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {platform.engagement.toLocaleString()}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Posts:</span>
                    <span className="text-gray-900 dark:text-white">{platform.posts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Reach:</span>
                    <span className="text-gray-900 dark:text-white">{platform.reach.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Followers:</span>
                    <span className="text-gray-900 dark:text-white">{platform.followers.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Engagement Rate:</span>
                    <span className="text-gray-900 dark:text-white">{platform.engagement}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Followers:</span>
                    <span className="text-gray-900 dark:text-white">{platform.followers.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Performing Content */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
            Top Performing Content
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Content
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Platform
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Impressions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Engagement
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Rate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-600">
                {analytics?.data?.top_content?.map((content) => (
                  <tr key={content.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {content.title}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(content.published_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900 dark:text-white capitalize">
                        {content.platform}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {content.views.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-4 text-sm text-gray-900 dark:text-white">
                        <div className="flex items-center">
                          <HeartIcon className="h-4 w-4 mr-1 text-red-500" />
                          {content.likes}
                        </div>
                        <div className="flex items-center">
                          <ChatBubbleLeftIcon className="h-4 w-4 mr-1 text-blue-500" />
                          {content.comments}
                        </div>
                        <div className="flex items-center">
                          <ShareIcon className="h-4 w-4 mr-1 text-green-500" />
                          {content.shares}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {content.engagement_rate}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Engagement Trend Chart Placeholder */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
            Engagement Trend
          </h3>
          <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-center">
              <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto" />
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                Chart visualization would go here
              </p>
              <p className="text-sm text-gray-400">
                {analytics?.data?.engagement_trend?.length || 0} data points available
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}