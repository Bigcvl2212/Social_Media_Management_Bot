"use client";

import { useSession } from "next-auth/react";
import { DashboardLayout } from "@/components/dashboard/layout";
import { UserIcon, EnvelopeIcon, CalendarIcon } from "@heroicons/react/24/outline";

export default function ProfilePage() {
  const { data: session } = useSession();

  if (!session) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Profile
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Manage your account information and preferences.
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="px-6 py-8">
            <div className="flex items-center space-x-6">
              {session.user?.image ? (
                <img
                  className="h-20 w-20 rounded-full ring-4 ring-white dark:ring-gray-700"
                  src={session.user.image}
                  alt="Profile"
                />
              ) : (
                <div className="h-20 w-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center ring-4 ring-white dark:ring-gray-700">
                  <span className="text-2xl font-medium text-white">
                    {session.user?.name
                      ?.split(" ")
                      .map((word) => word[0])
                      .join("")
                      .toUpperCase()
                      .slice(0, 2) || "U"}
                  </span>
                </div>
              )}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {session.user?.name || "User"}
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  {session.user?.email}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Account Information */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Account Information
            </h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <UserIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Name</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {session.user?.name || "Not provided"}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {session.user?.email || "Not provided"}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Session Information */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Session Information
            </h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <CalendarIcon className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Signed in via</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                    OAuth Provider
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-5 w-5 bg-green-500 rounded-full flex items-center justify-center">
                  <div className="h-2 w-2 bg-white rounded-full"></div>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Status</p>
                  <p className="text-sm font-medium text-green-600 dark:text-green-400">
                    Active Session
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Security Section */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Security
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  OAuth Authentication
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  You&apos;re signed in using a secure OAuth provider
                </p>
              </div>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Enabled
              </span>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}