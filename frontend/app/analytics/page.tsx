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
  ExclamationTriangleIcon,
  UserGroupIcon,
  TrophyIcon,
  LightBulbIcon,
  ClipboardDocumentListIcon,
} from "@heroicons/react/24/outline";
import { analyticsApi } from "@/lib/analytics-api";
import { competitorAnalysisApi } from "@/lib/competitor-analysis-api";
import { audienceInsightsApi } from "@/lib/audience-insights-api";
import { growthRecommendationsApi } from "@/lib/growth-recommendations-api";

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

// Tab navigation component
function TabNavigation({ activeTab, setActiveTab }: { 
  activeTab: string; 
  setActiveTab: (tab: string) => void; 
}) {
  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'competitors', name: 'Competitors', icon: TrophyIcon },
    { id: 'audience', name: 'Audience', icon: UserGroupIcon },
    { id: 'recommendations', name: 'Growth Tips', icon: LightBulbIcon },
  ];

  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <nav className="-mb-px flex space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <tab.icon className="h-5 w-5 mr-2" />
            {tab.name}
          </button>
        ))}
      </nav>
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ selectedPeriod }: { selectedPeriod: string }) {
  const { data: analytics, isLoading, error } = useQuery({
    queryKey: ['analytics', selectedPeriod],
    queryFn: () => analyticsApi.getAnalytics(selectedPeriod as '7d' | '30d' | '90d' | '1y'),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading analytics...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto" />
        <p className="mt-2 text-red-600">Error loading analytics data</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto" />
        <p className="mt-2 text-gray-600 dark:text-gray-400">No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
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
    </div>
  );
}

// Competitors Tab Component
function CompetitorsTab() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['competitor-dashboard'],
    queryFn: () => competitorAnalysisApi.getCompetitorDashboard(),
  });

  const { data: trends } = useQuery({
    queryKey: ['competitor-trends'],
    queryFn: () => competitorAnalysisApi.getCompetitorTrends(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading competitor data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Competitor Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Competitors"
          value={dashboard?.summary.total_competitors?.toString() || '0'}
          icon={TrophyIcon}
          color="bg-purple-500"
        />
        <MetricCard
          title="Active Tracking"
          value={dashboard?.summary.active_competitors?.toString() || '0'}
          icon={EyeIcon}
          color="bg-green-500"
        />
        <MetricCard
          title="Platforms"
          value={dashboard?.summary.platforms_tracked?.toString() || '0'}
          icon={ClipboardDocumentListIcon}
          color="bg-blue-500"
        />
        <MetricCard
          title="Growth Leaders"
          value={trends?.growth_leaders?.length?.toString() || '0'}
          icon={ArrowUpIcon}
          color="bg-orange-500"
        />
      </div>

      {/* Top Performer */}
      {dashboard?.top_performer && (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Top Performing Competitor
          </h3>
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <p className="text-xl font-semibold text-gray-900 dark:text-white">
                @{dashboard.top_performer.username}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 capitalize">
                {dashboard.top_performer.platform}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-green-600">
                {dashboard.top_performer.avg_engagement_rate}%
              </p>
              <p className="text-sm text-gray-500">Engagement Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* Trending Hashtags */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Trending Hashtags from Competitors
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dashboard?.trending_hashtags?.map((hashtag, index) => (
            <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-blue-600 dark:text-blue-400">
                  {hashtag.hashtag}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {hashtag.usage_count} uses
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                Avg engagement: {hashtag.avg_engagement.toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Growth Opportunities */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Growth Opportunities
        </h3>
        <div className="space-y-4">
          {dashboard?.growth_opportunities?.map((opportunity, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-medium text-gray-900 dark:text-white">
                {opportunity.title}
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                {opportunity.description}
              </p>
              <p className="text-sm text-blue-600 dark:text-blue-400 mt-2">
                Action: {opportunity.action}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Audience Tab Component
function AudienceTab() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['audience-dashboard'],
    queryFn: () => audienceInsightsApi.getAudienceDashboard(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading audience data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Audience Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Audience"
          value={dashboard?.summary.total_audience_size?.toLocaleString() || '0'}
          icon={UsersIcon}
          color="bg-blue-500"
        />
        <MetricCard
          title="Segments"
          value={dashboard?.summary.total_segments?.toString() || '0'}
          icon={UserGroupIcon}
          color="bg-green-500"
        />
        <MetricCard
          title="Avg Engagement"
          value={`${dashboard?.summary.avg_engagement_rate || 0}%`}
          icon={HeartIcon}
          color="bg-purple-500"
        />
        <MetricCard
          title="Top Interests"
          value={dashboard?.demographics.top_interests?.length?.toString() || '0'}
          icon={LightBulbIcon}
          color="bg-orange-500"
        />
      </div>

      {/* Top Segments */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Top Audience Segments
        </h3>
        <div className="space-y-4">
          {dashboard?.top_segments?.map((segment) => (
            <div key={segment.id} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {segment.name}
                </h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {segment.size.toLocaleString()} users ({segment.percentage}%)
                </p>
              </div>
              <div className="text-right">
                <span className="text-lg font-semibold text-green-600">
                  {segment.engagement_rate}%
                </span>
                <p className="text-sm text-gray-500">Engagement</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Demographics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Age Distribution */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Age Distribution
          </h3>
          <div className="space-y-3">
            {dashboard?.demographics.age_distribution?.map((age, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {age.age_range}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${age.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {age.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Gender Distribution */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Gender Distribution
          </h3>
          <div className="space-y-3">
            {dashboard?.demographics.gender_distribution?.map((gender, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-300 capitalize">
                  {gender.gender}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full" 
                      style={{ width: `${gender.percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {gender.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Content Preferences */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Content Preferences
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {dashboard?.engagement_insights.content_preferences?.map((pref, index) => (
            <div key={index} className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-white font-bold">
                  {Math.round(pref.preference_score * 100)}
                </span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                {pref.content_type}
              </h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {pref.avg_engagement}% avg engagement
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Growth Recommendations Tab Component
function RecommendationsTab() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['recommendations-dashboard'],
    queryFn: () => growthRecommendationsApi.getRecommendationsDashboard(),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading recommendations...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Recommendations Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Recommendations"
          value={dashboard?.summary.total_recommendations?.toString() || '0'}
          icon={LightBulbIcon}
          color="bg-yellow-500"
        />
        <MetricCard
          title="Quick Wins"
          value={dashboard?.summary.quick_wins?.toString() || '0'}
          icon={TrophyIcon}
          color="bg-green-500"
        />
        <MetricCard
          title="Urgent Actions"
          value={dashboard?.summary.urgent_recommendations?.toString() || '0'}
          icon={ExclamationTriangleIcon}
          color="bg-red-500"
        />
        <MetricCard
          title="Completion Rate"
          value={`${Math.round(dashboard?.summary.completion_rate || 0)}%`}
          icon={ChartBarIcon}
          color="bg-blue-500"
        />
      </div>

      {/* Top Recommendations */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Top Recommendations
        </h3>
        <div className="space-y-4">
          {dashboard?.top_recommendations?.slice(0, 5).map((rec) => (
            <div key={rec.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      rec.is_urgent 
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                    }`}>
                      {rec.category}
                    </span>
                    {rec.is_urgent && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300">
                        Urgent
                      </span>
                    )}
                  </div>
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {rec.title}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    {rec.description}
                  </p>
                  <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
                    <span>Impact: {Math.round(rec.impact_score * 100)}%</span>
                    <span>Confidence: {Math.round(rec.confidence_score * 100)}%</span>
                    <span>Effort: {rec.estimated_effort}</span>
                  </div>
                </div>
                <div className="ml-4 text-right">
                  <div className="text-lg font-semibold text-gray-900 dark:text-white">
                    {Math.round(rec.priority_score * 100)}
                  </div>
                  <div className="text-xs text-gray-500">Priority</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Wins */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Quick Wins (High Impact, Low Effort)
        </h3>
        <div className="space-y-3">
          {dashboard?.quick_wins?.map((rec) => (
            <div key={rec.id} className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {rec.title}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Expected time: {rec.estimated_time}
                </p>
              </div>
              <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                Implement
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Analytics & Insights
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Track your performance, analyze competitors, understand your audience, and get AI-powered growth recommendations.
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

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Tab Content */}
        <div className="mt-6">
          {activeTab === 'overview' && <OverviewTab selectedPeriod={selectedPeriod} />}
          {activeTab === 'competitors' && <CompetitorsTab />}
          {activeTab === 'audience' && <AudienceTab />}
          {activeTab === 'recommendations' && <RecommendationsTab />}
        </div>
      </div>
    </DashboardLayout>
  );
}