'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  HashtagIcon,
  MusicalNoteIcon,
  FireIcon,
  ArrowTrendingUpIcon,
  BellIcon,
  ClockIcon,
  EyeIcon,
  PlusIcon
} from '@heroicons/react/24/outline';
import { curationAPI } from '@/lib/curation-api';

interface TrendingData {
  platform: string;
  hashtags: Array<{
    tag: string;
    volume: number;
    growth: string;
    momentum: string;
    engagement_rate: number;
  }>;
  sounds?: Array<{
    name: string;
    artist: string;
    usage: number;
    growth: string;
  }>;
  viral_spikes: Array<{
    content_id: string;
    title: string;
    creator: string;
    current_engagement: number;
    spike_multiplier: number;
  }>;
}

export default function TrendDiscoveryPage() {
  const [selectedPlatforms, setSelectedPlatforms] = useState(['tiktok', 'instagram']);
  const [trendingData, setTrendingData] = useState<Record<string, TrendingData>>({});
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const platforms = [
    { id: 'tiktok', name: 'TikTok', color: 'bg-black' },
    { id: 'instagram', name: 'Instagram', color: 'bg-pink-500' },
    { id: 'youtube', name: 'YouTube', color: 'bg-red-500' },
    { id: 'twitter', name: 'Twitter', color: 'bg-blue-500' },
    { id: 'linkedin', name: 'LinkedIn', color: 'bg-blue-700' }
  ];

  const loadTrendingData = useCallback(async () => {
    setLoading(true);
    
    try {
      const data: Record<string, TrendingData> = {};
      
      // Load hashtags for all platforms
      const hashtagPromises = selectedPlatforms.map(async (platform) => {
        try {
          const hashtagData = await curationAPI.getRealtimeHashtags([platform]);
          const viralSpikes = await curationAPI.getViralSpikes(platform);
          
          data[platform] = {
            platform,
            hashtags: hashtagData.map(trend => ({
              tag: trend.hashtag,
              volume: trend.volume,
              growth: trend.growth_rate,
              momentum: trend.growth_rate.includes('+') ? 'rising' : 'declining',
              engagement_rate: trend.engagement_rate || 0
            })),
            viral_spikes: viralSpikes.map(spike => ({
              content_id: spike.content_id,
              title: spike.content_type,
              creator: 'Unknown',
              current_engagement: spike.current_engagement,
              spike_multiplier: parseFloat(spike.growth_rate.replace('%', '')) / 100
            }))
          };
          
          // Load sounds for TikTok and Instagram
          if (platform === 'tiktok' || platform === 'instagram') {
            const soundData = await curationAPI.getRealtimeSounds([platform]);
            data[platform].sounds = soundData.map(sound => ({
              name: sound.title,
              artist: sound.artist || 'Unknown',
              usage: sound.usage_count,
              growth: sound.growth_rate
            }));
          }
        } catch (error) {
          console.error(`Error loading data for ${platform}:`, error);
          data[platform] = {
            platform,
            hashtags: [],
            viral_spikes: []
          };
        }
      });
      
      await Promise.all(hashtagPromises);
      setTrendingData(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error loading trending data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedPlatforms]);

  useEffect(() => {
    loadTrendingData();
    
    // Set up auto-refresh every 5 minutes
    refreshIntervalRef.current = setInterval(loadTrendingData, 5 * 60 * 1000);
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
    };
  }, [loadTrendingData]);

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getMomentumIcon = (momentum: string) => {
    switch (momentum) {
      case 'rising':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
      case 'declining':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-red-500 transform rotate-180" />;
      default:
        return <ArrowTrendingUpIcon className="h-4 w-4 text-yellow-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Trend Discovery</h1>
              <p className="mt-2 text-gray-600">Real-time monitoring of trending topics, hashtags, and sounds</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={loadTrendingData}
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                <ClockIcon className="h-5 w-5 mr-2" />
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                <BellIcon className="h-5 w-5 mr-2" />
                Set Alert
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Selector */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Select Platforms to Monitor</h3>
          <div className="flex flex-wrap gap-3">
            {platforms.map((platform) => (
              <button
                key={platform.id}
                onClick={() => handlePlatformToggle(platform.id)}
                className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  selectedPlatforms.includes(platform.id)
                    ? `${platform.color} text-white`
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {platform.name}
              </button>
            ))}
          </div>
          {lastUpdate && (
            <p className="mt-4 text-sm text-gray-500">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>

      {/* Trending Content Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {selectedPlatforms.map((platformId) => {
            const platform = platforms.find(p => p.id === platformId);
            const data = trendingData[platformId];
            
            if (!platform || !data) return null;

            return (
              <div key={platformId} className="space-y-6">
                {/* Platform Header */}
                <div className="bg-white rounded-lg shadow">
                  <div className={`${platform.color} rounded-t-lg px-6 py-4`}>
                    <h2 className="text-xl font-bold text-white">{platform.name} Trends</h2>
                  </div>
                  
                  {/* Trending Hashtags */}
                  <div className="p-6">
                    <div className="flex items-center mb-4">
                      <HashtagIcon className="h-5 w-5 mr-2 text-gray-600" />
                      <h3 className="text-lg font-medium text-gray-900">Trending Hashtags</h3>
                    </div>
                    
                    {data.hashtags.length === 0 ? (
                      <p className="text-gray-500 text-sm">No hashtag data available</p>
                    ) : (
                      <div className="space-y-3">
                        {data.hashtags.slice(0, 5).map((hashtag, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center">
                              {getMomentumIcon(hashtag.momentum)}
                              <span className="ml-2 font-medium text-gray-900">{hashtag.tag}</span>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900">{formatNumber(hashtag.volume)}</p>
                              <p className="text-xs text-green-600">{hashtag.growth}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Trending Sounds (for TikTok and Instagram) */}
                  {data.sounds && (
                    <div className="px-6 pb-6">
                      <div className="flex items-center mb-4">
                        <MusicalNoteIcon className="h-5 w-5 mr-2 text-gray-600" />
                        <h3 className="text-lg font-medium text-gray-900">Trending Sounds</h3>
                      </div>
                      
                      {data.sounds.length === 0 ? (
                        <p className="text-gray-500 text-sm">No sound data available</p>
                      ) : (
                        <div className="space-y-3">
                          {data.sounds.slice(0, 3).map((sound, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                              <div>
                                <p className="font-medium text-gray-900">{sound.name}</p>
                                <p className="text-sm text-gray-600">by {sound.artist}</p>
                              </div>
                              <div className="text-right">
                                <p className="text-sm font-medium text-gray-900">{formatNumber(sound.usage)}</p>
                                <p className="text-xs text-green-600">{sound.growth}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Viral Spikes */}
                  <div className="px-6 pb-6">
                    <div className="flex items-center mb-4">
                      <FireIcon className="h-5 w-5 mr-2 text-gray-600" />
                      <h3 className="text-lg font-medium text-gray-900">Viral Content Spikes</h3>
                    </div>
                    
                    {data.viral_spikes.length === 0 ? (
                      <p className="text-gray-500 text-sm">No viral spikes detected</p>
                    ) : (
                      <div className="space-y-3">
                        {data.viral_spikes.slice(0, 3).map((spike, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                            <div>
                              <p className="font-medium text-gray-900">{spike.title}</p>
                              <p className="text-sm text-gray-600">by {spike.creator}</p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900">
                                {(spike.current_engagement * 100).toFixed(1)}% engagement
                              </p>
                              <p className="text-xs text-red-600">
                                {spike.spike_multiplier.toFixed(1)}x spike
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <PlusIcon className="h-5 w-5 mr-2 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Create Trend Watch</span>
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <BellIcon className="h-5 w-5 mr-2 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Set Smart Alert</span>
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <EyeIcon className="h-5 w-5 mr-2 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">View All Alerts</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}