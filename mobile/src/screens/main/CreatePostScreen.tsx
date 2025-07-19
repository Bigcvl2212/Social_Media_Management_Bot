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
import aiContentService from '../../services/aiContentService';

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
  // AI generation state
  const [aiPrompt, setAiPrompt] = useState('');
  const [selectedAIFeature, setSelectedAIFeature] = useState<'content' | 'hashtags' | 'image' | 'ideas'>('content');
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [generatedHashtags, setGeneratedHashtags] = useState<string[]>([]);

  const AI_FEATURES = [
    { id: 'content' as const, label: 'Generate Content', icon: 'article', description: 'Create engaging post content' },
    { id: 'hashtags' as const, label: 'Generate Hashtags', icon: 'tag', description: 'Find relevant hashtags' },
    { id: 'image' as const, label: 'Generate Image', icon: 'image', description: 'Create AI-generated images' },
    { id: 'ideas' as const, label: 'Content Ideas', icon: 'lightbulb', description: 'Get content inspiration' },
  ];
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
      switch (selectedAIFeature) {
        case 'content':
          const contentResult = await aiContentService.generateContent(aiPrompt, selectedPlatforms, contentType);
          setTitle(contentResult.title || title);
          setCaption(contentResult.content);
          break;

        case 'hashtags':
          const hashtags = await aiContentService.generateHashtags(aiPrompt, selectedPlatforms[0] || 'instagram', 10);
          setGeneratedHashtags(hashtags);
          // Append hashtags to caption
          if (hashtags.length > 0) {
            const hashtagString = '\n\n' + hashtags.map(tag => `#${tag}`).join(' ');
            setCaption(prev => prev + hashtagString);
          }
          break;

        case 'image':
          const imageResult = await aiContentService.generateImage(aiPrompt, 'square');
          if (imageResult.image_url) {
            // Add the generated image to media files
            const mockMediaFile: MediaFile = {
              uri: imageResult.image_url,
              type: 'image/jpeg',
              filename: 'ai-generated-image.jpg',
              fileSize: 0,
              width: 512,
              height: 512,
            };
            setMediaFiles(prev => [...prev, mockMediaFile]);
            setUploadedUrls(prev => [...prev, imageResult.image_url]);
          }
          break;

        case 'ideas':
          const ideas = await aiContentService.getContentIdeas(selectedPlatforms.length > 0 ? selectedPlatforms : ['instagram'], contentType);
          const ideaTexts = ideas.map(idea => typeof idea === 'string' ? idea : idea.title || idea.content || '');
          setAiSuggestions(ideaTexts);
          break;
      }

      setShowAIModal(false);
      setAiPrompt('');
      
      Alert.alert('Success', `AI ${selectedAIFeature} generated successfully!`);
    } catch (error) {
      console.error('AI generation error:', error);
      Alert.alert('Error', `Failed to generate AI ${selectedAIFeature}. Please try again.`);
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const handleApplySuggestion = (suggestion: string) => {
    setCaption(suggestion);
    setAiSuggestions([]);
  };

  const handleGenerateHashtagsOnly = async () => {
    if (!caption.trim()) {
      Alert.alert('Error', 'Please enter some content first to generate relevant hashtags');
      return;
    }

    try {
      const hashtags = await aiContentService.generateHashtags(caption, [selectedPlatforms[0] || 'instagram'], 10);
      setGeneratedHashtags(hashtags);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate hashtags');
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
          
          {/* AI Suggestions Panel */}
          {aiSuggestions.length > 0 && (
            <View style={[styles.suggestionsPanel, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}>
              <Text style={[styles.suggestionsTitle, { color: theme.colors.text }]}>
                AI Content Ideas:
              </Text>
              {aiSuggestions.map((suggestion, index) => (
                <TouchableOpacity
                  key={index}
                  style={[styles.suggestionItem, { borderColor: theme.colors.border }]}
                  onPress={() => handleApplySuggestion(suggestion)}
                >
                  <Text style={[styles.suggestionText, { color: theme.colors.text }]} numberOfLines={2}>
                    {suggestion}
                  </Text>
                  <Icon name="arrow-forward" size={16} color={theme.colors.primary} />
                </TouchableOpacity>
              ))}
              <TouchableOpacity
                style={[styles.dismissButton, { backgroundColor: theme.colors.error + '20' }]}
                onPress={() => setAiSuggestions([])}
              >
                <Text style={[styles.dismissButtonText, { color: theme.colors.error }]}>
                  Dismiss Suggestions
                </Text>
              </TouchableOpacity>
            </View>
          )}

          {/* Hashtags Management */}
          <View style={styles.hashtagsSection}>
            <View style={styles.sectionHeader}>
              <Text style={[styles.sectionSubTitle, { color: theme.colors.text }]}>
                Hashtags
              </Text>
              <TouchableOpacity
                style={[styles.generateHashtagsButton, { backgroundColor: theme.colors.primary + '20' }]}
                onPress={handleGenerateHashtagsOnly}
              >
                <Icon name="tag" size={14} color={theme.colors.primary} />
                <Text style={[styles.generateHashtagsText, { color: theme.colors.primary }]}>
                  Generate
                </Text>
              </TouchableOpacity>
            </View>
            
            {generatedHashtags.length > 0 && (
              <View style={styles.hashtagsContainer}>
                {generatedHashtags.map((hashtag, index) => (
                  <TouchableOpacity
                    key={index}
                    style={[styles.hashtagChip, { backgroundColor: theme.colors.primary + '20' }]}
                    onPress={() => {
                      const hashtagText = `#${hashtag} `;
                      setCaption(prev => prev + hashtagText);
                    }}
                  >
                    <Text style={[styles.hashtagText, { color: theme.colors.primary }]}>
                      #{hashtag}
                    </Text>
                    <Icon name="add" size={14} color={theme.colors.primary} />
                  </TouchableOpacity>
                ))}
              </View>
            )}
          </View>
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
            {/* AI Feature Selection */}
            <Text style={[styles.inputLabel, { color: theme.colors.text }]}>
              Choose AI Feature:
            </Text>
            <View style={styles.aiFeatureGrid}>
              {AI_FEATURES.map((feature) => (
                <TouchableOpacity
                  key={feature.id}
                  style={[
                    styles.aiFeatureCard,
                    { 
                      backgroundColor: selectedAIFeature === feature.id ? theme.colors.primary + '20' : theme.colors.surface,
                      borderColor: selectedAIFeature === feature.id ? theme.colors.primary : theme.colors.border,
                    }
                  ]}
                  onPress={() => setSelectedAIFeature(feature.id)}
                >
                  <Icon 
                    name={feature.icon} 
                    size={24} 
                    color={selectedAIFeature === feature.id ? theme.colors.primary : theme.colors.textSecondary} 
                  />
                  <Text style={[
                    styles.aiFeatureLabel, 
                    { color: selectedAIFeature === feature.id ? theme.colors.primary : theme.colors.text }
                  ]}>
                    {feature.label}
                  </Text>
                  <Text style={[styles.aiFeatureDescription, { color: theme.colors.textSecondary }]}>
                    {feature.description}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={[styles.inputLabel, styles.aiPromptLabel, { color: theme.colors.text }]}>
              {selectedAIFeature === 'content' ? 'Describe what you want to post about:' :
               selectedAIFeature === 'hashtags' ? 'Describe your content for hashtag generation:' :
               selectedAIFeature === 'image' ? 'Describe the image you want to generate:' :
               'What type of content ideas do you need?'}
            </Text>
            <TextInput
              style={[styles.textArea, { backgroundColor: theme.colors.surface, color: theme.colors.text, borderColor: theme.colors.border }]}
              value={aiPrompt}
              onChangeText={setAiPrompt}
              placeholder={
                selectedAIFeature === 'content' ? 'e.g., A motivational post about productivity tips for entrepreneurs' :
                selectedAIFeature === 'hashtags' ? 'e.g., Healthy breakfast recipe with avocado' :
                selectedAIFeature === 'image' ? 'e.g., A minimalist workspace with laptop and coffee' :
                'e.g., Content ideas for a fitness brand targeting millennials'
              }
              placeholderTextColor={theme.colors.textSecondary}
              multiline
              numberOfLines={3}
            />
            
            <TouchableOpacity
              style={[
                styles.generateButton, 
                { backgroundColor: theme.colors.primary },
                (isGeneratingAI || !aiPrompt.trim()) && styles.disabledButton
              ]}
              onPress={handleGenerateAIContent}
              disabled={isGeneratingAI || !aiPrompt.trim()}
            >
              {isGeneratingAI ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <>
                  <Icon name="auto-awesome" size={20} color="#fff" />
                  <Text style={styles.generateButtonText}>
                    Generate {AI_FEATURES.find(f => f.id === selectedAIFeature)?.label}
                  </Text>
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
  // Enhanced AI UI styles
  suggestionsPanel: {
    marginTop: 12,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
  },
  suggestionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderBottomWidth: 0.5,
    marginBottom: 8,
    borderRadius: 6,
  },
  suggestionText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
  dismissButton: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    borderRadius: 6,
    marginTop: 8,
  },
  dismissButtonText: {
    fontSize: 12,
    fontWeight: '500',
  },
  hashtagsSection: {
    marginTop: 16,
  },
  sectionSubTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  generateHashtagsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  generateHashtagsText: {
    fontSize: 12,
    fontWeight: '500',
  },
  hashtagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginTop: 12,
  },
  hashtagChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  hashtagText: {
    fontSize: 12,
    fontWeight: '500',
  },
  aiFeatureGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  aiFeatureCard: {
    width: '47%',
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    alignItems: 'center',
    minHeight: 80,
    justifyContent: 'center',
  },
  aiFeatureLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 6,
    textAlign: 'center',
  },
  aiFeatureDescription: {
    fontSize: 10,
    textAlign: 'center',
    marginTop: 2,
  },
  aiPromptLabel: {
    marginTop: 20,
  },
  disabledButton: {
    opacity: 0.6,
  },
});