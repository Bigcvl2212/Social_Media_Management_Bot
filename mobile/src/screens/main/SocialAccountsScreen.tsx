/**
 * Social Accounts Screen for Social Media Management Bot
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';

export default function SocialAccountsScreen() {
  const platforms = [
    { name: 'Instagram', status: 'Not Connected', color: '#E4405F' },
    { name: 'TikTok', status: 'Not Connected', color: '#000000' },
    { name: 'YouTube', status: 'Not Connected', color: '#FF0000' },
    { name: 'Twitter/X', status: 'Not Connected', color: '#1DA1F2' },
    { name: 'Facebook', status: 'Not Connected', color: '#1877F2' },
    { name: 'LinkedIn', status: 'Not Connected', color: '#0A66C2' },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Social Accounts</Text>
        <Text style={styles.subtitle}>
          Connect your social media accounts to start managing them
        </Text>
      </View>

      <View style={styles.platformsList}>
        {platforms.map((platform, index) => (
          <View key={index} style={styles.platformCard}>
            <View style={styles.platformInfo}>
              <View 
                style={[styles.platformIcon, { backgroundColor: platform.color }]}
              >
                <Text style={styles.platformIconText}>
                  {platform.name.charAt(0)}
                </Text>
              </View>
              <View style={styles.platformDetails}>
                <Text style={styles.platformName}>{platform.name}</Text>
                <Text style={styles.platformStatus}>{platform.status}</Text>
              </View>
            </View>
            <TouchableOpacity style={styles.connectButton}>
              <Text style={styles.connectButtonText}>Connect</Text>
            </TouchableOpacity>
          </View>
        ))}
      </View>

      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>Why Connect Your Accounts?</Text>
        <View style={styles.benefitsList}>
          <Text style={styles.benefitItem}>• Schedule posts across all platforms</Text>
          <Text style={styles.benefitItem}>• Monitor engagement and analytics</Text>
          <Text style={styles.benefitItem}>• Respond to comments and messages</Text>
          <Text style={styles.benefitItem}>• Auto-post with AI optimization</Text>
        </View>
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
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
  platformsList: {
    padding: 16,
  },
  platformCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  platformInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  platformIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  platformIconText: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  platformDetails: {
    flex: 1,
  },
  platformName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  platformStatus: {
    fontSize: 14,
    color: '#6b7280',
  },
  connectButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  connectButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  infoSection: {
    margin: 16,
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  benefitsList: {
    marginLeft: 8,
  },
  benefitItem: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 8,
  },
});