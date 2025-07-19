"use client";

import { DashboardLayout } from "@/components/dashboard/layout";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  LinkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ArrowPathIcon,
  Cog6ToothIcon,
  PlusIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import {
  socialAccountsApi,
  SocialAccount,
  SocialPlatform,
  AccountStatus,
  Platform,
} from "@/lib/social-accounts-api";

const platformColors = {
  [SocialPlatform.INSTAGRAM]: "bg-gradient-to-r from-purple-500 to-pink-500",
  [SocialPlatform.TIKTOK]: "bg-black",
  [SocialPlatform.YOUTUBE]: "bg-red-600",
  [SocialPlatform.TWITTER]: "bg-black",
  [SocialPlatform.FACEBOOK]: "bg-blue-600",
  [SocialPlatform.LINKEDIN]: "bg-blue-700",
};

const platformAbbreviation = {
  [SocialPlatform.INSTAGRAM]: "IG",
  [SocialPlatform.TIKTOK]: "TT",
  [SocialPlatform.YOUTUBE]: "YT",
  [SocialPlatform.TWITTER]: "X",
  [SocialPlatform.FACEBOOK]: "FB",
  [SocialPlatform.LINKEDIN]: "LI",
};

const statusColors = {
  [AccountStatus.CONNECTED]: "text-green-600 bg-green-100",
  [AccountStatus.DISCONNECTED]: "text-gray-600 bg-gray-100",
  [AccountStatus.ERROR]: "text-red-600 bg-red-100",
  [AccountStatus.EXPIRED]: "text-yellow-600 bg-yellow-100",
  [AccountStatus.PENDING]: "text-blue-600 bg-blue-100",
};

const statusIcons = {
  [AccountStatus.CONNECTED]: CheckCircleIcon,
  [AccountStatus.DISCONNECTED]: XCircleIcon,
  [AccountStatus.ERROR]: ExclamationTriangleIcon,
  [AccountStatus.EXPIRED]: ExclamationTriangleIcon,
  [AccountStatus.PENDING]: ClockIcon,
};

