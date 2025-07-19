/**
 * Analytics Screen for Social Media Management Bot
 * Enhanced with real-time metrics, charts, and comprehensive analytics
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  RefreshControl,
  Modal,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../../contexts/ThemeContext';
import { useQuery } from '@tanstack/react-query';

const { width } = Dimensions.get('window');

interface AnalyticsData {
  totalReach: number;
  totalEngagement: number;
  engagementRate: number;
  followerGrowth: number;
  topPosts: Array<{
    id: string;
    title: string;
    engagement: number;
    platform: string;
  }>;
  platformStats: Array<{
    platform: string;
    followers: number;
    engagement: number;
    posts: number;
    color: string;
  }>;
  weeklyData: Array<{
    day: string;
    reach: number;
    engagement: number;
  }>;
}

const TIME_PERIODS = [
  { id: '7d', label: '7 Days' },
  { id: '30d', label: '30 Days' },
  { id: '90d', label: '3 Months' },
  { id: '1y', label: '1 Year' },
];

export default function AnalyticsScreen() {
  const { theme } = useTheme();
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [showPeriodModal, setShowPeriodModal] = useState(false);

  const { data: analyticsData, isLoading, refetch } = useQuery({
    queryKey: ['analytics', selectedPeriod],
    queryFn: async (): Promise<AnalyticsData> => {
      // Mock data for demonstration - in real app, this would call API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        totalReach: 125430,
        totalEngagement: 8640,
        engagementRate: 6.9,
        followerGrowth: 12.5,
        topPosts: [
          { id: '1', title: 'Summer vibes are here! 🌞', engagement: 1250, platform: 'Instagram' },
          { id: '2', title: 'Product launch announcement', engagement: 980, platform: 'LinkedIn' },
          { id: '3', title: 'Behind the scenes video', engagement: 850, platform: 'TikTok' },
        ],
        platformStats: [
          { platform: 'Instagram', followers: 15200, engagement: 3420, posts: 45, color: '#E4405F' },
          { platform: 'LinkedIn', followers: 8900, engagement: 2100, posts: 28, color: '#0A66C2' },
          { platform: 'TikTok', followers: 22100, engagement: 4200, posts: 38, color: '#000000' },
          { platform: 'Twitter', followers: 12600, engagement: 1800, posts: 52, color: '#1DA1F2' },
        ],
        weeklyData: [
          { day: 'Mon', reach: 18500, engagement: 1200 },
          { day: 'Tue', reach: 22300, engagement: 1450 },
          { day: 'Wed', reach: 19800, engagement: 1100 },
          { day: 'Thu', reach: 25600, engagement: 1680 },
          { day: 'Fri', reach: 21200, engagement: 1320 },
          { day: 'Sat', reach: 16900, engagement: 980 },
          { day: 'Sun', reach: 14200, engagement: 850 },
        ],
      };
    },
  });

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const renderOverviewCards = () => (
    <View style={styles.overviewContainer}>
      <View style={[styles.overviewCard, { backgroundColor: theme.colors.surface }]}>
        <Icon name="visibility" size={24} color={theme.colors.primary} />
        <Text style={[styles.overviewNumber, { color: theme.colors.text }]}>
          {formatNumber(analyticsData?.totalReach || 0)}
        </Text>
        <Text style={[styles.overviewLabel, { color: theme.colors.textSecondary }]}>
          Total Reach
        </Text>
      </View>

      <View style={[styles.overviewCard, { backgroundColor: theme.colors.surface }]}>
        <Icon name="favorite" size={24} color="#ef4444" />
        <Text style={[styles.overviewNumber, { color: theme.colors.text }]}>
          {formatNumber(analyticsData?.totalEngagement || 0)}
        </Text>
        <Text style={[styles.overviewLabel, { color: theme.colors.textSecondary }]}>
          Total Engagement
        </Text>
      </View>

      <View style={[styles.overviewCard, { backgroundColor: theme.colors.surface }]}>
        <Icon name="trending-up" size={24} color="#10b981" />
        <Text style={[styles.overviewNumber, { color: theme.colors.text }]}>
          {analyticsData?.engagementRate.toFixed(1) || 0}%
        </Text>
        <Text style={[styles.overviewLabel, { color: theme.colors.textSecondary }]}>
          Engagement Rate
        </Text>
      </View>

      <View style={[styles.overviewCard, { backgroundColor: theme.colors.surface }]}>
        <Icon name="group-add" size={24} color="#f59e0b" />
        <Text style={[styles.overviewNumber, { color: theme.colors.text }]}>
          +{analyticsData?.followerGrowth.toFixed(1) || 0}%
        </Text>
        <Text style={[styles.overviewLabel, { color: theme.colors.textSecondary }]}>
          Follower Growth
        </Text>
      </View>
    </View>
  );

  const renderPlatformStats = () => (
    <View style={[styles.section, { backgroundColor: theme.colors.surface }]}>
      <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
        Platform Performance
      </Text>
      {analyticsData?.platformStats.map((platform) => (
        <View key={platform.platform} style={styles.platformRow}>
          <View style={[styles.platformIndicator, { backgroundColor: platform.color }]} />
          <View style={styles.platformInfo}>
            <Text style={[styles.platformName, { color: theme.colors.text }]}>
              {platform.platform}
            </Text>
            <Text style={[styles.platformStats, { color: theme.colors.textSecondary }]}>
              {formatNumber(platform.followers)} followers • {formatNumber(platform.engagement)} engagement
            </Text>
          </View>
          <Text style={[styles.platformPosts, { color: theme.colors.textSecondary }]}>
            {platform.posts} posts
          </Text>
        </View>
      ))}
    </View>
  );

  const renderTopPosts = () => (
    <View style={[styles.section, { backgroundColor: theme.colors.surface }]}>
      <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
        Top Performing Posts
      </Text>
      {analyticsData?.topPosts.map((post, index) => (
        <View key={post.id} style={styles.topPostItem}>
          <View style={styles.topPostRank}>
            <Text style={[styles.rankNumber, { color: theme.colors.primary }]}>
              #{index + 1}
            </Text>
          </View>
          <View style={styles.topPostInfo}>
            <Text style={[styles.topPostTitle, { color: theme.colors.text }]} numberOfLines={1}>
              {post.title}
            </Text>
            <Text style={[styles.topPostMeta, { color: theme.colors.textSecondary }]}>
              {post.platform} • {formatNumber(post.engagement)} engagement
            </Text>
          </View>
          <Icon name="trending-up" size={20} color="#10b981" />
        </View>
      ))}
    </View>
  );

  const renderSimpleChart = () => (
    <View style={[styles.section, { backgroundColor: theme.colors.surface }]}>
      <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
        Weekly Performance
      </Text>
      <View style={styles.chartContainer}>
        {analyticsData?.weeklyData.map((day) => {
          const maxReach = Math.max(...(analyticsData?.weeklyData.map(d => d.reach) || [0]));
          const height = (day.reach / maxReach) * 100;
          
          return (
            <View key={day.day} style={styles.chartBar}>
              <View 
                style={[
                  styles.chartBarFill, 
                  { 
                    height: `${height}%`,
                    backgroundColor: theme.colors.primary,
                  }
                ]} 
              />
              <Text style={[styles.chartLabel, { color: theme.colors.textSecondary }]}>
                {day.day}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { backgroundColor: theme.colors.surface }]}>
        <Text style={[styles.title, { color: theme.colors.text }]}>Analytics</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity 
            style={[styles.periodButton, { borderColor: theme.colors.border }]}
            onPress={() => setShowPeriodModal(true)}
          >
            <Text style={[styles.periodButtonText, { color: theme.colors.text }]}>
              {TIME_PERIODS.find(p => p.id === selectedPeriod)?.label}
            </Text>
            <Icon name="keyboard-arrow-down" size={20} color={theme.colors.text} />
          </TouchableOpacity>
          <TouchableOpacity style={[styles.exportButton, { backgroundColor: theme.colors.primary }]}>
            <Icon name="file-download" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={refetch}
            colors={[theme.colors.primary]}
            tintColor={theme.colors.primary}
          />
        }
      >
        {renderOverviewCards()}
        {renderSimpleChart()}
        {renderPlatformStats()}
        {renderTopPosts()}
      </ScrollView>

      {/* Period Selection Modal */}
      <Modal
        visible={showPeriodModal}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setShowPeriodModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContainer, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              Select Time Period
            </Text>
            {TIME_PERIODS.map((period) => (
              <TouchableOpacity
                key={period.id}
                style={[
                  styles.periodOption,
                  selectedPeriod === period.id && { backgroundColor: theme.colors.primary + '20' },
                ]}
                onPress={() => {
                  setSelectedPeriod(period.id);
                  setShowPeriodModal(false);
                }}
              >
                <Text style={[
                  styles.periodOptionText, 
                  { color: selectedPeriod === period.id ? theme.colors.primary : theme.colors.text }
                ]}>
                  {period.label}
                </Text>
                {selectedPeriod === period.id && (
                  <Icon name="check" size={20} color={theme.colors.primary} />
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 0.5,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  periodButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderWidth: 1,
    borderRadius: 6,
    gap: 4,
  },
  periodButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  exportButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  overviewContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  overviewCard: {
    flex: 1,
    minWidth: (width - 44) / 2,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    gap: 8,
  },
  overviewNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  overviewLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  section: {
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  platformRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 0.5,
    borderBottomColor: '#f3f4f6',
  },
  platformIndicator: {
    width: 4,
    height: 40,
    borderRadius: 2,
    marginRight: 12,
  },
  platformInfo: {
    flex: 1,
  },
  platformName: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 2,
  },
  platformStats: {
    fontSize: 12,
  },
  platformPosts: {
    fontSize: 12,
    fontWeight: '500',
  },
  topPostItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 0.5,
    borderBottomColor: '#f3f4f6',
  },
  topPostRank: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  rankNumber: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  topPostInfo: {
    flex: 1,
  },
  topPostTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 2,
  },
  topPostMeta: {
    fontSize: 12,
  },
  chartContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    height: 120,
    paddingHorizontal: 8,
  },
  chartBar: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'flex-end',
    height: '100%',
    marginHorizontal: 2,
  },
  chartBarFill: {
    width: '80%',
    borderRadius: 2,
    marginBottom: 8,
  },
  chartLabel: {
    fontSize: 12,
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    margin: 20,
    borderRadius: 12,
    padding: 20,
    minWidth: 250,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
    textAlign: 'center',
  },
  periodOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginBottom: 4,
  },
  periodOptionText: {
    fontSize: 16,
  },
});
