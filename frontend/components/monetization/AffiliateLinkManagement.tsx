/**
 * Affiliate Link Management Component
 * 
 * Allows users to create, manage, and track affiliate links with detailed analytics
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  PlusIcon,
  LinkIcon,
  EyeIcon,
  ChartBarIcon,
  ClipboardDocumentIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

interface AffiliateLink {
  id: number;
  name: string;
  originalUrl: string;
  affiliateCode: string;
  shortUrl: string;
  productName?: string;
  commissionRate: number;
  clickCount: number;
  conversionCount: number;
  totalEarnings: number;
  isActive: boolean;
  createdAt: string;
  lastClicked?: string;
}

interface NewLinkForm {
  name: string;
  originalUrl: string;
  productName: string;
  commissionRate: number;
}

export default function AffiliateLinkManagement() {
  const [links, setLinks] = useState<AffiliateLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newLink, setNewLink] = useState<NewLinkForm>({
    name: '',
    originalUrl: '',
    productName: '',
    commissionRate: 10
  });

  useEffect(() => {
    fetchAffiliateLinks();
  }, []);

  const fetchAffiliateLinks = async () => {
    try {
      // Mock data - replace with actual API call
      const mockLinks: AffiliateLink[] = [
        {
          id: 1,
          name: "Summer Fashion Collection",
          originalUrl: "https://fashionbrand.com/summer-collection",
          affiliateCode: "SUMMER123",
          shortUrl: "https://short.ly/SUMMER123",
          productName: "Summer Dress Collection",
          commissionRate: 15,
          clickCount: 342,
          conversionCount: 28,
          totalEarnings: 1260.50,
          isActive: true,
          createdAt: "2024-01-10",
          lastClicked: "2024-01-20"
        },
        {
          id: 2,
          name: "Tech Gadget Store",
          originalUrl: "https://techstore.com/gadgets",
          affiliateCode: "TECH456",
          shortUrl: "https://short.ly/TECH456",
          productName: "Wireless Earbuds",
          commissionRate: 8,
          clickCount: 189,
          conversionCount: 12,
          totalEarnings: 432.80,
          isActive: true,
          createdAt: "2024-01-15",
          lastClicked: "2024-01-19"
        },
        {
          id: 3,
          name: "Beauty Essentials",
          originalUrl: "https://beautyco.com/essentials",
          affiliateCode: "BEAUTY789",
          shortUrl: "https://short.ly/BEAUTY789",
          productName: "Skincare Bundle",
          commissionRate: 12,
          clickCount: 156,
          conversionCount: 8,
          totalEarnings: 289.60,
          isActive: false,
          createdAt: "2024-01-05",
          lastClicked: "2024-01-18"
        }
      ];

      setLinks(mockLinks);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch affiliate links:', error);
      setLoading(false);
    }
  };

  const handleCreateLink = async () => {
    try {
      // Generate a random affiliate code for demo
      const affiliateCode = Math.random().toString(36).substring(2, 10).toUpperCase();
      
      const newAffiliateLink: AffiliateLink = {
        id: Date.now(),
        ...newLink,
        affiliateCode,
        shortUrl: `https://short.ly/${affiliateCode}`,
        clickCount: 0,
        conversionCount: 0,
        totalEarnings: 0,
        isActive: true,
        createdAt: new Date().toISOString().split('T')[0]
      };

      setLinks([newAffiliateLink, ...links]);
      setShowCreateForm(false);
      setNewLink({
        name: '',
        originalUrl: '',
        productName: '',
        commissionRate: 10
      });
    } catch (error) {
      console.error('Failed to create affiliate link:', error);
    }
  };

  const handleCopyLink = (shortUrl: string) => {
    navigator.clipboard.writeText(shortUrl);
    alert('Link copied to clipboard!');
  };

  const handleToggleActive = (id: number) => {
    setLinks(links.map(link => 
      link.id === id ? { ...link, isActive: !link.isActive } : link
    ));
  };

  const handleDeleteLink = (id: number) => {
    if (confirm('Are you sure you want to delete this affiliate link?')) {
      setLinks(links.filter(link => link.id !== id));
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const calculateConversionRate = (conversions: number, clicks: number) => {
    return clicks > 0 ? ((conversions / clicks) * 100).toFixed(2) : '0.00';
  };

  const totalStats = {
    totalEarnings: links.reduce((sum, link) => sum + link.totalEarnings, 0),
    totalClicks: links.reduce((sum, link) => sum + link.clickCount, 0),
    totalConversions: links.reduce((sum, link) => sum + link.conversionCount, 0),
    activeLinks: links.filter(link => link.isActive).length
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="animate-pulse max-w-7xl mx-auto">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg p-6 h-24"></div>
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
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Affiliate Link Management</h1>
            <p className="text-gray-600 mt-2">Create and track your affiliate marketing links</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create New Link
          </button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Earnings</p>
                <p className="text-2xl font-semibold text-green-600">{formatCurrency(totalStats.totalEarnings)}</p>
              </div>
              <ChartBarIcon className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Clicks</p>
                <p className="text-2xl font-semibold text-blue-600">{totalStats.totalClicks.toLocaleString()}</p>
              </div>
              <EyeIcon className="h-12 w-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Conversions</p>
                <p className="text-2xl font-semibold text-purple-600">{totalStats.totalConversions}</p>
              </div>
              <ChartBarIcon className="h-12 w-12 text-purple-500" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Links</p>
                <p className="text-2xl font-semibold text-orange-600">{totalStats.activeLinks}</p>
              </div>
              <LinkIcon className="h-12 w-12 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Create Link Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-semibold mb-4">Create New Affiliate Link</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Link Name</label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Summer Fashion Collection"
                    value={newLink.name}
                    onChange={(e) => setNewLink({...newLink, name: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Original URL</label>
                  <input
                    type="url"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="https://example.com/product"
                    value={newLink.originalUrl}
                    onChange={(e) => setNewLink({...newLink, originalUrl: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
                  <input
                    type="text"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Wireless Earbuds"
                    value={newLink.productName}
                    onChange={(e) => setNewLink({...newLink, productName: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Commission Rate (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="0.1"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={newLink.commissionRate}
                    onChange={(e) => setNewLink({...newLink, commissionRate: parseFloat(e.target.value)})}
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateLink}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  disabled={!newLink.name || !newLink.originalUrl}
                >
                  Create Link
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Affiliate Links Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Your Affiliate Links</h2>
          </div>
          
          {links.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Link Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Performance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Earnings
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {links.map((link) => (
                    <tr key={link.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{link.name}</div>
                          <div className="text-sm text-gray-500">{link.productName}</div>
                          <div className="text-xs text-gray-400 mt-1">
                            Code: {link.affiliateCode} • Created: {formatDate(link.createdAt)}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          <div>Clicks: <span className="font-medium">{link.clickCount.toLocaleString()}</span></div>
                          <div>Conversions: <span className="font-medium">{link.conversionCount}</span></div>
                          <div>Rate: <span className="font-medium">{calculateConversionRate(link.conversionCount, link.clickCount)}%</span></div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-green-600">{formatCurrency(link.totalEarnings)}</div>
                        <div className="text-xs text-gray-500">{link.commissionRate}% commission</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          link.isActive 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {link.isActive ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleCopyLink(link.shortUrl)}
                            className="text-blue-600 hover:text-blue-900"
                            title="Copy Link"
                          >
                            <ClipboardDocumentIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleToggleActive(link.id)}
                            className="text-yellow-600 hover:text-yellow-900"
                            title={link.isActive ? 'Deactivate' : 'Activate'}
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteLink(link.id)}
                            className="text-red-600 hover:text-red-900"
                            title="Delete Link"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <LinkIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No affiliate links yet</h3>
              <p className="text-gray-600 mb-4">Start earning by creating your first affiliate link</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Your First Link
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}