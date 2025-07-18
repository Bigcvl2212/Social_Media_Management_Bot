import { DashboardLayout } from "@/components/dashboard/layout";

export default function AccountsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Social Media Accounts
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Connect and manage your social media accounts across all platforms.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Instagram */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">IG</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Instagram</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
              </div>
            </div>
            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Connect Account
              </button>
            </div>
          </div>

          {/* TikTok */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-black rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">TT</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">TikTok</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
              </div>
            </div>
            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Connect Account
              </button>
            </div>
          </div>

          {/* YouTube */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-red-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">YT</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">YouTube</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
              </div>
            </div>
            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Connect Account
              </button>
            </div>
          </div>

          {/* Twitter/X */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-black rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">X</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">X (Twitter)</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
              </div>
            </div>
            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Connect Account
              </button>
            </div>
          </div>

          {/* Facebook */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">FB</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Facebook</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
              </div>
            </div>
            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Connect Account
              </button>
            </div>
          </div>

          {/* LinkedIn */}
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 bg-blue-700 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">LI</span>
                </div>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">LinkedIn</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
              </div>
            </div>
            <div className="mt-4">
              <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Connect Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}