export default function AccountsPage() {
  const [selectedAccount, setSelectedAccount] = useState<SocialAccount | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const queryClient = useQueryClient();

  // Fetch social accounts
  const { data: accounts } = useQuery({
    queryKey: ['social-accounts'],
    queryFn: socialAccountsApi.getAccounts,
  });

  // Fetch available platforms
  const { data: platformsData } = useQuery({
    queryKey: ['social-platforms'],
    queryFn: socialAccountsApi.getPlatforms,
  });

  // Fetch account stats
  const { data: stats } = useQuery({
    queryKey: ['social-accounts-stats'],
    queryFn: socialAccountsApi.getStats,
  });

  // Connect account mutation
  const connectMutation = useMutation({
    mutationFn: async (platform: SocialPlatform) => {
      const result = await socialAccountsApi.startOAuth(platform);
      if (result.auth_url) {
        window.location.href = result.auth_url;
      } else {
        throw new Error(result.message || 'Failed to get auth URL');
      }
    },
    onError: (error) => {
      console.error('Failed to start OAuth:', error);
    },
  });

  // Disconnect account mutation
  const disconnectMutation = useMutation({
    mutationFn: socialAccountsApi.disconnectAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['social-accounts'] });
      queryClient.invalidateQueries({ queryKey: ['social-accounts-stats'] });
    },
  });

  // Sync account mutation
  const syncMutation = useMutation({
    mutationFn: socialAccountsApi.syncAccount,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['social-accounts'] });
    },
  });

  // Update account mutation
  const updateMutation = useMutation({
    mutationFn: ({ accountId, data }: { accountId: string; data: { auto_post?: boolean; auto_engage?: boolean } }) =>
      socialAccountsApi.updateAccount(accountId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['social-accounts'] });
      setShowSettings(false);
    },
  });

  const getConnectedAccount = (platform: SocialPlatform): SocialAccount | undefined => {
    return accounts?.accounts?.find(
      (acc) => acc.platform === platform && acc.status === AccountStatus.CONNECTED
    );
  };

  const handleConnect = (platform: SocialPlatform) => {
    connectMutation.mutate(platform);
  };

  const handleDisconnect = (accountId: string) => {
    if (confirm('Are you sure you want to disconnect this account?')) {
      disconnectMutation.mutate(accountId);
    }
  };

  const handleSync = (accountId: string) => {
    syncMutation.mutate(accountId);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Social Media Accounts
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            Connect and manage your social media accounts across all platforms.
          </p>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Account Overview
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {stats.connected_accounts}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Connected</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">
                  {stats.total_accounts}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {stats.total_accounts > 0 ? Math.round((stats.connected_accounts / stats.total_accounts) * 100) : 0}%
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Connection Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {Object.values(stats.by_platform || {}).filter(count => count > 0).length}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Platforms</div>
              </div>
            </div>
          </div>
        )}

        {/* Accounts Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {platformsData?.map((platform: Platform) => {
            const connectedAccount = getConnectedAccount(platform.platform as SocialPlatform);
            const isConnected = connectedAccount?.status === AccountStatus.CONNECTED;
            const StatusIcon = connectedAccount ? statusIcons[connectedAccount.status] : LinkIcon;

            return (
              <div
                key={platform.platform}
                className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div
                      className={`flex-shrink-0 h-10 w-10 ${
                        platformColors[platform.platform as SocialPlatform]
                      } rounded-lg flex items-center justify-center`}
                    >
                      <span className="text-white font-bold text-sm">
                        {platformAbbreviation[platform.platform as SocialPlatform]}
                      </span>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {platform.name}
                      </h3>
                      {connectedAccount ? (
                        <div className="flex items-center space-x-2">
                          <span
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              statusColors[connectedAccount.status]
                            }`}
                          >
                            <StatusIcon className="h-3 w-3 mr-1" />
                            {connectedAccount.status}
                          </span>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 dark:text-gray-400">Not connected</p>
                      )}
                    </div>
                  </div>

                  {connectedAccount && (
                    <button
                      onClick={() => {
                        setSelectedAccount(connectedAccount);
                        setShowSettings(true);
                      }}
                      className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <Cog6ToothIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>

                {connectedAccount && (
                  <div className="mt-4 space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-500 dark:text-gray-400">Username: </span>
                      <span className="text-gray-900 dark:text-white">
                        {connectedAccount.username}
                      </span>
                    </div>
                    {connectedAccount.display_name && (
                      <div className="text-sm">
                        <span className="text-gray-500 dark:text-gray-400">Display Name: </span>
                        <span className="text-gray-900 dark:text-white">
                          {connectedAccount.display_name}
                        </span>
                      </div>
                    )}
                    {connectedAccount.last_sync && (
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Last sync: {new Date(connectedAccount.last_sync).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                )}

                <div className="mt-4 space-y-2">
                  {isConnected ? (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSync(connectedAccount!.id)}
                        disabled={syncMutation.isPending}
                        className="flex-1 flex items-center justify-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50"
                      >
                        <ArrowPathIcon className="h-4 w-4 mr-1" />
                        Sync
                      </button>
                      <button
                        onClick={() => handleDisconnect(connectedAccount!.id)}
                        disabled={disconnectMutation.isPending}
                        className="flex-1 px-3 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-red-50 hover:bg-red-100 disabled:opacity-50"
                      >
                        Disconnect
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleConnect(platform.platform as SocialPlatform)}
                      disabled={connectMutation.isPending}
                      className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                    >
                      <PlusIcon className="h-4 w-4 mr-1" />
                      Connect Account
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Account Settings Modal */}
        {showSettings && selectedAccount && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Account Settings
                </h3>
                
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.currentTarget);
                    updateMutation.mutate({
                      accountId: selectedAccount.id,
                      data: {
                        auto_post: formData.get('auto_post') === 'on',
                        auto_engage: formData.get('auto_engage') === 'on',
                      },
                    });
                  }}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Platform
                    </label>
                    <p className="text-sm text-gray-900 dark:text-white capitalize">
                      {selectedAccount.platform} ({selectedAccount.username})
                    </p>
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="auto_post"
                        defaultChecked={selectedAccount.account_settings?.auto_post as boolean}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                        Enable automatic posting
                      </span>
                    </label>
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="auto_engage"
                        defaultChecked={selectedAccount.account_settings?.auto_engage as boolean}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                        Enable automatic engagement
                      </span>
                    </label>
                  </div>

                  {selectedAccount.permissions && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Permissions
                      </label>
                      <div className="flex flex-wrap gap-1">
                        {selectedAccount.permissions.map((permission) => (
                          <span
                            key={permission}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                          >
                            {permission}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowSettings(false)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={updateMutation.isPending}
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50"
                    >
                      {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}