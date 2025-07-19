"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  CalendarIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  PlusIcon,
  ViewColumnsIcon,
  ListBulletIcon,
} from "@heroicons/react/24/outline";
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, addMonths, subMonths } from "date-fns";
import { CalendarGrid } from "./calendar-grid";
import { ScheduleModal } from "./schedule-modal";
import { PostsList } from "./posts-list";

interface ScheduledPost {
  id: string;
  title: string;
  platform: string;
  scheduledDate: Date;
  status: "scheduled" | "published" | "failed";
  content: string;
  imageUrl?: string;
}

type ViewMode = "calendar" | "list";

export function CalendarView() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [isScheduleModalOpen, setIsScheduleModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("calendar");

  // Fetch scheduled posts
  const { data: scheduledPosts = [], isLoading, error } = useQuery({
    queryKey: ["scheduled-posts"],
    queryFn: async (): Promise<ScheduledPost[]> => {
      // Mock data for now - will connect to real API
      return [
        {
          id: "1",
          title: "Morning motivation post",
          platform: "Instagram",
          scheduledDate: new Date(2024, 11, 20, 9, 0),
          status: "scheduled",
          content: "Start your day with positive energy! ✨ #motivation #morningvibes",
          imageUrl: "/api/placeholder/400/400"
        },
        {
          id: "2", 
          title: "Product showcase",
          platform: "TikTok",
          scheduledDate: new Date(2024, 11, 22, 15, 30),
          status: "scheduled",
          content: "Check out our latest features! 🚀",
        },
        {
          id: "3",
          title: "Weekly roundup",
          platform: "LinkedIn",
          scheduledDate: new Date(2024, 11, 25, 10, 0),
          status: "published",
          content: "Here's what happened this week in our community...",
        }
      ];
    },
  });

  const navigateMonth = (direction: "prev" | "next") => {
    setCurrentDate(direction === "prev" ? subMonths(currentDate, 1) : addMonths(currentDate, 1));
  };

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setIsScheduleModalOpen(true);
  };

  const getPostsForDate = (date: Date) => {
    return scheduledPosts.filter(post => 
      isSameDay(new Date(post.scheduledDate), date)
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-2/3"></div>
        </div>
        <div className="animate-pulse">
          <div className="grid grid-cols-7 gap-4">
            {Array.from({ length: 35 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-300 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass rounded-xl p-8 border border-red-500/20 text-center">
        <div className="text-red-500 mb-4">
          <CalendarIcon className="h-12 w-12 mx-auto" />
        </div>
        <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">
          Failed to load calendar
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          There was an error loading your scheduled posts. Please try again.
        </p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold gradient-text">
            Content Calendar
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Schedule and manage your social media posts across all platforms
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {/* View Mode Toggle */}
          <div className="glass rounded-lg p-1 border border-white/10">
            <button
              onClick={() => setViewMode("calendar")}
              className={`p-2 rounded transition-colors ${
                viewMode === "calendar" 
                  ? "bg-blue-500 text-white" 
                  : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              }`}
            >
              <ViewColumnsIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`p-2 rounded transition-colors ${
                viewMode === "list" 
                  ? "bg-blue-500 text-white" 
                  : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              }`}
            >
              <ListBulletIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Schedule New Post Button */}
          <button
            onClick={() => setIsScheduleModalOpen(true)}
            className="interactive-card bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all duration-300 flex items-center gap-2"
          >
            <PlusIcon className="h-5 w-5" />
            Schedule Post
          </button>
        </div>
      </div>

      {/* Calendar Navigation */}
      {viewMode === "calendar" && (
        <div className="glass rounded-xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">
              {format(currentDate, "MMMM yyyy")}
            </h2>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => navigateMonth("prev")}
                className="p-2 rounded-lg glass-strong hover:bg-white/20 transition-colors"
              >
                <ChevronLeftIcon className="h-5 w-5 text-gray-300" />
              </button>
              <button
                onClick={() => setCurrentDate(new Date())}
                className="px-3 py-1 text-sm rounded-lg glass-strong hover:bg-white/20 transition-colors text-gray-300"
              >
                Today
              </button>
              <button
                onClick={() => navigateMonth("next")}
                className="p-2 rounded-lg glass-strong hover:bg-white/20 transition-colors"
              >
                <ChevronRightIcon className="h-5 w-5 text-gray-300" />
              </button>
            </div>
          </div>

          <CalendarGrid
            currentDate={currentDate}
            scheduledPosts={scheduledPosts}
            onDateSelect={handleDateSelect}
            getPostsForDate={getPostsForDate}
          />
        </div>
      )}

      {/* List View */}
      {viewMode === "list" && (
        <PostsList scheduledPosts={scheduledPosts} />
      )}

      {/* Schedule Modal */}
      <ScheduleModal
        isOpen={isScheduleModalOpen}
        onClose={() => setIsScheduleModalOpen(false)}
        selectedDate={selectedDate}
      />
    </div>
  );
}