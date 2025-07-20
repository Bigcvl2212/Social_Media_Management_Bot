
"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  ClockIcon,
  PlusIcon,
  PhotoIcon,
  VideoCameraIcon,
  DocumentTextIcon,
} from "@heroicons/react/24/outline";
import { contentApi, CalendarEvent, ContentType, ScheduleStatus } from "@/lib/content-api";

const contentTypeIcons = {
  [ContentType.IMAGE]: PhotoIcon,
  [ContentType.VIDEO]: VideoCameraIcon,
  [ContentType.TEXT]: DocumentTextIcon,
  [ContentType.CAROUSEL]: PhotoIcon,
  [ContentType.STORY]: PhotoIcon,
  [ContentType.REEL]: VideoCameraIcon,
};

const statusColors = {
  [ScheduleStatus.PENDING]: "bg-yellow-100 text-yellow-800 border-yellow-200",
  [ScheduleStatus.PROCESSING]: "bg-blue-100 text-blue-800 border-blue-200",
  [ScheduleStatus.COMPLETED]: "bg-green-100 text-green-800 border-green-200",
  [ScheduleStatus.FAILED]: "bg-red-100 text-red-800 border-red-200",
  [ScheduleStatus.CANCELLED]: "bg-gray-100 text-gray-800 border-gray-200",
};

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: CalendarEvent[];
}

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  
  // Calculate calendar month boundaries
  const monthStart = useMemo(() => {
    const start = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    return start;
  }, [currentDate]);
  
  const monthEnd = useMemo(() => {
    const end = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    return end;
  }, [currentDate]);
  
  // Extend to show full weeks
  const calendarStart = useMemo(() => {
    const start = new Date(monthStart);
    start.setDate(start.getDate() - start.getDay()); // Go to Sunday
    return start;
  }, [monthStart]);
  
  const calendarEnd = useMemo(() => {
    const end = new Date(monthEnd);
    end.setDate(end.getDate() + (6 - end.getDay())); // Go to Saturday
    return end;
  }, [monthEnd]);
  
  // Fetch calendar events for the visible period
  const { data: eventsData, isLoading } = useQuery({
    queryKey: ['calendar-events', calendarStart, calendarEnd],
    queryFn: () => contentApi.getCalendarEvents(calendarStart, calendarEnd),
  });
  
  // Generate calendar days
  const calendarDays = useMemo(() => {
    const days: CalendarDay[] = [];
    const current = new Date(calendarStart);
    const today = new Date();
    
    while (current <= calendarEnd) {
      const dayEvents = eventsData?.events?.filter(event => {
        const eventDate = new Date(event.scheduled_time);
        return eventDate.toDateString() === current.toDateString();
      }) || [];
      
      days.push({
        date: new Date(current),
        isCurrentMonth: current.getMonth() === currentDate.getMonth(),
        isToday: current.toDateString() === today.toDateString(),
        events: dayEvents,
      });
      
      current.setDate(current.getDate() + 1);
    }
    
    return days;
  }, [calendarStart, calendarEnd, currentDate, eventsData]);
  
  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };
  
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Content Calendar
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              Schedule and manage your content across all platforms.
            </p>
          </div>
          <button className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
            <PlusIcon className="h-5 w-5 mr-2" />
            Schedule Post
          </button>
        </div>

        {/* Calendar Controls */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {currentDate.toLocaleDateString('en-US', { 
                month: 'long', 
                year: 'numeric' 
              })}
            </h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateMonth('prev')}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <ChevronLeftIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => setCurrentDate(new Date())}
                className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                Today
              </button>
              <button
                onClick={() => navigateMonth('next')}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <ChevronRightIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600 dark:text-gray-400">Loading calendar...</p>
            </div>
          ) : (
            <div className="grid grid-cols-7">
              {/* Day headers */}
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div
                  key={day}
                  className="bg-gray-50 dark:bg-gray-700 px-4 py-3 text-sm font-medium text-gray-500 dark:text-gray-400 text-center border-b border-gray-200 dark:border-gray-600"
                >
                  {day}
                </div>
              ))}
              
              {/* Calendar days */}
              {calendarDays.map((day, index) => (
                <div
                  key={index}
                  className={`min-h-[120px] border-r border-b border-gray-200 dark:border-gray-600 p-2 ${
                    !day.isCurrentMonth 
                      ? 'bg-gray-50 dark:bg-gray-700' 
                      : 'bg-white dark:bg-gray-800'
                  } ${
                    day.isToday 
                      ? 'bg-blue-50 dark:bg-blue-900/20' 
                      : ''
                  }`}
                >
                  <div className={`text-sm font-medium mb-2 ${
                    !day.isCurrentMonth 
                      ? 'text-gray-400 dark:text-gray-500' 
                      : day.isToday
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {day.date.getDate()}
                  </div>
                  
                  <div className="space-y-1">
                    {day.events.slice(0, 3).map((event) => {
                      const Icon = contentTypeIcons[event.content_type];
                      return (
                        <div
                          key={event.id}
                          onClick={() => setSelectedEvent(event)}
                          className={`text-xs p-1 rounded border cursor-pointer hover:shadow-sm ${statusColors[event.status]}`}
                        >
                          <div className="flex items-center space-x-1">
                            <Icon className="h-3 w-3 flex-shrink-0" />
                            <span className="truncate font-medium">
                              {event.title}
                            </span>
                          </div>
                          <div className="flex items-center space-x-1 mt-1">
                            <ClockIcon className="h-3 w-3 flex-shrink-0" />
                            <span>{formatTime(event.scheduled_time)}</span>
                          </div>
                        </div>
                      );
                    })}
                    
                    {day.events.length > 3 && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 px-1">
                        +{day.events.length - 3} more
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Event Details Modal */}
        {selectedEvent && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Scheduled Post Details
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Title
                    </label>
                    <p className="mt-1 text-sm text-gray-900 dark:text-white">
                      {selectedEvent.title}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Content Type
                    </label>
                    <div className="mt-1 flex items-center space-x-2">
                      {(() => {
                        const Icon = contentTypeIcons[selectedEvent.content_type];
                        return <Icon className="h-4 w-4" />;
                      })()}
                      <span className="text-sm text-gray-900 dark:text-white">
                        {selectedEvent.content_type}
                      </span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Platform
                    </label>
                    <p className="mt-1 text-sm text-gray-900 dark:text-white">
                      {selectedEvent.platform}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Scheduled Time
                    </label>
                    <p className="mt-1 text-sm text-gray-900 dark:text-white">
                      {formatDate(selectedEvent.scheduled_time)} at {formatTime(selectedEvent.scheduled_time)}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Status
                    </label>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${statusColors[selectedEvent.status]}`}>
                      {selectedEvent.status}
                    </span>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                  >
                    Close
                  </button>
                  <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md">
                    Edit Schedule
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}