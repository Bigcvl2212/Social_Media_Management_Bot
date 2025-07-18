/**
 * Create Post Screen for Social Media Management Bot
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';

export default function CreatePostScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Create Post</Text>
      </View>

      <View style={styles.content}>
        <Text style={styles.comingSoon}>Coming Soon</Text>
        <Text style={styles.description}>
          Create and publish content across all your social platforms
        </Text>
        
        <View style={styles.featureList}>
          <Text style={styles.featureItem}>• AI-powered caption generation</Text>
          <Text style={styles.featureItem}>• Multi-media upload support</Text>
          <Text style={styles.featureItem}>• Cross-platform publishing</Text>
          <Text style={styles.featureItem}>• Content optimization suggestions</Text>
          <Text style={styles.featureItem}>• Template library</Text>
        </View>

        <TouchableOpacity style={styles.demoButton}>
          <Text style={styles.demoButtonText}>Try Demo</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    padding: 24,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  comingSoon: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#10b981',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 32,
  },
  featureList: {
    alignItems: 'flex-start',
    marginBottom: 32,
  },
  featureItem: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 8,
  },
  demoButton: {
    backgroundColor: '#10b981',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  demoButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});