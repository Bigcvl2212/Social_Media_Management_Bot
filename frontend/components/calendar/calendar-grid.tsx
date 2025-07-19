"use client";

import { format, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, isToday } from "date-fns";
import { clsx } from "clsx";

interface ScheduledPost {
  id: string;
  title: string;
  platform: string;
  scheduledDate: Date;
  status: "scheduled" | "published" | "failed";
  content: string;
  imageUrl?: string;
}

interface CalendarGridProps {
  currentDate: Date;
  scheduledPosts: ScheduledPost[];
  onDateSelect: (date: Date) => void;
  getPostsForDate: (date: Date) => ScheduledPost[];
}

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const platformColors = {
  Instagram: "bg-gradient-to-r from-purple-500 to-pink-500",
  TikTok: "bg-black",
  YouTube: "bg-red-600",
  Twitter: "bg-black",
  Facebook: "bg-blue-600",
  LinkedIn: "bg-blue-700",
} as const;

export function CalendarGrid({ currentDate, scheduledPosts, onDateSelect, getPostsForDate }: CalendarGridProps) {
  const startDate = startOfWeek(currentDate);
  const endDate = endOfWeek(currentDate);
  
  const days = [];
  let day = startDate;
  
  while (day <= endDate) {
    const monthStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const monthEnd = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    
    for (let i = 0; i < 7; i++) {
      days.push(addDays(day, i));
    }
    day = addDays(day, 7);
  }

  // Get 6 weeks of days for consistent calendar height
  const calendarDays = [];
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  const startCalendar = startOfWeek(firstDayOfMonth);
  
  for (let i = 0; i < 42; i++) { // 6 weeks × 7 days
    calendarDays.push(addDays(startCalendar, i));
  }

  return (
    <div className="space-y-4">
      {/* Weekday Headers */}
      <div className="grid grid-cols-7 gap-1">
        {WEEKDAYS.map((weekday) => (
          <div key={weekday} className="p-3 text-center text-sm font-medium text-gray-400">
            {weekday}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1">
        {calendarDays.map((day, index) => {
          const isCurrentMonth = isSameMonth(day, currentDate);
          const isCurrentDay = isSameDay(day, new Date());
          const dayPosts = getPostsForDate(day);

          return (
            <div
              key={day.toISOString()}
              onClick={() => onDateSelect(day)}
              className={clsx(
                "min-h-[100px] p-2 border border-white/10 rounded-lg cursor-pointer transition-all duration-200 hover:bg-white/5",
                isCurrentMonth ? "glass-strong" : "opacity-40",
                isCurrentDay && "ring-2 ring-blue-400"
              )}
            >
              {/* Day Number */}
              <div className={clsx(
                "text-sm font-medium mb-2",
                isCurrentDay 
                  ? "text-blue-400" 
                  : isCurrentMonth 
                    ? "text-white" 
                    : "text-gray-500"
              )}>
                {format(day, "d")}
              </div>

              {/* Posts */}
              <div className="space-y-1">
                {dayPosts.slice(0, 3).map((post) => (
                  <div
                    key={post.id}
                    className={clsx(
                      "text-xs p-1 rounded text-white truncate",
                      platformColors[post.platform as keyof typeof platformColors] || "bg-gray-600"
                    )}
                    title={`${post.platform}: ${post.title}`}
                  >
                    {post.title}
                  </div>
                ))}
                
                {dayPosts.length > 3 && (
                  <div className="text-xs text-gray-400 font-medium">
                    +{dayPosts.length - 3} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 pt-4 border-t border-white/10">
        <div className="text-sm text-gray-400 font-medium">Platforms:</div>
        {Object.entries(platformColors).map(([platform, colorClass]) => (
          <div key={platform} className="flex items-center gap-2">
            <div className={clsx("w-3 h-3 rounded", colorClass)}></div>
            <span className="text-sm text-gray-300">{platform}</span>
          </div>
        ))}
      </div>
    </div>
  );
}