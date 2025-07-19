/**
 * Advanced AI Dashboard Screen
 * State-of-the-art AI features for viral content creation and social media management
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Modal,
  TextInput,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../../contexts/ThemeContext';
import { aiContentService } from '../../services/aiContentService';
import { socialMonitoringService, SocialInteraction } from '../../services/socialMonitoringService';
import { autonomousContentService, GeneratedContent } from '../../services/autonomousContentService';
import { PlatformType, ContentType } from '../../types';

interface AIFeature {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  premium: boolean;
  viralCapability: boolean;
}

const ADVANCED_AI_FEATURES: AIFeature[] = [
  {
    id: 'video_editing',
    title: 'Viral Video Editing',
    description: 'Human-level AI video editing for maximum engagement',
    icon: 'movie',
    color: '#FF6B6B',
    premium: true,
    viralCapability: true,
  },
  {
    id: 'autonomous_content',
    title: 'Autonomous Content Creation',
    description: 'AI creates content from your library automatically',
    icon: 'auto-awesome',
    color: '#4ECDC4',
    premium: true,
    viralCapability: true,
  },
  {
    id: 'social_monitoring',
    title: 'AI Social Monitoring',
    description: 'Monitor and respond to all interactions automatically',
    icon: 'monitor',
    color: '#45B7D1',
    premium: true,
    viralCapability: false,
  },
  {
    id: 'multi_format',
    title: 'Multi-Format Generator',
    description: 'Create videos, images, graphics, posts in one click',
    icon: 'view-module',
    color: '#96CEB4',
    premium: true,
    viralCapability: true,
  },
  {
    id: 'growth_analysis',
    title: 'Growth Intelligence',
    description: 'Deep insights and actionable growth strategies',
    icon: 'trending-up',
    color: '#FFEAA7',
    premium: true,
    viralCapability: false,
  },
  {
    id: 'viral_optimization',
    title: 'Viral Optimization',
    description: 'Real-time content optimization for maximum reach',
    icon: 'rocket-launch',
    color: '#DDA0DD',
    premium: true,
    viralCapability: true,
  },
];

const AIAdvancedDashboard: React.FC = () => {
  const { theme } = useTheme();
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  
  // Data states
  const [recentInteractions, setRecentInteractions] = useState<SocialInteraction[]>([]);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load recent interactions
      const interactions = await socialMonitoringService.getInteractions(10);
      setRecentInteractions(interactions.interactions);
      
      // Load generated content
      const content = await autonomousContentService.getGeneratedContent('pending_review', 5);
      setGeneratedContent(content.content);
      
      // Load analytics
      const analyticsData = await socialMonitoringService.getAnalytics('24h');
      setAnalytics(analyticsData);
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleFeaturePress = (feature: AIFeature) => {
    setSelectedFeature(feature.id);
    setModalVisible(true);
  };

  const renderFeatureCard = ({ item }: { item: AIFeature }) => (
    <TouchableOpacity
      style={[styles.featureCard, { backgroundColor: theme.colors.surface }]}
      onPress={() => handleFeaturePress(item)}
    >
      <View style={[styles.featureIcon, { backgroundColor: item.color + '20' }]}>
        <Icon name={item.icon} size={32} color={item.color} />
        {item.viralCapability && (
          <View style={styles.viralBadge}>
            <Icon name="local-fire-department" size={16} color="#FF4500" />
          </View>
        )}
        {item.premium && (
          <View style={styles.premiumBadge}>
            <Icon name="star" size={14} color="#FFD700" />
          </View>
        )}
      </View>
      <Text style={[styles.featureTitle, { color: theme.colors.text }]}>
        {item.title}
      </Text>
      <Text style={[styles.featureDescription, { color: theme.colors.textSecondary }]}>
        {item.description}
      </Text>
    </TouchableOpacity>
  );

  const renderInteractionItem = ({ item }: { item: SocialInteraction }) => (
    <TouchableOpacity
      style={[styles.interactionCard, { backgroundColor: theme.colors.surface }]}
    >
      <View style={styles.interactionHeader}>
        <Text style={[styles.interactionAuthor, { color: theme.colors.text }]}>
          {item.author.displayName}
        </Text>
        <View style={[
          styles.priorityBadge,
          { backgroundColor: item.priority === 'high' ? '#FF6B6B' : 
                             item.priority === 'medium' ? '#FFA726' : '#66BB6A' }
        ]}>
          <Text style={styles.priorityText}>{item.priority.toUpperCase()}</Text>
        </View>
      </View>
      <Text style={[styles.interactionContent, { color: theme.colors.textSecondary }]}>
        {item.content.substring(0, 100)}...
      </Text>
      <View style={styles.interactionFooter}>
        <Text style={[styles.interactionPlatform, { color: theme.colors.primary }]}>
          {item.platform.toUpperCase()}
        </Text>
        {item.suggestedReply && (
          <TouchableOpacity style={styles.replyButton}>
            <Icon name="reply" size={16} color={theme.colors.primary} />
            <Text style={[styles.replyButtonText, { color: theme.colors.primary }]}>
              AI Reply Ready
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </TouchableOpacity>
  );

  const renderContentItem = ({ item }: { item: GeneratedContent }) => (
    <TouchableOpacity
      style={[styles.contentCard, { backgroundColor: theme.colors.surface }]}
    >
      <View style={styles.contentHeader}>
        <Text style={[styles.contentTitle, { color: theme.colors.text }]}>
          {item.content.title}
        </Text>
        <View style={styles.viralScoreContainer}>
          <Icon name="local-fire-department" size={16} color="#FF4500" />
          <Text style={[styles.viralScore, { color: '#FF4500' }]}>
            {Math.round(item.analytics.viralScore)}%
          </Text>
        </View>
      </View>
      <Text style={[styles.contentBody, { color: theme.colors.textSecondary }]}>
        {item.content.body.substring(0, 80)}...
      </Text>
      <View style={styles.contentFooter}>
        <Text style={[styles.contentPlatform, { color: theme.colors.primary }]}>
          {item.platform.toUpperCase()}
        </Text>
        <View style={styles.contentActions}>
          <TouchableOpacity style={[styles.actionButton, styles.approveButton]}>
            <Icon name="check" size={16} color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionButton, styles.rejectButton]}>
            <Icon name="close" size={16} color="#fff" />
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <ScrollView
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={[styles.headerTitle, { color: theme.colors.text }]}>
          AI Command Center
        </Text>
        <Text style={[styles.headerSubtitle, { color: theme.colors.textSecondary }]}>
          State-of-the-art AI for viral content & growth
        </Text>
      </View>

      {/* Analytics Overview */}
      {analytics && (
        <View style={[styles.analyticsContainer, { backgroundColor: theme.colors.surface }]}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Today's AI Performance
          </Text>
          <View style={styles.analyticsGrid}>
            <View style={styles.analyticCard}>
              <Text style={[styles.analyticNumber, { color: theme.colors.primary }]}>
                {analytics.totalInteractions}
              </Text>
              <Text style={[styles.analyticLabel, { color: theme.colors.textSecondary }]}>
                Interactions
              </Text>
            </View>
            <View style={styles.analyticCard}>
              <Text style={[styles.analyticNumber, { color: '#4ECDC4' }]}>
                {Math.round(analytics.responseRate)}%
              </Text>
              <Text style={[styles.analyticLabel, { color: theme.colors.textSecondary }]}>
                Auto-Reply Rate
              </Text>
            </View>
            <View style={styles.analyticCard}>
              <Text style={[styles.analyticNumber, { color: '#FF6B6B' }]}>
                {Math.round(analytics.avgResponseTime)}m
              </Text>
              <Text style={[styles.analyticLabel, { color: theme.colors.textSecondary }]}>
                Avg Response
              </Text>
            </View>
            <View style={styles.analyticCard}>
              <Text style={[styles.analyticNumber, { color: '#96CEB4' }]}>
                +{Math.round(analytics.engagementGrowth)}%
              </Text>
              <Text style={[styles.analyticLabel, { color: theme.colors.textSecondary }]}>
                Growth
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* AI Features Grid */}
      <View style={styles.featuresSection}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          Advanced AI Features
        </Text>
        <FlatList
          data={ADVANCED_AI_FEATURES}
          renderItem={renderFeatureCard}
          keyExtractor={(item) => item.id}
          numColumns={2}
          scrollEnabled={false}
          contentContainerStyle={styles.featuresGrid}
        />
      </View>

      {/* Recent Interactions */}
      <View style={styles.interactionsSection}>
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Recent Interactions
          </Text>
          <TouchableOpacity>
            <Text style={[styles.seeAllText, { color: theme.colors.primary }]}>
              See All
            </Text>
          </TouchableOpacity>
        </View>
        <FlatList
          data={recentInteractions}
          renderItem={renderInteractionItem}
          keyExtractor={(item) => item.id}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.horizontalList}
        />
      </View>

      {/* Generated Content */}
      <View style={styles.contentSection}>
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            AI Generated Content
          </Text>
          <TouchableOpacity>
            <Text style={[styles.seeAllText, { color: theme.colors.primary }]}>
              Review All
            </Text>
          </TouchableOpacity>
        </View>
        <FlatList
          data={generatedContent}
          renderItem={renderContentItem}
          keyExtractor={(item) => item.id}
          scrollEnabled={false}
        />
      </View>

      {/* Feature Detail Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.colors.background }]}>
          <View style={styles.modalHeader}>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              {selectedFeature && ADVANCED_AI_FEATURES.find(f => f.id === selectedFeature)?.title}
            </Text>
            <TouchableOpacity onPress={() => setModalVisible(false)}>
              <Icon name="close" size={24} color={theme.colors.text} />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            <Text style={[styles.modalDescription, { color: theme.colors.textSecondary }]}>
              {selectedFeature && ADVANCED_AI_FEATURES.find(f => f.id === selectedFeature)?.description}
            </Text>
            
            {/* Feature-specific content would go here */}
            <View style={styles.featureContent}>
              <Text style={[styles.comingSoonText, { color: theme.colors.textSecondary }]}>
                Advanced configuration panel coming soon...
              </Text>
            </View>
          </ScrollView>
        </View>
      </Modal>

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingTop: 40,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 16,
    opacity: 0.8,
  },
  analyticsContainer: {
    margin: 20,
    padding: 20,
    borderRadius: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  analyticsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 15,
  },
  analyticCard: {
    alignItems: 'center',
    flex: 1,
  },
  analyticNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  analyticLabel: {
    fontSize: 12,
    marginTop: 5,
  },
  featuresSection: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  seeAllText: {
    fontSize: 14,
    fontWeight: '600',
  },
  featuresGrid: {
    gap: 15,
  },
  featureCard: {
    flex: 1,
    margin: 5,
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  featureIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    position: 'relative',
  },
  viralBadge: {
    position: 'absolute',
    top: -5,
    right: -5,
    backgroundColor: '#FFF',
    borderRadius: 10,
    padding: 2,
  },
  premiumBadge: {
    position: 'absolute',
    bottom: -5,
    right: -5,
    backgroundColor: '#FFF',
    borderRadius: 10,
    padding: 2,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  featureDescription: {
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 16,
  },
  interactionsSection: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  contentSection: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  horizontalList: {
    paddingRight: 20,
  },
  interactionCard: {
    width: 280,
    padding: 15,
    borderRadius: 12,
    marginRight: 15,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  interactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  interactionAuthor: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  priorityText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  interactionContent: {
    fontSize: 12,
    lineHeight: 16,
    marginBottom: 10,
  },
  interactionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  interactionPlatform: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  replyButton: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  replyButtonText: {
    fontSize: 10,
    marginLeft: 4,
  },
  contentCard: {
    padding: 15,
    borderRadius: 12,
    marginBottom: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  contentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  contentTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    flex: 1,
  },
  viralScoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  viralScore: {
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  contentBody: {
    fontSize: 12,
    lineHeight: 16,
    marginBottom: 10,
  },
  contentFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  contentPlatform: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  contentActions: {
    flexDirection: 'row',
  },
  actionButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  approveButton: {
    backgroundColor: '#4CAF50',
  },
  rejectButton: {
    backgroundColor: '#F44336',
  },
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  modalDescription: {
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 20,
  },
  featureContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  comingSoonText: {
    fontSize: 14,
    fontStyle: 'italic',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
});

export default AIAdvancedDashboard;