"use client";

import {
  ChartBarIcon,
  PhotoIcon,
  CalendarIcon,
  UserGroupIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from "@heroicons/react/24/outline";

const stats = [
  {
    name: "Total Posts",
    value: "2,547",
    change: "+12%",
    changeType: "increase",
    icon: PhotoIcon,
  },
  {
    name: "Total Engagement",
    value: "84.2K",
    change: "+5.4%",
    changeType: "increase",
    icon: ChartBarIcon,
  },
  {
    name: "Scheduled Posts",
    value: "23",
    change: "-2%",
    changeType: "decrease",
    icon: CalendarIcon,
  },
  {
    name: "Connected Accounts",
    value: "8",
    change: "+1",
    changeType: "increase",
    icon: UserGroupIcon,
  },
];

const recentActivity = [
  {
    id: 1,
    type: "post",
    content: "New Instagram post published",
    platform: "Instagram",
    time: "2 minutes ago",
    status: "success",
  },
  {
    id: 2,
    type: "schedule",
    content: "TikTok video scheduled for 3 PM",
    platform: "TikTok",
    time: "15 minutes ago",
    status: "scheduled",
  },
  {
    id: 3,
    type: "engagement",
    content: "High engagement on YouTube video",
    platform: "YouTube",
    time: "1 hour ago",
    status: "success",
  },
  {
    id: 4,
    type: "ai",
    content: "AI generated 5 new post captions",
    platform: "AI Assistant",
    time: "2 hours ago",
    status: "info",
  },
];

export function DashboardOverview() {
  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back!
        </h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Here's what's happening with your social media accounts today.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="relative overflow-hidden rounded-lg bg-white dark:bg-gray-800 px-4 py-5 shadow border border-gray-200 dark:border-gray-700 sm:px-6 sm:py-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon
                  className="h-8 w-8 text-blue-600 dark:text-blue-400"
                  aria-hidden="true"
                />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-gray-500 dark:text-gray-400">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900 dark:text-white">
                      {stat.value}
                    </div>
                    <div
                      className={`ml-2 flex items-baseline text-sm font-semibold ${
                        stat.changeType === "increase"
                          ? "text-green-600 dark:text-green-400"
                          : "text-red-600 dark:text-red-400"
                      }`}
                    >
                      {stat.changeType === "increase" ? (
                        <ArrowUpIcon className="h-3 w-3 flex-shrink-0 self-center" />
                      ) : (
                        <ArrowDownIcon className="h-3 w-3 flex-shrink-0 self-center" />
                      )}
                      <span className="sr-only">
                        {stat.changeType === "increase" ? "Increased" : "Decreased"} by
                      </span>
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              Recent Activity
            </h3>
            <div className="mt-5">
              <div className="flow-root">
                <ul role="list" className="-mb-8">
                  {recentActivity.map((activity, activityIdx) => (
                    <li key={activity.id}>
                      <div className="relative pb-8">
                        {activityIdx !== recentActivity.length - 1 ? (
                          <span
                            className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-600"
                            aria-hidden="true"
                          />
                        ) : null}
                        <div className="relative flex space-x-3">
                          <div>
                            <span
                              className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white dark:ring-gray-800 ${
                                activity.status === "success"
                                  ? "bg-green-500"
                                  : activity.status === "scheduled"
                                  ? "bg-blue-500"
                                  : "bg-gray-500"
                              }`}
                            >
                              <PhotoIcon className="h-4 w-4 text-white" aria-hidden="true" />
                            </span>
                          </div>
                          <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                            <div>
                              <p className="text-sm text-gray-900 dark:text-white">
                                {activity.content}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {activity.platform}
                              </p>
                            </div>
                            <div className="whitespace-nowrap text-right text-sm text-gray-500 dark:text-gray-400">
                              {activity.time}
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900 dark:text-white">
              Quick Actions
            </h3>
            <div className="mt-5 grid grid-cols-1 gap-4">
              <button className="relative block w-full rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 p-12 text-center hover:border-gray-400 dark:hover:border-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                <PhotoIcon className="mx-auto h-12 w-12 text-gray-400" />
                <span className="mt-2 block text-sm font-medium text-gray-900 dark:text-white">
                  Create New Post
                </span>
              </button>
              
              <div className="grid grid-cols-2 gap-4">
                <button className="flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                  Schedule Content
                </button>
                <button className="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                  AI Generate
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}