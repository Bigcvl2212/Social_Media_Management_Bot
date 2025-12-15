"use client";

import { useState } from "react";
import { CalendarIcon, PlusIcon } from "@heroicons/react/24/outline";

export function ContentScheduler() {
  const [view, setView] = useState<"month" | "week" | "list">("month");

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Content Calendar</h2>
          <p className="text-gray-600 dark:text-gray-400">Drag and drop to schedule posts</p>
        </div>

        <div className="flex gap-2">
          {(["month", "week", "list"] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                view === v
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300"
              }`}
            >
              {v.charAt(0).toUpperCase() + v.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Calendar Placeholder */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 border border-gray-200 dark:border-gray-700">
        <div className="text-center py-12">
          <CalendarIcon className="h-16 w-16 mx-auto text-blue-600 dark:text-blue-400 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            Drag content from library to schedule posts
          </p>
          <button className="mt-6 bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700">
            <PlusIcon className="h-5 w-5 inline mr-2" />
            Add to Schedule
          </button>
        </div>
      </div>
    </div>
  );
}
