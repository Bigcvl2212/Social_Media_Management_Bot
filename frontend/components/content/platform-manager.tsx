"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Cog6ToothIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";

interface Platform {
  id: string;
  name: string;
  icon: string;
  connected: boolean;
  followers?: number;
  lastSync?: string;
}

export function PlatformManager() {
  const { data: platforms, isLoading } = useQuery({
    queryKey: ["platforms"],
    queryFn: async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/platforms`);
      if (!response.ok) throw new Error("Failed to fetch platforms");
      return response.json() as Promise<Platform[]>;
    },
  });

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Connected Platforms
        </h2>

        {isLoading ? (
          <div className="text-center py-8">Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms?.map((platform) => (
              <PlatformCard key={platform.id} platform={platform} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function PlatformCard({ platform }: { platform: Platform }) {
  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-bold text-gray-900 dark:text-white">{platform.name}</h3>
        {platform.connected ? (
          <CheckCircleIcon className="h-5 w-5 text-green-600" />
        ) : (
          <XCircleIcon className="h-5 w-5 text-red-600" />
        )}
      </div>

      {platform.connected && platform.followers && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          {platform.followers.toLocaleString()} followers
        </p>
      )}

      <button
        className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
          platform.connected
            ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100"
            : "bg-blue-600 text-white hover:bg-blue-700"
        }`}
      >
        {platform.connected ? "Reconnect" : "Connect"}
      </button>
    </div>
  );
}
