/**

 * Push Notification Service
 * Handles Firebase Cloud Messaging integration
 */

import messaging, { FirebaseMessagingTypes } from '@react-native-firebase/messaging';
import { Platform, PermissionsAndroid, Alert } from 'react-native';
import { MMKV } from 'react-native-mmkv';
import apiClient from '../api';

export interface NotificationData {
  id: string;
  title: string;
  body: string;
  data?: Record<string, any>;
  timestamp: number;
  read: boolean;
}

class PushNotificationService {
  private storage = new MMKV();
  private fcmToken: string | null = null;

  /**
   * Initialize push notifications
   */
  async initialize(): Promise<void> {
    try {
      // Request permission
      const authStatus = await this.requestPermission();
      
      if (authStatus === messaging.AuthorizationStatus.AUTHORIZED || 
          authStatus === messaging.AuthorizationStatus.PROVISIONAL) {
        
        // Get FCM token
        await this.getFCMToken();
        
        // Set up message handlers
        this.setupMessageHandlers();
        
        // Handle background app state
        await this.handleBackgroundMessage();
        
        console.log('Push notifications initialized successfully');
      } else {
        console.log('Push notification permission denied');
      }
    } catch (error) {
      console.error('Failed to initialize push notifications:', error);
    }
  }

  /**
   * Request notification permission
   */
  private async requestPermission(): Promise<messaging.AuthorizationStatus> {
    if (Platform.OS === 'android') {
      // Request Android notification permission for API level 33+
      if (Platform.Version >= 33) {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS
        );
        
        if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
          return messaging.AuthorizationStatus.DENIED;
        }
      }
    }

    const authStatus = await messaging().requestPermission({
      sound: true,
      announcement: true,
      carPlay: true,
      criticalAlert: true,
    });

    return authStatus;
  }

  /**
   * Get FCM token and register with backend
   */
  private async getFCMToken(): Promise<string | null> {
    try {
      // Check if token exists and is valid
      const existingToken = this.storage.getString('fcm_token');
      
      if (existingToken) {
        this.fcmToken = existingToken;
      } else {
        // Get new token
        const token = await messaging().getToken();
        this.fcmToken = token;
        this.storage.set('fcm_token', token);
      }

      // Register token with backend
      if (this.fcmToken) {
        await this.registerTokenWithBackend(this.fcmToken);
      }

      // Listen for token refresh
      messaging().onTokenRefresh(async (token) => {
        this.fcmToken = token;
        this.storage.set('fcm_token', token);
        await this.registerTokenWithBackend(token);
      });

      return this.fcmToken;
    } catch (error) {
      console.error('Failed to get FCM token:', error);
      return null;
    }
  }

  /**
   * Register FCM token with backend
   */
  private async registerTokenWithBackend(token: string): Promise<void> {
    try {
      await apiClient.post('/notifications/register-token', {
        token,
        platform: Platform.OS,
      });
      console.log('FCM token registered with backend');
    } catch (error) {
      console.error('Failed to register FCM token with backend:', error);
    }
  }

  /**
   * Set up message handlers
   */
  private setupMessageHandlers(): void {
    // Handle foreground messages
    messaging().onMessage(async (remoteMessage) => {
      console.log('Foreground message received:', remoteMessage);
      this.handleIncomingMessage(remoteMessage);
      this.showInAppNotification(remoteMessage);
    });

    // Handle notification opened app
    messaging().onNotificationOpenedApp((remoteMessage) => {
      console.log('Notification caused app to open:', remoteMessage);
      this.handleNotificationOpen(remoteMessage);
    });

    // Check if app was opened from a notification (app was completely closed)
    messaging().getInitialNotification().then((remoteMessage) => {
      if (remoteMessage) {
        console.log('App opened from notification (closed state):', remoteMessage);
        this.handleNotificationOpen(remoteMessage);
      }
    });
  }

  /**
   * Handle background messages
   */
  private async handleBackgroundMessage(): Promise<void> {
    messaging().setBackgroundMessageHandler(async (remoteMessage) => {
      console.log('Background message received:', remoteMessage);
      this.handleIncomingMessage(remoteMessage);
    });
  }

  /**
   * Handle incoming message and store locally
   */
  private handleIncomingMessage(remoteMessage: FirebaseMessagingTypes.RemoteMessage): void {
    if (!remoteMessage.notification) return;

    const notification: NotificationData = {
      id: remoteMessage.messageId || Date.now().toString(),
      title: remoteMessage.notification.title || 'Social Media Bot',
      body: remoteMessage.notification.body || '',
      data: remoteMessage.data,
      timestamp: Date.now(),
      read: false,
    };

    // Store notification locally
    this.storeNotification(notification);
  }

  /**
   * Store notification in local storage
   */
  private storeNotification(notification: NotificationData): void {
    try {
      const notifications = this.getStoredNotifications();
      notifications.unshift(notification);
      
      // Keep only last 50 notifications
      const trimmedNotifications = notifications.slice(0, 50);
      
      this.storage.set('notifications', JSON.stringify(trimmedNotifications));
    } catch (error) {
      console.error('Failed to store notification:', error);
    }
  }

  /**
   * Get stored notifications
   */
  getStoredNotifications(): NotificationData[] {
    try {
      const stored = this.storage.getString('notifications');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to get stored notifications:', error);
      return [];
    }
  }

  /**
   * Mark notification as read
   */
  markAsRead(notificationId: string): void {
    try {
      const notifications = this.getStoredNotifications();
      const updated = notifications.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      );
      this.storage.set('notifications', JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  }

  /**
   * Clear all notifications
   */
  clearAllNotifications(): void {
    try {
      this.storage.delete('notifications');
    } catch (error) {
      console.error('Failed to clear notifications:', error);
    }
  }

  /**
   * Show in-app notification for foreground messages
   */
  private showInAppNotification(remoteMessage: FirebaseMessagingTypes.RemoteMessage): void {
    if (remoteMessage.notification) {
      Alert.alert(
        remoteMessage.notification.title || 'Social Media Bot',
        remoteMessage.notification.body || '',
        [
          {
            text: 'Dismiss',
            style: 'cancel',
          },
          {
            text: 'View',
            onPress: () => this.handleNotificationOpen(remoteMessage),
          },
        ]
      );
    }
  }

  /**
   * Handle notification tap/open
   */
  private handleNotificationOpen(remoteMessage: FirebaseMessagingTypes.RemoteMessage): void {
    const { data } = remoteMessage;
    
    if (data?.screen) {
      // Navigate to specific screen based on notification data
      // This will be handled by the navigation system
      console.log('Should navigate to:', data.screen);
    }
  }

  /**
   * Subscribe to topic
   */
  async subscribeToTopic(topic: string): Promise<void> {
    try {
      await messaging().subscribeToTopic(topic);
      console.log(`Subscribed to topic: ${topic}`);
    } catch (error) {
      console.error(`Failed to subscribe to topic ${topic}:`, error);
    }
  }

  /**
   * Unsubscribe from topic
   */
  async unsubscribeFromTopic(topic: string): Promise<void> {
    try {
      await messaging().unsubscribeFromTopic(topic);
      console.log(`Unsubscribed from topic: ${topic}`);
    } catch (error) {
      console.error(`Failed to unsubscribe from topic ${topic}:`, error);
    }
  }

  /**
   * Get notification badge count
   */
  getUnreadCount(): number {
    const notifications = this.getStoredNotifications();
    return notifications.filter(notif => !notif.read).length;
  }

  /**
   * Get current FCM token
   */
  getCurrentToken(): string | null {
    return this.fcmToken;
  }
}

