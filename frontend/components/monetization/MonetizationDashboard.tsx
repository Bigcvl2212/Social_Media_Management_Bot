/**
 * Monetization Dashboard Component
 * 
 * Displays an overview of monetization features including:
 * - Brand collaboration opportunities
 * - Active campaigns
 * - Affiliate link performance
 * - Earnings summary
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  CurrencyDollarIcon, 
  BuildingOfficeIcon,
  LinkIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';

interface MonetizationStats {
  totalEarnings: number;
  activeCollaborations: number;
  pendingCollaborations: number;
  activeAffiliateLinks: number;
  totalClicks: number;
  totalConversions: number;
  conversionRate: number;
}

interface RecentActivity {
  id: number;
  type: 'collaboration' | 'affiliate' | 'campaign';
  title: string;
  amount?: number;
  status: string;
  date: string;
}

export default function MonetizationDashboard() {
  const [stats, setStats] = useState<MonetizationStats>({
    totalEarnings: 0,
    activeCollaborations: 0,
    pendingCollaborations: 0,
    activeAffiliateLinks: 0,
    totalClicks: 0,
    totalConversions: 0,
    conversionRate: 0
  });

  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMonetizationData();
  }, []);

  const fetchMonetizationData = async () => {
    try {
      // Mock data for now - replace with actual API calls
      setStats({
        totalEarnings: 15750.50,
        activeCollaborations: 3,
        pendingCollaborations: 2,
        activeAffiliateLinks: 8,
        totalClicks: 1250,
        totalConversions: 47,
        conversionRate: 3.76
      });

      setRecentActivities([
        {
          id: 1,
          type: 'collaboration',
          title: 'Summer Fashion Campaign',
          amount: 5000,
          status: 'completed',
          date: '2024-01-15'
        },
        {
          id: 2,
          type: 'affiliate',
          title: 'Beauty Products Link',
          amount: 237.50,
          status: 'earning',
          date: '2024-01-14'
        },
        {
          id: 3,
          type: 'campaign',
          title: 'Tech Gadget Review',
          amount: 1500,
          status: 'in_progress',
          date: '2024-01-12'
        }
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch monetization data:', error);
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'earning': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg p-6 h-32"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Monetization Dashboard</h1>
          <p className="text-gray-600 mt-2">Track your earnings, collaborations, and affiliate performance</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Earnings</p>
                <p className="text-2xl font-semibold text-green-600">{formatCurrency(stats.totalEarnings)}</p>
              </div>
              <CurrencyDollarIcon className="h-12 w-12 text-green-500" />
            </div>
            <div className="mt-4 flex items-center">
              <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-sm text-green-600">+12.5% from last month</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Collaborations</p>
                <p className="text-2xl font-semibold text-blue-600">{stats.activeCollaborations}</p>
              </div>
              <BuildingOfficeIcon className="h-12 w-12 text-blue-500" />
            </div>
            <div className="mt-4">
              <span className="text-sm text-gray-600">{stats.pendingCollaborations} pending approval</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Affiliate Links</p>
                <p className="text-2xl font-semibold text-purple-600">{stats.activeAffiliateLinks}</p>
              </div>
              <LinkIcon className="h-12 w-12 text-purple-500" />
            </div>
            <div className="mt-4">
              <span className="text-sm text-gray-600">{stats.totalClicks.toLocaleString()} total clicks</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Conversion Rate</p>
                <p className="text-2xl font-semibold text-orange-600">{stats.conversionRate}%</p>
              </div>
              <ChartBarIcon className="h-12 w-12 text-orange-500" />
            </div>
            <div className="mt-4">
              <span className="text-sm text-gray-600">{stats.totalConversions} conversions</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activities */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Recent Activities</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        {activity.type === 'collaboration' && <BuildingOfficeIcon className="h-8 w-8 text-blue-500" />}
                        {activity.type === 'affiliate' && <LinkIcon className="h-8 w-8 text-purple-500" />}
                        {activity.type === 'campaign' && <CalendarIcon className="h-8 w-8 text-green-500" />}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                        <p className="text-sm text-gray-600">{activity.date}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      {activity.amount && (
                        <p className="text-sm font-semibold text-gray-900">{formatCurrency(activity.amount)}</p>
                      )}
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(activity.status)}`}>
                        {activity.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
            </div>
            <div className="p-6 space-y-4">
              <button className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                Browse Brand Campaigns
              </button>
              <button className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors">
                Create Affiliate Link
              </button>
              <button className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors">
                View Analytics Report
              </button>
              <button className="w-full border border-gray-300 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors">
                Manage Brand Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}