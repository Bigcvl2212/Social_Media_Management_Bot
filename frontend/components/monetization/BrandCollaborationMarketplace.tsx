/**
 * Brand Collaboration Marketplace Component
 * 
 * Allows influencers to discover and apply to brand collaboration opportunities
 * and brands to post campaigns and find influencers
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  HandshakeIcon,
  BuildingOfficeIcon,
  CheckBadgeIcon
} from '@heroicons/react/24/outline';

interface Campaign {
  id: number;
  name: string;
  description: string;
  brandName: string;
  brandLogo?: string;
  isVerified: boolean;
  campaignType: string;
  budget: number;
  platforms: string[];
  industry: string;
  applicationDeadline: string;
  startDate: string;
  endDate: string;
  requirements: string[];
  targetAudience: {
    ageRange: string;
    location: string;
    interests: string[];
  };
}

interface FilterOptions {
  industry: string[];
  platforms: string[];
  budgetRange: [number, number];
  campaignType: string[];
}

export default function BrandCollaborationMarketplace() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [filteredCampaigns, setFilteredCampaigns] = useState<Campaign[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    industry: [],
    platforms: [],
    budgetRange: [0, 100000],
    campaignType: []
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  useEffect(() => {
    filterCampaigns();
  }, [searchTerm, filters, campaigns]);

  const fetchCampaigns = async () => {
    try {
      // Mock data - replace with actual API call
      const mockCampaigns: Campaign[] = [
        {
          id: 1,
          name: "Summer Fashion Collection Launch",
          description: "Promote our new summer collection with authentic lifestyle content showcasing versatile pieces for young professionals.",
          brandName: "StyleCo Fashion",
          isVerified: true,
          campaignType: "sponsored_post",
          budget: 15000,
          platforms: ["instagram", "tiktok"],
          industry: "fashion",
          applicationDeadline: "2024-02-15",
          startDate: "2024-03-01",
          endDate: "2024-03-31",
          requirements: [
            "Minimum 10K followers on Instagram",
            "Fashion/lifestyle content focus",
            "High engagement rate (>3%)",
            "Based in US or Canada"
          ],
          targetAudience: {
            ageRange: "22-35",
            location: "North America",
            interests: ["fashion", "lifestyle", "shopping"]
          }
        },
        {
          id: 2,
          name: "Tech Gadget Review Series",
          description: "Create honest reviews and unboxing videos for our latest smartphone accessories and tech gadgets.",
          brandName: "TechNova",
          isVerified: true,
          campaignType: "product_review",
          budget: 25000,
          platforms: ["youtube", "instagram", "tiktok"],
          industry: "technology",
          applicationDeadline: "2024-02-20",
          startDate: "2024-03-05",
          endDate: "2024-04-15",
          requirements: [
            "Tech content creator",
            "Minimum 25K subscribers on YouTube",
            "Professional video quality",
            "Previous tech review experience"
          ],
          targetAudience: {
            ageRange: "18-45",
            location: "Global",
            interests: ["technology", "gadgets", "innovation"]
          }
        },
        {
          id: 3,
          name: "Sustainable Beauty Campaign",
          description: "Showcase eco-friendly beauty products and sustainable beauty routines to environmentally conscious audiences.",
          brandName: "Green Beauty Co",
          isVerified: false,
          campaignType: "brand_ambassador",
          budget: 8000,
          platforms: ["instagram", "youtube"],
          industry: "beauty",
          applicationDeadline: "2024-02-10",
          startDate: "2024-02-25",
          endDate: "2024-05-25",
          requirements: [
            "Beauty/skincare content creator",
            "Passion for sustainability",
            "Minimum 5K followers",
            "Authentic engagement"
          ],
          targetAudience: {
            ageRange: "25-40",
            location: "US, UK, Australia",
            interests: ["beauty", "sustainability", "wellness"]
          }
        }
      ];

      setCampaigns(mockCampaigns);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch campaigns:', error);
      setLoading(false);
    }
  };

  const filterCampaigns = () => {
    let filtered = campaigns;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(campaign =>
        campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        campaign.brandName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        campaign.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Industry filter
    if (filters.industry.length > 0) {
      filtered = filtered.filter(campaign =>
        filters.industry.includes(campaign.industry)
      );
    }

    // Platform filter
    if (filters.platforms.length > 0) {
      filtered = filtered.filter(campaign =>
        filters.platforms.some(platform => campaign.platforms.includes(platform))
      );
    }

    // Budget filter
    filtered = filtered.filter(campaign =>
      campaign.budget >= filters.budgetRange[0] && campaign.budget <= filters.budgetRange[1]
    );

    // Campaign type filter
    if (filters.campaignType.length > 0) {
      filtered = filtered.filter(campaign =>
        filters.campaignType.includes(campaign.campaignType)
      );
    }

    setFilteredCampaigns(filtered);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getPlatformIcon = (platform: string) => {
    // In a real app, you'd use actual platform icons
    const icons: { [key: string]: string } = {
      instagram: '📸',
      tiktok: '🎵',
      youtube: '📺',
      twitter: '🐦',
      linkedin: '💼'
    };
    return icons[platform] || '📱';
  };

  const handleApplyToCampaign = (campaignId: number) => {
    // Handle application logic
    alert(`Applied to campaign ${campaignId}! You'll receive a confirmation email shortly.`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="animate-pulse max-w-7xl mx-auto">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
          <div className="space-y-6">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg p-6 h-64"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Brand Collaboration Marketplace</h1>
          <p className="text-gray-600 mt-2">Discover exciting brand partnership opportunities</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search campaigns, brands, or keywords..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filters
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                    <option value="">All Industries</option>
                    <option value="fashion">Fashion</option>
                    <option value="beauty">Beauty</option>
                    <option value="technology">Technology</option>
                    <option value="fitness">Fitness</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Platform</label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                    <option value="">All Platforms</option>
                    <option value="instagram">Instagram</option>
                    <option value="tiktok">TikTok</option>
                    <option value="youtube">YouTube</option>
                    <option value="twitter">Twitter</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Budget Range</label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                    <option value="">Any Budget</option>
                    <option value="0-5000">$0 - $5,000</option>
                    <option value="5000-15000">$5,000 - $15,000</option>
                    <option value="15000-50000">$15,000 - $50,000</option>
                    <option value="50000+">$50,000+</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Type</label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                    <option value="">All Types</option>
                    <option value="sponsored_post">Sponsored Post</option>
                    <option value="product_review">Product Review</option>
                    <option value="brand_ambassador">Brand Ambassador</option>
                    <option value="giveaway">Giveaway</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {filteredCampaigns.length} of {campaigns.length} campaigns
          </p>
        </div>

        {/* Campaign Cards */}
        <div className="space-y-6">
          {filteredCampaigns.map((campaign) => (
            <div key={campaign.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex flex-col lg:flex-row gap-6">
                <div className="flex-1">
                  {/* Campaign Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-xl font-semibold text-gray-900">{campaign.name}</h2>
                        {campaign.isVerified && (
                          <CheckBadgeIcon className="h-6 w-6 text-blue-500" title="Verified Brand" />
                        )}
                      </div>
                      <div className="flex items-center text-gray-600 mb-2">
                        <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                        <span className="text-sm">{campaign.brandName}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-green-600">{formatCurrency(campaign.budget)}</p>
                      <p className="text-sm text-gray-600">Total Budget</p>
                    </div>
                  </div>

                  {/* Campaign Description */}
                  <p className="text-gray-700 mb-4 line-clamp-2">{campaign.description}</p>

                  {/* Campaign Details */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <div className="flex items-center text-sm text-gray-600 mb-1">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        Campaign Period
                      </div>
                      <p className="text-sm font-medium">
                        {formatDate(campaign.startDate)} - {formatDate(campaign.endDate)}
                      </p>
                    </div>
                    <div>
                      <div className="flex items-center text-sm text-gray-600 mb-1">
                        <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                        Application Deadline
                      </div>
                      <p className="text-sm font-medium">{formatDate(campaign.applicationDeadline)}</p>
                    </div>
                    <div>
                      <div className="flex items-center text-sm text-gray-600 mb-1">
                        <HandshakeIcon className="h-4 w-4 mr-1" />
                        Campaign Type
                      </div>
                      <p className="text-sm font-medium capitalize">
                        {campaign.campaignType.replace('_', ' ')}
                      </p>
                    </div>
                  </div>

                  {/* Platforms */}
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">Platforms:</p>
                    <div className="flex gap-2">
                      {campaign.platforms.map((platform) => (
                        <span
                          key={platform}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                        >
                          <span className="mr-1">{getPlatformIcon(platform)}</span>
                          {platform.charAt(0).toUpperCase() + platform.slice(1)}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Requirements */}
                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2">Requirements:</p>
                    <ul className="text-sm text-gray-700 space-y-1">
                      {campaign.requirements.slice(0, 2).map((req, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-blue-500 mr-2">•</span>
                          {req}
                        </li>
                      ))}
                      {campaign.requirements.length > 2 && (
                        <li className="text-blue-600 cursor-pointer hover:underline">
                          <EyeIcon className="h-4 w-4 inline mr-1" />
                          View all {campaign.requirements.length} requirements
                        </li>
                      )}
                    </ul>
                  </div>
                </div>

                {/* Action Panel */}
                <div className="lg:w-64 border-l border-gray-200 lg:pl-6">
                  <div className="space-y-4">
                    <button
                      onClick={() => handleApplyToCampaign(campaign.id)}
                      className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                      Apply Now
                    </button>
                    <button className="w-full border border-gray-300 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors">
                      View Details
                    </button>
                    <button className="w-full border border-gray-300 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors">
                      Save for Later
                    </button>
                  </div>

                  {/* Target Audience */}
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Target Audience</h4>
                    <div className="space-y-2 text-sm text-gray-600">
                      <p><strong>Age:</strong> {campaign.targetAudience.ageRange}</p>
                      <p><strong>Location:</strong> {campaign.targetAudience.location}</p>
                      <p><strong>Interests:</strong> {campaign.targetAudience.interests.join(', ')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredCampaigns.length === 0 && !loading && (
          <div className="text-center py-12">
            <HandshakeIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search criteria or filters</p>
            <button
              onClick={() => {
                setSearchTerm('');
                setFilters({
                  industry: [],
                  platforms: [],
                  budgetRange: [0, 100000],
                  campaignType: []
                });
              }}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}