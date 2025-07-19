"use client";

import {
  ChartBarIcon,
  PhotoIcon,
  CalendarIcon,
  UserGroupIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  SparklesIcon,
  RocketLaunchIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/analytics-api";
import { contentApi } from "@/lib/content-api";
import { socialAccountsApi } from "@/lib/social-accounts-api";

const recentActivity = [
  {
    id: 1,
    type: "post",
    content: "New Instagram post published",
    platform: "Instagram",
    time: "2 minutes ago",
    status: "success",
    engagement: "1.2K likes",
    icon: PhotoIcon,
  },
  {
    id: 2,
    type: "schedule",
    content: "TikTok video scheduled for 3 PM",
    platform: "TikTok",
    time: "15 minutes ago",
    status: "scheduled",
    engagement: "Scheduled",
    icon: CalendarIcon,
  },
  {
    id: 3,
    type: "engagement",
    content: "High engagement on YouTube video",
    platform: "YouTube",
    time: "1 hour ago",
    status: "success",
    engagement: "15K views",
    icon: ArrowTrendingUpIcon,
  },
  {
    id: 4,
    type: "ai",
    content: "AI generated 5 new post captions",
    platform: "AI Assistant",
    time: "2 hours ago",
    status: "info",
    engagement: "Ready to use",
    icon: SparklesIcon,
  },
];

function AnimatedCounter({ value, duration = 2000, suffix = "" }: { value: number; duration?: number; suffix?: string }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    const startValue = 0;
    const endValue = value;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      
      setCount(Math.floor(startValue + (endValue - startValue) * progress));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    const timer = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(timer);
  }, [value, duration]);

  return <span>{count.toLocaleString()}{suffix}</span>;
}

