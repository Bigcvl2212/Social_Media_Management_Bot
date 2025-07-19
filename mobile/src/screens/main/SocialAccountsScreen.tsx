/**
 * Social Accounts Screen for Social Media Management Bot
 * Enhanced with real OAuth integration and account management
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
  ActivityIndicator,
  Linking,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useTheme } from '../../contexts/ThemeContext';
import { useFocusEffect } from '@react-navigation/native';
import { PlatformType } from '../../types';
import oauthService from '../../services/oauthService';

interface ConnectedAccount {
  platform: PlatformType;
  username: string;
  userId: string;
  connected: boolean;
  lastSync?: string;
  status: 'active' | 'error' | 'pending';
}

export default function SocialAccountsScreen() {
  const { theme } = useTheme();
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const platformConfigs = oauthService.getAllPlatformConfigs();

  const loadAccountStatus = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const accountsData: ConnectedAccount[] = [];
      
      for (const [platform] of Object.entries(platformConfigs) as [PlatformType, any][]) {
        const credentials = oauthService.getStoredCredentials(platform);
        const isConnected = oauthService.isConnected(platform);
        
        accountsData.push({
          platform,
          username: credentials?.platformUsername || '',
          userId: credentials?.platformUserId || '',
          connected: isConnected,
          lastSync: credentials ? new Date().toISOString() : undefined,
          status: isConnected ? 'active' : 'pending',
        });
      }
      
      setAccounts(accountsData);
    } catch (error) {
      console.error('Error loading account status:', error);
    } finally {
      setIsLoading(false);
    }
  }, [platformConfigs]);

  const handleOAuthCallback = React.useCallback(async (url: string) => {
    try {
      const parsedUrl = new URL(url);
      if (parsedUrl.hostname !== 'oauth') return;

      const platform = parsedUrl.pathname.replace('/', '') as PlatformType;
      const code = parsedUrl.searchParams.get('code');
      const state = parsedUrl.searchParams.get('state');

      if (!code || !state) {
        throw new Error('Missing OAuth parameters');
      }

      setIsLoading(true);
      const success = await oauthService.handleOAuthCallback(platform, code, state);
      
      if (success) {
        await loadAccountStatus();
      }
    } catch (error) {
      console.error('OAuth callback error:', error);
      Alert.alert('Authentication Error', 'Failed to complete authentication');
    } finally {
      setIsLoading(false);
    }
  }, [loadAccountStatus]);

  // Load account status on screen focus
  useFocusEffect(
    React.useCallback(() => {
      loadAccountStatus();
    }, [loadAccountStatus])
  );

  // Set up deep link handler for OAuth callbacks
  useEffect(() => {
    const handleDeepLink = (url: string) => {
      handleOAuthCallback(url);
    };

    const subscription = Linking.addEventListener('url', ({ url }) => handleDeepLink(url));
    
    // Check if app was opened with a deep link
    Linking.getInitialURL().then((url) => {
      if (url) {
        handleDeepLink(url);
      }
    });

    return () => subscription?.remove();
  }, [handleOAuthCallback]);

  const refreshAccounts = async () => {
    setIsRefreshing(true);
    await loadAccountStatus();
    setIsRefreshing(false);
  };

  const handleConnect = async (platform: PlatformType) => {
    try {
      setIsLoading(true);
      const success = await oauthService.startOAuthFlow(platform);
      if (!success) {
        Alert.alert('Error', 'Failed to start authentication process');
      }
    } catch (error) {
      console.error('Connection error:', error);
      Alert.alert('Error', 'Failed to connect account');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = async (platform: PlatformType) => {
    Alert.alert(
      'Disconnect Account',
      `Are you sure you want to disconnect your ${platformConfigs[platform].name} account?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Disconnect', 
          style: 'destructive',
          onPress: async () => {
            try {
              setIsLoading(true);
              await oauthService.disconnectPlatform(platform);
              await loadAccountStatus();
            } catch (error) {
              console.error('Disconnect error:', error);
              Alert.alert('Error', 'Failed to disconnect account');
            } finally {
              setIsLoading(false);
            }
          }
        },
      ]
    );
  };

  const handleTestConnection = async (platform: PlatformType) => {
    try {
      setIsLoading(true);
      const isWorking = await oauthService.testConnection(platform);
      
      Alert.alert(
        'Connection Test',
        isWorking 
          ? `${platformConfigs[platform].name} connection is working properly!`
          : `${platformConfigs[platform].name} connection failed. You may need to reconnect.`
      );
    } catch (error) {
      console.error('Test connection error:', error);
      Alert.alert('Error', 'Failed to test connection');
    } finally {
      setIsLoading(false);
    }
  };

  const getPlatformIcon = (platform: PlatformType): string => {
    const iconMap: Record<PlatformType, string> = {
      instagram: 'camera-alt',
      facebook: 'facebook',
      twitter: 'alternate-email',
      linkedin: 'business',
      youtube: 'play-circle-filled',
      tiktok: 'music-video',
    };
    return iconMap[platform] || 'help';
  };

  const renderAccountCard = (account: ConnectedAccount) => {
    const config = platformConfigs[account.platform];
    
    return (
      <View key={account.platform} style={[styles.accountCard, { backgroundColor: theme.colors.surface }]}>
        <View style={styles.accountHeader}>
          <View style={styles.accountInfo}>
            <View style={[styles.platformIcon, { backgroundColor: config.color }]}>
              <Icon name={getPlatformIcon(account.platform)} size={24} color="#fff" />
            </View>
            <View style={styles.accountDetails}>
              <Text style={[styles.platformName, { color: theme.colors.text }]}>
                {config.name}
              </Text>
              {account.connected ? (
                <>
                  <Text style={[styles.accountUsername, { color: theme.colors.textSecondary }]}>
                    @{account.username}
                  </Text>
                  <View style={styles.statusContainer}>
                    <View style={[styles.statusDot, styles.connectedDot]} />
                    <Text style={[styles.statusText, styles.connectedText]}>
                      Connected
                    </Text>
                  </View>
                </>
              ) : (
                <View style={styles.statusContainer}>
                  <View style={[styles.statusDot, { backgroundColor: theme.colors.textSecondary }]} />
                  <Text style={[styles.statusText, { color: theme.colors.textSecondary }]}>
                    Not Connected
                  </Text>
                </View>
              )}
            </View>
          </View>
          
          <View style={styles.accountActions}>
            {account.connected ? (
              <>
                <TouchableOpacity
                  style={[styles.actionButton, styles.testButton, { borderColor: theme.colors.border }]}
                  onPress={() => handleTestConnection(account.platform)}
                >
                  <Icon name="sync" size={16} color={theme.colors.primary} />
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.actionButton, styles.disconnectButton]}
                  onPress={() => handleDisconnect(account.platform)}
                >
                  <Text style={[styles.actionButtonText, styles.errorText]}>
                    Disconnect
                  </Text>
                </TouchableOpacity>
              </>
            ) : (
              <TouchableOpacity
                style={[styles.actionButton, styles.connectButton, { backgroundColor: config.color }]}
                onPress={() => handleConnect(account.platform)}
              >
                <Text style={[styles.actionButtonText, styles.whiteText]}>
                  Connect
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
        
        {account.connected && account.lastSync && (
          <View style={styles.accountFooter}>
            <Text style={[styles.lastSync, { color: theme.colors.textSecondary }]}>
              Last synced: {new Date(account.lastSync).toLocaleString()}
            </Text>
          </View>
        )}
      </View>
    );
  };

  const connectedCount = accounts.filter(account => account.connected).length;

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <View style={[styles.header, { backgroundColor: theme.colors.surface }]}>
        <Text style={[styles.title, { color: theme.colors.text }]}>
          Social Accounts
        </Text>
        <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
          Connect your social media accounts to start managing them
        </Text>
        
        <View style={styles.summaryCard}>
          <View style={styles.summaryItem}>
            <Text style={[styles.summaryNumber, { color: theme.colors.primary }]}>
              {connectedCount}
            </Text>
            <Text style={[styles.summaryLabel, { color: theme.colors.textSecondary }]}>
              Connected
            </Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={[styles.summaryNumber, { color: theme.colors.textSecondary }]}>
              {accounts.length - connectedCount}
            </Text>
            <Text style={[styles.summaryLabel, { color: theme.colors.textSecondary }]}>
              Available
            </Text>
          </View>
        </View>
      </View>

      <ScrollView 
        style={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={refreshAccounts}
            colors={[theme.colors.primary]}
            tintColor={theme.colors.primary}
          />
        }
      >
        <View style={styles.accountsList}>
          {accounts.map(renderAccountCard)}
        </View>
        
        <View style={styles.helpSection}>
          <Text style={[styles.helpTitle, { color: theme.colors.text }]}>
            Need Help?
          </Text>
          <Text style={[styles.helpText, { color: theme.colors.textSecondary }]}>
            Having trouble connecting your accounts? Check our setup guide or contact support.
          </Text>
          <TouchableOpacity style={[styles.helpButton, { borderColor: theme.colors.border }]}>
            <Icon name="help-outline" size={20} color={theme.colors.primary} />
            <Text style={[styles.helpButtonText, { color: theme.colors.primary }]}>
              Setup Guide
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {isLoading && (
        <View style={styles.loadingOverlay}>
          <View style={[styles.loadingContainer, { backgroundColor: theme.colors.surface }]}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={[styles.loadingText, { color: theme.colors.text }]}>
              Connecting...
            </Text>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 16,
    borderBottomWidth: 0.5,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 16,
  },
  summaryCard: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    paddingHorizontal: 8,
    borderRadius: 12,
    backgroundColor: '#f9fafb',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  summaryLabel: {
    fontSize: 12,
  },
  content: {
    flex: 1,
  },
  accountsList: {
    padding: 16,
  },
  accountCard: {
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  accountHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  accountInfo: {
    flexDirection: 'row',
    flex: 1,
  },
  platformIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  accountDetails: {
    flex: 1,
    justifyContent: 'center',
  },
  platformName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  accountUsername: {
    fontSize: 14,
    marginBottom: 4,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
  },
  accountActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  connectButton: {
    borderWidth: 0,
  },
  disconnectButton: {
    borderColor: '#ef4444',
  },
  testButton: {
    width: 32,
    height: 32,
    paddingHorizontal: 0,
    paddingVertical: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionButtonText: {
    fontSize: 12,
    fontWeight: '600',
  },
  accountFooter: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 0.5,
    borderTopColor: '#f3f4f6',
  },
  lastSync: {
    fontSize: 12,
  },
  helpSection: {
    margin: 16,
    padding: 16,
    borderRadius: 12,
    backgroundColor: '#f9fafb',
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  helpText: {
    fontSize: 14,
    marginBottom: 12,
    lineHeight: 20,
  },
  helpButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    borderWidth: 1,
    alignSelf: 'flex-start',
    gap: 6,
  },
  helpButtonText: {
    fontSize: 14,
    fontWeight: '500',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    gap: 12,
  },
  loadingText: {
    fontSize: 16,
    fontWeight: '500',
  },
  connectedDot: {
    backgroundColor: '#10b981',
  },
  connectedText: {
    color: '#10b981',
  },
  errorText: {
    color: '#ef4444',
  },
  whiteText: {
    color: '#fff',
  },
});
