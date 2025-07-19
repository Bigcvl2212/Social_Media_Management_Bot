/**
 * Dashboard Screen for Social Media Management Bot
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useTranslation } from 'react-i18next';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../contexts/ThemeContext';
import { DashboardData } from '../../types';
import apiClient, { API_ENDPOINTS } from '../../services/api';

export default function DashboardScreen() {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const { user, logout } = useAuth();
  const navigation = useNavigation();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [_isLoading, setIsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get(API_ENDPOINTS.DASHBOARD_DATA);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // For now, set mock data
      setDashboardData({
        total_followers: 0,
        total_posts: 0,
        avg_engagement_rate: 0,
        platforms_count: 0,
        recent_posts: [],
        analytics_summary: [],
      });
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleLogout = () => {
    Alert.alert(
      t('auth.logout'),
      t('settings.logoutConfirm'),
      [
        { text: t('common.cancel'), style: 'cancel' },
        { text: t('auth.logout'), onPress: logout, style: 'destructive' },
      ]
    );
  };

  const navigateToSettings = () => {
    navigation.navigate('Settings' as never);
  };

  const quickActions = [
    {
      id: 'create',
      title: t('dashboard.createPost'),
      subtitle: t('dashboard.shareNewContent'),
      icon: 'add-circle',
      color: theme.colors.primary,
      onPress: () => navigation.navigate('Create' as never),
    },
    {
      id: 'connect',
      title: t('dashboard.connectAccount'),
      subtitle: t('dashboard.linkSocialPlatforms'),
      icon: 'link',
      color: theme.colors.success,
      onPress: () => navigation.navigate('SocialAccounts' as never),
    },
    {
      id: 'analytics',
      title: t('dashboard.viewAnalytics'),
      subtitle: t('dashboard.checkPerformance'),
      icon: 'analytics',
      color: theme.colors.info,
      onPress: () => navigation.navigate('Analytics' as never),
    },
    {
      id: 'schedule',
      title: t('dashboard.schedulePosts'),
      subtitle: t('dashboard.planYourContent'),
      icon: 'schedule',
      color: theme.colors.warning,
      onPress: () => navigation.navigate('Calendar' as never),
    },
  ];

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={[styles.header, { backgroundColor: theme.colors.surface, borderBottomColor: theme.colors.border }]}>
        <View>
          <Text style={[styles.welcomeText, { color: theme.colors.textSecondary }]}>
            {t('dashboard.welcomeBack')}
          </Text>
          <Text style={[styles.userName, { color: theme.colors.text }]}>
            {user?.full_name || user?.username}
          </Text>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.settingsButton} onPress={navigateToSettings}>
            <Icon name="settings" size={24} color={theme.colors.textSecondary} />
          </TouchableOpacity>
          <TouchableOpacity style={[styles.logoutButton, { backgroundColor: theme.colors.error }]} onPress={handleLogout}>
            <Text style={[styles.logoutButtonText, { color: theme.colors.surface }]}>
              {t('auth.logout')}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statsRow}>
          <View style={[styles.statCard, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
              {dashboardData?.total_followers.toLocaleString() || '0'}
            </Text>
            <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
              {t('dashboard.totalFollowers')}
            </Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
              {dashboardData?.total_posts || '0'}
            </Text>
            <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
              {t('dashboard.totalPosts')}
            </Text>
          </View>
        </View>

        <View style={styles.statsRow}>
          <View style={[styles.statCard, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
              {dashboardData?.avg_engagement_rate.toFixed(1) || '0.0'}%
            </Text>
            <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
              {t('dashboard.avgEngagement')}
            </Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: theme.colors.surface }]}>
            <Text style={[styles.statNumber, { color: theme.colors.primary }]}>
              {dashboardData?.platforms_count || '0'}
            </Text>
            <Text style={[styles.statLabel, { color: theme.colors.textSecondary }]}>
              {t('dashboard.connectedPlatforms')}
            </Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          {t('dashboard.quickActions')}
        </Text>
        <View style={styles.actionsContainer}>
          {quickActions.map((action) => (
            <TouchableOpacity
              key={action.id}
              style={[styles.actionCard, { backgroundColor: theme.colors.surface }]}
              onPress={action.onPress}
            >
              <Icon name={action.icon} size={24} color={action.color} style={styles.actionIcon} />
              <Text style={[styles.actionTitle, { color: theme.colors.text }]}>
                {action.title}
              </Text>
              <Text style={[styles.actionSubtitle, { color: theme.colors.textSecondary }]}>
                {action.subtitle}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Posts */}
      <View style={styles.section}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          {t('dashboard.recentPosts')}
        </Text>
        {dashboardData?.recent_posts.length === 0 ? (
          <View style={[styles.emptyState, { backgroundColor: theme.colors.surface }]}>
            <Icon name="post-add" size={48} color={theme.colors.textSecondary} />
            <Text style={[styles.emptyStateText, { color: theme.colors.text }]}>
              {t('dashboard.noPosts')}
            </Text>
            <Text style={[styles.emptyStateSubtext, { color: theme.colors.textSecondary }]}>
              {t('dashboard.createFirstPost')}
            </Text>
          </View>
        ) : (
          <View>
            {dashboardData?.recent_posts.map((post) => (
              <View key={post.id} style={[styles.postCard, { backgroundColor: theme.colors.surface }]}>
                <Text style={[styles.postTitle, { color: theme.colors.text }]}>
                  {post.title}
                </Text>
                <Text style={[styles.postCaption, { color: theme.colors.textSecondary }]} numberOfLines={2}>
                  {post.caption}
                </Text>
                <Text style={[styles.postStatus, { color: theme.colors.primary }]}>
                  Status: {post.status}
                </Text>
              </View>
            ))}
          </View>
        )}
      </View>
    </ScrollView>
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
    padding: 24,
    borderBottomWidth: 1,
  },
  welcomeText: {
    fontSize: 16,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  settingsButton: {
    padding: 8,
  },
  logoutButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  logoutButtonText: {
    fontWeight: '600',
  },
  statsContainer: {
    padding: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    padding: 20,
    borderRadius: 12,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    textAlign: 'center',
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  actionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionCard: {
    width: '48%',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  actionIcon: {
    marginBottom: 8,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  actionSubtitle: {
    fontSize: 14,
  },
  emptyState: {
    padding: 32,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  emptyStateText: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateSubtext: {
    fontSize: 14,
    textAlign: 'center',
  },
  postCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  postTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  postCaption: {
    fontSize: 14,
    marginBottom: 8,
  },
  postStatus: {
    fontSize: 12,
    fontWeight: '500',
  },
});