export function DashboardOverview() {
  // Fetch real dashboard data
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard-data'],
    queryFn: analyticsApi.getDashboardData,
  });

  const { data: contentStats } = useQuery({
    queryKey: ['content-stats'],
    queryFn: contentApi.getContentStats,
  });

  const { data: accountsStats } = useQuery({
    queryKey: ['social-accounts-stats'],
    queryFn: socialAccountsApi.getStats,
  });

  // Create stats from real data
  const stats = [
    {
      name: "Total Posts",
      value: contentStats?.total_content || 0,
      change: "+12%",
      changeType: "increase" as const,
      icon: PhotoIcon,
      gradient: "from-blue-500 to-cyan-500",
      description: "Published content",
    },
    {
      name: "Total Engagement",
      value: dashboardData ? Math.round(dashboardData.total_engagement / 1000 * 10) / 10 : 0,
      change: dashboardData ? `${dashboardData.engagement_growth >= 0 ? '+' : ''}${dashboardData.engagement_growth}%` : "+0%",
      changeType: (dashboardData?.engagement_growth || 0) >= 0 ? "increase" as const : "decrease" as const,
      icon: ChartBarIcon,
      gradient: "from-purple-500 to-pink-500",
      description: "Likes, comments & shares",
    },
    {
      name: "Scheduled Posts",
      value: dashboardData?.scheduled_posts || 0,
      change: "-2%",
      changeType: "decrease" as const,
      icon: CalendarIcon,
      gradient: "from-green-500 to-teal-500",
      description: "Ready to publish",
    },
    {
      name: "Connected Accounts",
      value: accountsStats?.connected_accounts || 0,
      change: "+1",
      changeType: "increase" as const,
      icon: UserGroupIcon,
      gradient: "from-orange-500 to-red-500",
      description: "Active platforms",
    },
  ];
  return (
    <div className="space-y-8">
      {/* Welcome section with enhanced styling */}
      <div className="text-center lg:text-left">
        <h1 className="text-4xl lg:text-5xl font-bold gradient-text animate-slide-in-up">
          Welcome back!
        </h1>
        <p className="mt-3 text-lg text-gray-300 animate-slide-in-up" style={{animationDelay: '200ms'}}>
          Here&apos;s what&apos;s happening with your social media empire today.
        </p>
        <div className="mt-4 flex items-center justify-center lg:justify-start space-x-2 animate-slide-in-up" style={{animationDelay: '400ms'}}>
          <div className="h-2 w-2 bg-green-400 rounded-full animate-glow"></div>
          <span className="text-sm text-gray-400">All systems operational</span>
        </div>
      </div>

      {/* Enhanced Stats with animations and glassmorphism */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <div
            key={stat.name}
            className={`relative overflow-hidden glass rounded-2xl p-6 interactive-card animate-slide-in-up`}
            style={{animationDelay: `${index * 150 + 600}ms`}}
          >
            {/* Gradient background overlay */}
            <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-10`}></div>
            
            {/* Animated background pattern */}
            <div className="absolute inset-0 animate-float" style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='m0 40h40v-40h-40z'/%3E%3C/g%3E%3C/svg%3E")`
            }}></div>
            
            <div className="relative">
              <div className="flex items-center justify-between">
                <div className={`flex-shrink-0 p-3 rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg`}>
                  <stat.icon
                    className="h-6 w-6 text-white"
                    aria-hidden="true"
                  />
                </div>
                <div
                  className={`flex items-center text-sm font-semibold ${
                    stat.changeType === "increase"
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {stat.changeType === "increase" ? (
                    <ArrowUpIcon className="h-4 w-4 mr-1" />
                  ) : (
                    <ArrowDownIcon className="h-4 w-4 mr-1" />
                  )}
                  {stat.change}
                </div>
              </div>
              
              <div className="mt-4">
                <div className="text-3xl font-bold text-white">
                  <AnimatedCounter value={stat.value} suffix={stat.name === "Total Engagement" ? "K" : ""} />
                </div>
                <div className="text-sm font-medium text-gray-300 mt-1">
                  {stat.name}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {stat.description}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Enhanced Activity and Actions Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Recent Activity with enhanced design */}
        <div className="xl:col-span-2 glass rounded-2xl p-6 animate-fade-in-scale" style={{animationDelay: '1200ms'}}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white flex items-center">
              <SparklesIcon className="h-6 w-6 mr-2 text-blue-400" />
              Recent Activity
            </h3>
            <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
              View all
            </button>
          </div>
          
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="group glass rounded-xl p-4 hover:bg-white/5 transition-all duration-300 interactive-card"
              >
                <div className="flex items-start space-x-4">
                  <div className={`flex-shrink-0 p-2 rounded-lg ${
                    activity.status === "success"
                      ? "bg-green-500/20 text-green-400"
                      : activity.status === "scheduled"
                      ? "bg-blue-500/20 text-blue-400"
                      : "bg-purple-500/20 text-purple-400"
                  }`}>
                    <activity.icon className="h-5 w-5" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">
                        {activity.content}
                      </p>
                      <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                        {activity.time}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <p className="text-xs text-gray-400">{activity.platform}</p>
                      <p className="text-xs text-blue-400 font-medium">{activity.engagement}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Enhanced Quick Actions */}
        <div className="space-y-6">
          {/* AI Quick Actions */}
          <div className="glass rounded-2xl p-6 animate-fade-in-scale" style={{animationDelay: '1400ms'}}>
            <h3 className="text-lg font-bold text-white mb-4 flex items-center">
              <RocketLaunchIcon className="h-5 w-5 mr-2 text-purple-400" />
              Quick Actions
            </h3>
            
            <div className="space-y-3">
              <button className="w-full glass rounded-xl p-4 text-left hover:bg-white/5 transition-all duration-300 interactive-card group">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                    <PhotoIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">
                      Create AI Post
                    </p>
                    <p className="text-xs text-gray-400">Generate with AI</p>
                  </div>
                </div>
              </button>
              
              <button className="w-full glass rounded-xl p-4 text-left hover:bg-white/5 transition-all duration-300 interactive-card group">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-green-500 to-teal-600">
                    <CalendarIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white group-hover:text-green-300 transition-colors">
                      Schedule Content
                    </p>
                    <p className="text-xs text-gray-400">Plan your posts</p>
                  </div>
                </div>
              </button>
              
              <button className="w-full glass rounded-xl p-4 text-left hover:bg-white/5 transition-all duration-300 interactive-card group">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-red-600">
                    <EyeIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white group-hover:text-orange-300 transition-colors">
                      Analytics Insights
                    </p>
                    <p className="text-xs text-gray-400">View performance</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* AI Assistant Card */}
          <div className="glass rounded-2xl p-6 bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-500/20 animate-fade-in-scale" style={{animationDelay: '1600ms'}}>
            <div className="text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center mb-4 animate-glow">
                <SparklesIcon className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-lg font-bold text-white mb-2">AI Assistant</h4>
              <p className="text-sm text-gray-300 mb-4">
                Ready to help you create amazing content
              </p>
              <button className="btn-gradient w-full">
                Start Creating
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}