// Export singleton instance
export const pushNotificationService = new PushNotificationService();
export default pushNotificationService;

 * Push Notification Service for Social Media Management Bot
 */

import { Platform } from 'react-native';
import { PostStatus } from '../types/post';

interface NotificationData {
  title: string;
  body: string;
  data?: any;
}

class PushNotificationService {
  private static instance: PushNotificationService;

  public static getInstance(): PushNotificationService {
    if (!PushNotificationService.instance) {
      PushNotificationService.instance = new PushNotificationService();
    }
    return PushNotificationService.instance;
  }

  async initialize(): Promise<void> {
    try {
      console.log('Initializing push notifications for platform:', Platform.OS);
    } catch (error) {
      console.error('Error initializing push notifications:', error);
    }
  }

  async scheduleNotification(notification: NotificationData, _delay: number): Promise<void> {
    try {
      console.log('Scheduling notification:', notification.title);
    } catch (error) {
      console.error('Error scheduling notification:', error);
    }
  }

  async sendPostStatusNotification(status: PostStatus): Promise<void> {
    try {
      const notification: NotificationData = {
        title: 'Post Update',
        body: `Your post status changed to: ${status}`,
        data: { status }
      };
      
      await this.scheduleNotification(notification, 0);
    } catch (error) {
      console.error('Error sending post status notification:', error);
    }
  }

  async requestPermissions(): Promise<boolean> {
    return true;
  }
}

export const pushNotificationService = PushNotificationService.getInstance();

