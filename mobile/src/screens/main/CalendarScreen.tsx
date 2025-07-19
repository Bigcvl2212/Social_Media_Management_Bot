/**
 * Calendar Screen for Social Media Management Bot
 * Enhanced with content scheduling, calendar view, and post management
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  Alert,
  RefreshControl,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../../contexts/ThemeContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PlatformType } from '../../types';
import apiClient from '../../services/api';

const { width } = Dimensions.get('window');

interface ScheduledPost {
  id: string;
  title: string;
  content: string;
  platforms: PlatformType[];
  scheduledTime: string;
  status: 'scheduled' | 'published' | 'failed' | 'draft';
  mediaUrls?: string[];
  engagement?: {
    likes: number;
    shares: number;
    comments: number;
  };
}

interface CalendarDay {
  date: string;
  isCurrentMonth: boolean;
  isToday: boolean;
  posts: ScheduledPost[];
}

const PLATFORM_COLORS: Record<PlatformType, string> = {
  instagram: '#E4405F',
  facebook: '#1877F2',
  twitter: '#1DA1F2',
  linkedin: '#0A66C2',
  youtube: '#FF0000',
  tiktok: '#000000',
};

const STATUS_COLORS = {
  scheduled: '#3b82f6',
  published: '#10b981',
  failed: '#ef4444',
  draft: '#6b7280',
};

export default function CalendarScreen() {
  const { theme } = useTheme();
  const queryClient = useQueryClient();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [showPostModal, setShowPostModal] = useState(false);
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'list'>('month');

  const { data: scheduledPosts, isLoading, refetch } = useQuery({
    queryKey: ['scheduledPosts', currentDate.getFullYear(), currentDate.getMonth()],
    queryFn: async (): Promise<ScheduledPost[]> => {
      // Mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const posts: ScheduledPost[] = [
        {
          id: '1',
          title: 'Summer Campaign Launch',
          content: 'Exciting summer collection is here! 🌞 Check out our latest designs.',
          platforms: ['instagram', 'facebook'],
          scheduledTime: new Date(2025, currentDate.getMonth(), 15, 10, 0).toISOString(),
          status: 'scheduled',
          mediaUrls: ['https://via.placeholder.com/300'],
        },
        {
          id: '2',
          title: 'Product Tutorial Video',
          content: 'Learn how to use our latest product in this quick tutorial video.',
          platforms: ['youtube', 'tiktok'],
          scheduledTime: new Date(2025, currentDate.getMonth(), 18, 14, 30).toISOString(),
          status: 'published',
          engagement: { likes: 245, shares: 67, comments: 23 },
        },
        {
          id: '3',
          title: 'Weekly Team Update',
          content: 'This week our team achieved amazing milestones. Here\'s what we accomplished.',
          platforms: ['linkedin'],
          scheduledTime: new Date(2025, currentDate.getMonth(), 20, 9, 0).toISOString(),
          status: 'scheduled',
        },
        {
          id: '4',
          title: 'Flash Sale Announcement',
          content: 'FLASH SALE! 50% off selected items. Limited time only! 🔥',
          platforms: ['instagram', 'twitter', 'facebook'],
          scheduledTime: new Date(2025, currentDate.getMonth(), 22, 16, 0).toISOString(),
          status: 'draft',
        },
      ];
      
      return posts;
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (postId: string) => {
      await apiClient.delete(`/content/${postId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduledPosts'] });
      Alert.alert('Success', 'Post deleted successfully');
    },
    onError: () => {
      Alert.alert('Error', 'Failed to delete post');
    },
  });

  const generateCalendarDays = (): CalendarDay[] => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days: CalendarDay[] = [];
    const today = new Date();
    
    for (let i = 0; i < 42; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      const dateString = date.toISOString().split('T')[0];
      const dayPosts = scheduledPosts?.filter(post => 
        post.scheduledTime.split('T')[0] === dateString
      ) || [];
      
      days.push({
        date: dateString,
        isCurrentMonth: date.getMonth() === month,
        isToday: date.toDateString() === today.toDateString(),
        posts: dayPosts,
      });
    }
    
    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + (direction === 'next' ? 1 : -1));
    setCurrentDate(newDate);
  };

  const handleDeletePost = (postId: string) => {
    Alert.alert(
      'Delete Post',
      'Are you sure you want to delete this scheduled post?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => deleteMutation.mutate(postId)
        },
      ]
    );
  };

  const renderCalendarHeader = () => (
    <View style={[styles.calendarHeader, { backgroundColor: theme.colors.surface }]}>
      <TouchableOpacity onPress={() => navigateMonth('prev')}>
        <Icon name="chevron-left" size={24} color={theme.colors.text} />
      </TouchableOpacity>
      
      <Text style={[styles.monthTitle, { color: theme.colors.text }]}>
        {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
      </Text>
      
      <TouchableOpacity onPress={() => navigateMonth('next')}>
        <Icon name="chevron-right" size={24} color={theme.colors.text} />
      </TouchableOpacity>
    </View>
  );

  const renderCalendarDay = (day: CalendarDay) => (
    <TouchableOpacity
      key={day.date}
      style={[
        styles.calendarDay,
        { backgroundColor: theme.colors.surface },
        day.isToday && { backgroundColor: theme.colors.primary + '20' },
        !day.isCurrentMonth && styles.dimmedDay,
      ]}
      onPress={() => {
        setSelectedDate(day.date);
        if (day.posts.length > 0) {
          setShowPostModal(true);
        }
      }}
    >
      <Text style={[
        styles.dayNumber,
        { color: day.isToday ? theme.colors.primary : theme.colors.text },
        !day.isCurrentMonth && { color: theme.colors.textSecondary },
      ]}>
        {new Date(day.date).getDate()}
      </Text>
      
      {day.posts.length > 0 && (
        <View style={styles.postIndicators}>
          {day.posts.slice(0, 3).map((post) => (
            <View
              key={post.id}
              style={[
                styles.postDot,
                { backgroundColor: STATUS_COLORS[post.status] }
              ]}
            />
          ))}
          {day.posts.length > 3 && (
            <Text style={[styles.moreIndicator, { color: theme.colors.textSecondary }]}>
              +{day.posts.length - 3}
            </Text>
          )}
        </View>
      )}
    </TouchableOpacity>
  );

  const renderPostItem = (post: ScheduledPost) => (
    <View style={[styles.postItem, { backgroundColor: theme.colors.surface }]}>
      <View style={styles.postHeader}>
        <View style={styles.postInfo}>
          <Text style={[styles.postTitle, { color: theme.colors.text }]} numberOfLines={1}>
            {post.title}
          </Text>
          <Text style={[styles.postTime, { color: theme.colors.textSecondary }]}>
            {new Date(post.scheduledTime).toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Text>
        </View>
        
        <View style={styles.postActions}>
          <View style={[styles.statusBadge, { backgroundColor: STATUS_COLORS[post.status] + '20' }]}>
            <Text style={[styles.statusText, { color: STATUS_COLORS[post.status] }]}>
              {post.status}
            </Text>
          </View>
          
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={() => handleDeletePost(post.id)}
          >
            <Icon name="delete" size={16} color="#ef4444" />
          </TouchableOpacity>
        </View>
      </View>
      
      <Text style={[styles.postContent, { color: theme.colors.textSecondary }]} numberOfLines={2}>
        {post.content}
      </Text>
      
      <View style={styles.postPlatforms}>
        {post.platforms.map((platform) => (
          <View
            key={platform}
            style={[styles.platformBadge, { backgroundColor: PLATFORM_COLORS[platform] }]}
          >
            <Text style={styles.platformText}>{platform}</Text>
          </View>
        ))}
      </View>
      
      {post.engagement && (
        <View style={styles.engagementStats}>
          <View style={styles.engagementItem}>
            <Icon name="favorite" size={14} color="#ef4444" />
            <Text style={[styles.engagementText, { color: theme.colors.textSecondary }]}>
              {post.engagement.likes}
            </Text>
          </View>
          <View style={styles.engagementItem}>
            <Icon name="share" size={14} color="#3b82f6" />
            <Text style={[styles.engagementText, { color: theme.colors.textSecondary }]}>
              {post.engagement.shares}
            </Text>
          </View>
          <View style={styles.engagementItem}>
            <Icon name="comment" size={14} color="#10b981" />
            <Text style={[styles.engagementText, { color: theme.colors.textSecondary }]}>
              {post.engagement.comments}
            </Text>
          </View>
        </View>
      )}
    </View>
  );

  const renderWeekDayHeaders = () => (
    <View style={styles.weekHeader}>
      {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
        <Text key={day} style={[styles.weekDay, { color: theme.colors.textSecondary }]}>
          {day}
        </Text>
      ))}
    </View>
  );

  const selectedDatePosts = selectedDate 
    ? scheduledPosts?.filter(post => post.scheduledTime.split('T')[0] === selectedDate) || []
    : [];

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { backgroundColor: theme.colors.surface }]}>
        <Text style={[styles.title, { color: theme.colors.text }]}>
          Content Calendar
        </Text>
        
        <View style={styles.headerActions}>
          <View style={styles.viewModeToggle}>
            {(['month', 'week', 'list'] as const).map((mode) => (
              <TouchableOpacity
                key={mode}
                style={[
                  styles.viewModeButton,
                  viewMode === mode && { backgroundColor: theme.colors.primary },
                ]}
                onPress={() => setViewMode(mode)}
              >
                <Text style={[
                  styles.viewModeText,
                  viewMode === mode ? styles.activeModeText : { color: theme.colors.text },
                ]}>
                  {mode}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <TouchableOpacity style={[styles.addButton, { backgroundColor: theme.colors.primary }]}>
            <Icon name="add" size={20} color="#fff" />
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
        {viewMode === 'month' && (
          <View style={styles.calendarContainer}>
            {renderCalendarHeader()}
            {renderWeekDayHeaders()}
            <View style={styles.calendarGrid}>
              {generateCalendarDays().map(renderCalendarDay)}
            </View>
          </View>
        )}
        
        {viewMode === 'list' && (
          <View style={styles.listContainer}>
            {scheduledPosts?.map(renderPostItem)}
          </View>
        )}
      </ScrollView>

      {/* Post Details Modal */}
      <Modal
        visible={showPostModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowPostModal(false)}
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: theme.colors.border }]}>
            <TouchableOpacity onPress={() => setShowPostModal(false)}>
              <Text style={[styles.modalCancel, { color: theme.colors.primary }]}>
                Close
              </Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              {selectedDate ? new Date(selectedDate).toLocaleDateString() : ''}
            </Text>
            <View style={styles.modalSpacer} />
          </View>
          
          <ScrollView style={styles.modalContent}>
            {selectedDatePosts.map(renderPostItem)}
          </ScrollView>
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
    gap: 12,
  },
  viewModeToggle: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    borderRadius: 6,
    padding: 2,
  },
  viewModeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  viewModeText: {
    fontSize: 12,
    fontWeight: '500',
    textTransform: 'capitalize',
  },
  addButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  calendarContainer: {
    margin: 16,
  },
  calendarHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  monthTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  weekHeader: {
    flexDirection: 'row',
    paddingVertical: 8,
  },
  weekDay: {
    flex: 1,
    textAlign: 'center',
    fontSize: 12,
    fontWeight: '500',
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  calendarDay: {
    width: (width - 32) / 7,
    height: 80,
    padding: 4,
    borderWidth: 0.5,
    borderColor: '#f3f4f6',
    justifyContent: 'space-between',
  },
  dayNumber: {
    fontSize: 14,
    fontWeight: '500',
    textAlign: 'center',
  },
  postIndicators: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: 2,
  },
  postDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  moreIndicator: {
    fontSize: 10,
    fontWeight: '600',
  },
  listContainer: {
    padding: 16,
  },
  postItem: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  postHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  postInfo: {
    flex: 1,
  },
  postTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
  },
  postTime: {
    fontSize: 12,
  },
  postActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  deleteButton: {
    padding: 4,
  },
  postContent: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  postPlatforms: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 8,
  },
  platformBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  platformText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  engagementStats: {
    flexDirection: 'row',
    gap: 16,
  },
  engagementItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  engagementText: {
    fontSize: 12,
    fontWeight: '500',
  },
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 0.5,
  },
  modalCancel: {
    fontSize: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  modalSpacer: {
    width: 60,
  },
  modalContent: {
    flex: 1,
    padding: 16,
  },
  dimmedDay: {
    opacity: 0.3,
  },
  activeModeText: {
    color: '#fff',
  },
});

