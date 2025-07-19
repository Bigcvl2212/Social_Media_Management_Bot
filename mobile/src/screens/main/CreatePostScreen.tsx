/**
 * Create Post Screen
 * Enhanced with AI content generation, media upload, and offline drafting
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  Modal,
  FlatList,
  Image,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../../contexts/ThemeContext';
import { PlatformType, ContentType } from '../../types';
import mediaUploadService, { MediaFile } from '../../services/mediaUploadService';
import offlineStorageService from '../../services/offlineStorageService';

const PLATFORMS: { id: PlatformType; name: string; icon: string; color: string }[] = [
  { id: 'instagram', name: 'Instagram', icon: 'camera-alt', color: '#E4405F' },
  { id: 'tiktok', name: 'TikTok', icon: 'music-video', color: '#000000' },
  { id: 'youtube', name: 'YouTube', icon: 'play-circle-filled', color: '#FF0000' },
  { id: 'twitter', name: 'Twitter/X', icon: 'alternate-email', color: '#1DA1F2' },
  { id: 'facebook', name: 'Facebook', icon: 'facebook', color: '#1877F2' },
  { id: 'linkedin', name: 'LinkedIn', icon: 'business', color: '#0A66C2' },
];

const CONTENT_TYPES: { id: ContentType; name: string; icon: string }[] = [
  { id: 'post', name: 'Post', icon: 'article' },
  { id: 'story', name: 'Story', icon: 'auto-stories' },
  { id: 'reel', name: 'Reel', icon: 'video-library' },
  { id: 'video', name: 'Video', icon: 'videocam' },
];

export default function CreatePostScreen() {
  const { theme } = useTheme();
  
  // Form state
  const [title, setTitle] = useState('');
  const [caption, setCaption] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<PlatformType[]>([]);
  const [contentType, setContentType] = useState<ContentType>('post');
  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);
  const [uploadedUrls, setUploadedUrls] = useState<string[]>([]);
  const [scheduledTime, setScheduledTime] = useState<Date | null>(null);
  
  // UI state
  const [showAIModal, setShowAIModal] = useState(false);
  const [showContentTypeModal, setShowContentTypeModal] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [isUploadingMedia, setIsUploadingMedia] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isOfflineMode, setIsOfflineMode] = useState(false);

  useEffect(() => {
    // Check if we're in offline mode
    setIsOfflineMode(!offlineStorageService.isOnlineStatus());
  }, []);

  const handlePlatformToggle = (platform: PlatformType) => {
    setSelectedPlatforms(prev => 
      prev.includes(platform) 
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  const handleGenerateAIContent = async () => {
    if (!aiPrompt.trim()) {
      Alert.alert('Error', 'Please enter a prompt for AI generation');
      return;
    }

    setIsGeneratingAI(true);
    try {
      // Mock AI generation for demo
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResult = {
        title: 'AI Generated Title',
        caption: `Here's an AI-generated caption based on your prompt: "${aiPrompt}". This would normally be generated using advanced AI models.`,
        hashtags: ['#AI', '#Generated', '#Content'],
        suggestions: ['Consider adding more visual elements', 'Try a different tone for better engagement'],
      };

      setTitle(mockResult.title);
      setCaption(mockResult.caption);
      setShowAIModal(false);
      setAiPrompt('');
      
      Alert.alert('Success', 'AI content generated successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to generate AI content. Please try again.');
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const handleAddMedia = async () => {
    try {
      const newMediaFiles = await mediaUploadService.showMediaPicker({
        mediaType: 'mixed',
        quality: 0.8,
        multiple: true,
      });

      if (newMediaFiles.length > 0) {
        setMediaFiles(prev => [...prev, ...newMediaFiles]);
        
        // Upload media if online
        if (offlineStorageService.isOnlineStatus()) {
          setIsUploadingMedia(true);
          try {
            // Mock upload for demo
            await new Promise(resolve => setTimeout(resolve, 1500));
            const mockUrls = newMediaFiles.map((_, index) => `https://example.com/media/${Date.now()}_${index}.jpg`);
            setUploadedUrls(prev => [...prev, ...mockUrls]);
          } catch (error) {
            Alert.alert('Error', 'Failed to upload some media files');
          } finally {
            setIsUploadingMedia(false);
          }
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to select media files');
    }
  };

  const handleRemoveMedia = (index: number) => {
    setMediaFiles(prev => prev.filter((_, i) => i !== index));
    setUploadedUrls(prev => prev.filter((_, i) => i !== index));
  };

  const handleSaveDraft = async () => {
    if (!title.trim() || !caption.trim()) {
      Alert.alert('Error', 'Please provide both title and caption');
      return;
    }

    if (selectedPlatforms.length === 0) {
      Alert.alert('Error', 'Please select at least one platform');
      return;
    }

    setIsSaving(true);
    try {
      offlineStorageService.saveDraftOffline({
        title: title.trim(),
        caption: caption.trim(),
        content_type: contentType,
        media_urls: uploadedUrls,
        platforms: selectedPlatforms,
        scheduled_time: scheduledTime?.toISOString(),
        mediaLocalPaths: mediaFiles.map(file => file.uri),
      });

      Alert.alert(
        'Success', 
        isOfflineMode 
          ? 'Draft saved offline. It will sync when you\'re back online.' 
          : 'Draft saved successfully!'
      );

      // Reset form
      resetForm();
      
    } catch (error) {
      Alert.alert('Error', 'Failed to save draft');
    } finally {
      setIsSaving(false);
    }
  };

  const resetForm = () => {
    setTitle('');
    setCaption('');
    setSelectedPlatforms([]);
    setContentType('post');
    setMediaFiles([]);
    setUploadedUrls([]);
    setScheduledTime(null);
  };

  const renderPlatformSelector = () => (
    <View style={styles.section}>
      <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
        Select Platforms
      </Text>
      <View style={styles.platformsContainer}>
        {PLATFORMS.map((platform) => (
          <TouchableOpacity
            key={platform.id}
            style={[
              styles.platformItem,
              { 
                backgroundColor: selectedPlatforms.includes(platform.id) 
                  ? platform.color 
                  : theme.colors.surface,
                borderColor: theme.colors.border,
              }
            ]}
            onPress={() => handlePlatformToggle(platform.id)}
          >
            <Icon 
              name={platform.icon} 
              size={20} 
              color={selectedPlatforms.includes(platform.id) ? '#fff' : theme.colors.text} 
            />
            <Text 
              style={[
                styles.platformText, 
                selectedPlatforms.includes(platform.id) 
                  ? styles.platformTextSelected
                  : { color: theme.colors.text }
              ]}
            >
              {platform.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  const renderMediaSection = () => (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
          Add Media
        </Text>
        <TouchableOpacity
          style={[styles.addButton, { backgroundColor: theme.colors.primary }]}
          onPress={handleAddMedia}
          disabled={isUploadingMedia}
        >
          {isUploadingMedia ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Icon name="add" size={20} color="#fff" />
          )}
        </TouchableOpacity>
      </View>
      
      {mediaFiles.length > 0 && (
        <ScrollView horizontal style={styles.mediaPreview}>
          {mediaFiles.map((file, index) => (
            <View key={index} style={styles.mediaItem}>
              <Image source={{ uri: file.uri }} style={styles.mediaImage} />
              <TouchableOpacity
                style={styles.removeMediaButton}
                onPress={() => handleRemoveMedia(index)}
              >
                <Icon name="close" size={16} color="#fff" />
              </TouchableOpacity>
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView style={styles.scrollView}>
        {/* Offline Indicator */}
        {isOfflineMode && (
          <View style={[styles.offlineIndicator, { backgroundColor: theme.colors.warning }]}>
            <Icon name="cloud-off" size={16} color="#fff" />
            <Text style={styles.offlineText}>Offline Mode - Drafts will sync when online</Text>
          </View>
        )}

        {/* Content Type Selector */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Content Type
          </Text>
          <TouchableOpacity
            style={[styles.selector, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
            onPress={() => setShowContentTypeModal(true)}
          >
            <Text style={[styles.selectorText, { color: theme.colors.text }]}>
              {CONTENT_TYPES.find(type => type.id === contentType)?.name || 'Post'}
            </Text>
            <Icon name="keyboard-arrow-down" size={24} color={theme.colors.textSecondary} />
          </TouchableOpacity>
        </View>

        {/* Title Input */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
            Title
          </Text>
          <TextInput
            style={[styles.textInput, { backgroundColor: theme.colors.surface, color: theme.colors.text, borderColor: theme.colors.border }]}
            value={title}
            onChangeText={setTitle}
            placeholder="Enter post title..."
            placeholderTextColor={theme.colors.textSecondary}
          />
        </View>

        {/* Caption Input with AI Generation */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.colors.text }]}>
              Caption
            </Text>
            <TouchableOpacity
              style={[styles.aiButton, { backgroundColor: theme.colors.info }]}
              onPress={() => setShowAIModal(true)}
            >
              <Icon name="auto-awesome" size={16} color="#fff" />
              <Text style={styles.aiButtonText}>AI</Text>
            </TouchableOpacity>
          </View>
          <TextInput
            style={[styles.textArea, { backgroundColor: theme.colors.surface, color: theme.colors.text, borderColor: theme.colors.border }]}
            value={caption}
            onChangeText={setCaption}
            placeholder="Write your caption..."
            placeholderTextColor={theme.colors.textSecondary}
            multiline
            numberOfLines={4}
          />
        </View>

        {/* Platform Selector */}
        {renderPlatformSelector()}

        {/* Media Section */}
        {renderMediaSection()}

        {/* Action Buttons */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity
            style={[styles.actionButton, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
            onPress={handleSaveDraft}
            disabled={isSaving}
          >
            {isSaving ? (
              <ActivityIndicator size="small" color={theme.colors.primary} />
            ) : (
              <>
                <Icon name="save" size={20} color={theme.colors.primary} />
                <Text style={[styles.actionButtonText, { color: theme.colors.primary }]}>
                  Save Draft
                </Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.primaryButton, { backgroundColor: theme.colors.primary }]}
            onPress={() => Alert.alert('Coming Soon', 'Publishing feature will be available soon!')}
          >
            <Icon name="publish" size={20} color="#fff" />
            <Text style={[styles.actionButtonText, styles.whiteText]}>
              Publish Now
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* AI Generation Modal */}
      <Modal
        visible={showAIModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowAIModal(false)}
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: theme.colors.border }]}>
            <TouchableOpacity onPress={() => setShowAIModal(false)}>
              <Text style={[styles.modalCancel, { color: theme.colors.primary }]}>
                Cancel
              </Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              AI Content Generation
            </Text>
            <View style={styles.modalSpacer} />
          </View>
          
          <View style={styles.modalContent}>
            <Text style={[styles.inputLabel, { color: theme.colors.text }]}>
              Describe what you want to post about:
            </Text>
            <TextInput
              style={[styles.textArea, { backgroundColor: theme.colors.surface, color: theme.colors.text, borderColor: theme.colors.border }]}
              value={aiPrompt}
              onChangeText={setAiPrompt}
              placeholder="e.g., A motivational post about productivity tips for entrepreneurs"
              placeholderTextColor={theme.colors.textSecondary}
              multiline
              numberOfLines={3}
            />
            
            <TouchableOpacity
              style={[styles.generateButton, { backgroundColor: theme.colors.primary }]}
              onPress={handleGenerateAIContent}
              disabled={isGeneratingAI || !aiPrompt.trim()}
            >
              {isGeneratingAI ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <>
                  <Icon name="auto-awesome" size={20} color="#fff" />
                  <Text style={styles.generateButtonText}>Generate Content</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Content Type Modal */}
      <Modal
        visible={showContentTypeModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowContentTypeModal(false)}
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: theme.colors.border }]}>
            <TouchableOpacity onPress={() => setShowContentTypeModal(false)}>
              <Text style={[styles.modalCancel, { color: theme.colors.primary }]}>
                Cancel
              </Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              Content Type
            </Text>
            <View style={styles.modalSpacer} />
          </View>
          
          <FlatList
            data={CONTENT_TYPES}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[styles.contentTypeItem, { borderBottomColor: theme.colors.border }]}
                onPress={() => {
                  setContentType(item.id);
                  setShowContentTypeModal(false);
                }}
              >
                <Icon name={item.icon} size={24} color={theme.colors.primary} />
                <Text style={[styles.contentTypeText, { color: theme.colors.text }]}>
                  {item.name}
                </Text>
                {contentType === item.id && (
                  <Icon name="check" size={20} color={theme.colors.primary} />
                )}
              </TouchableOpacity>
            )}
          />
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  offlineIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    gap: 8,
  },
  offlineText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  section: {
    marginBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  selector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
  },
  selectorText: {
    fontSize: 16,
  },
  platformsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  platformItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    gap: 6,
  },
  platformText: {
    fontSize: 14,
    fontWeight: '500',
  },
  aiButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  aiButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  addButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mediaPreview: {
    marginTop: 8,
  },
  mediaItem: {
    position: 'relative',
    marginRight: 8,
  },
  mediaImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  removeMediaButton: {
    position: 'absolute',
    top: -6,
    right: -6,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#ef4444',
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: 12,
    paddingVertical: 16,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    gap: 8,
  },
  primaryButton: {
    borderWidth: 0,
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
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
    padding: 16,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 8,
  },
  generateButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
    gap: 8,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  contentTypeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 0.5,
    gap: 12,
  },
  contentTypeText: {
    flex: 1,
    fontSize: 16,
  },
  platformTextSelected: {
    color: '#fff',
  },
  whiteText: {
    color: '#fff',
  },
});