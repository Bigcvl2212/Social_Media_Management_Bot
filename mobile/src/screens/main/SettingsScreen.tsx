/**
 * Settings Screen for Social Media Management Bot
 * Provides app configuration options including theme and language
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  Modal,
  FlatList,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { useTheme, ThemeMode } from '../../contexts/ThemeContext';
import { AVAILABLE_LANGUAGES, saveLanguage } from '../../i18n';
import { useAuth } from '../../hooks/useAuth';
import offlineStorageService from '../../services/offlineStorageService';

interface SettingsSection {
  title: string;
  items: SettingsItem[];
}

interface SettingsItem {
  id: string;
  title: string;
  subtitle?: string;
  type: 'toggle' | 'selection' | 'action' | 'navigation';
  value?: boolean | string;
  onPress?: () => void;
  onToggle?: (value: boolean) => void;
}

export default function SettingsScreen() {
  const { t, i18n } = useTranslation();
  const { theme, themeMode, setThemeMode } = useTheme();
  const { user, logout } = useAuth();
  const [showLanguageModal, setShowLanguageModal] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [pushNotificationsEnabled, setPushNotificationsEnabled] = useState(true);

  const handleLanguageSelect = (languageCode: string) => {
    saveLanguage(languageCode);
    setShowLanguageModal(false);
  };

  const handleThemeSelect = (mode: ThemeMode) => {
    setThemeMode(mode);
    setShowThemeModal(false);
  };

  const handleLogout = () => {
    Alert.alert(
      t('settings.logout'),
      t('settings.logoutConfirm'),
      [
        { text: t('common.cancel'), style: 'cancel' },
        { text: t('settings.logout'), onPress: logout, style: 'destructive' },
      ]
    );
  };

  const handleSyncDrafts = async () => {
    try {
      const result = await offlineStorageService.forceSync();
      Alert.alert(
        t('common.success'),
        `Synced ${result.syncedCount} drafts. ${result.failedCount} failed.`
      );
    } catch (error) {
      Alert.alert(t('common.error'), 'Failed to sync drafts');
    }
  };

  const getCurrentLanguageName = () => {
    const currentLang = AVAILABLE_LANGUAGES.find(lang => lang.code === i18n.language);
    return currentLang ? `${currentLang.flag} ${currentLang.name}` : 'English';
  };

  const getThemeDisplayName = () => {
    switch (themeMode) {
      case 'light': return t('settings.themeLight');
      case 'dark': return t('settings.themeDark');
      case 'auto': return t('settings.themeAuto');
      default: return t('settings.themeAuto');
    }
  };

  const sections: SettingsSection[] = [
    {
      title: t('settings.general'),
      items: [
        {
          id: 'language',
          title: t('settings.language'),
          subtitle: getCurrentLanguageName(),
          type: 'selection',
          onPress: () => setShowLanguageModal(true),
        },
        {
          id: 'theme',
          title: t('settings.theme'),
          subtitle: getThemeDisplayName(),
          type: 'selection',
          onPress: () => setShowThemeModal(true),
        },
      ],
    },
    {
      title: t('settings.notifications'),
      items: [
        {
          id: 'push_notifications',
          title: t('settings.pushNotifications'),
          type: 'toggle',
          value: pushNotificationsEnabled,
          onToggle: setPushNotificationsEnabled,
        },
      ],
    },
    {
      title: 'Data & Sync',
      items: [
        {
          id: 'sync_drafts',
          title: 'Sync Offline Drafts',
          subtitle: `${offlineStorageService.getSyncStats().pendingDrafts} pending`,
          type: 'action',
          onPress: handleSyncDrafts,
        },
      ],
    },
    {
      title: 'Account',
      items: [
        {
          id: 'logout',
          title: t('settings.logout'),
          type: 'action',
          onPress: handleLogout,
        },
      ],
    },
  ];

  const renderSettingsItem = ({ item }: { item: SettingsItem }) => (
    <TouchableOpacity
      style={[styles.settingsItem, { borderBottomColor: theme.colors.border }]}
      onPress={item.onPress}
      disabled={item.type === 'toggle'}
    >
      <View style={styles.settingsItemContent}>
        <View style={styles.settingsItemText}>
          <Text style={[styles.settingsItemTitle, { color: theme.colors.text }]}>
            {item.title}
          </Text>
          {item.subtitle && (
            <Text style={[styles.settingsItemSubtitle, { color: theme.colors.textSecondary }]}>
              {item.subtitle}
            </Text>
          )}
        </View>
        {item.type === 'toggle' && item.onToggle && (
          <Switch
            value={item.value as boolean}
            onValueChange={item.onToggle}
            trackColor={{ false: theme.colors.border, true: theme.colors.primary }}
            thumbColor={theme.colors.surface}
          />
        )}
        {(item.type === 'selection' || item.type === 'action' || item.type === 'navigation') && (
          <Text style={[styles.chevron, { color: theme.colors.textSecondary }]}>›</Text>
        )}
      </View>
    </TouchableOpacity>
  );

  const renderSection = (section: SettingsSection, index: number) => (
    <View key={index} style={styles.section}>
      <Text style={[styles.sectionTitle, { color: theme.colors.textSecondary }]}>
        {section.title}
      </Text>
      <View style={[styles.sectionContent, { backgroundColor: theme.colors.surface }]}>
        {section.items.map((item, itemIndex) => (
          <View key={item.id}>
            {renderSettingsItem({ item })}
            {itemIndex < section.items.length - 1 && (
              <View style={[styles.separator, { backgroundColor: theme.colors.border }]} />
            )}
          </View>
        ))}
      </View>
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <ScrollView style={styles.scrollView}>
        {/* User Info */}
        <View style={[styles.userSection, { backgroundColor: theme.colors.surface }]}>
          <View style={styles.userInfo}>
            <Text style={[styles.userName, { color: theme.colors.text }]}>
              {user?.full_name || user?.username}
            </Text>
            <Text style={[styles.userEmail, { color: theme.colors.textSecondary }]}>
              {user?.email}
            </Text>
          </View>
        </View>

        {/* Settings Sections */}
        {sections.map((section, index) => renderSection(section, index))}
      </ScrollView>

      {/* Language Selection Modal */}
      <Modal
        visible={showLanguageModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowLanguageModal(false)}
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: theme.colors.border }]}>
            <TouchableOpacity onPress={() => setShowLanguageModal(false)}>
              <Text style={[styles.modalCancel, { color: theme.colors.primary }]}>
                {t('common.cancel')}
              </Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              {t('settings.language')}
            </Text>
            <View style={styles.modalSpacer} />
          </View>
          <FlatList
            data={AVAILABLE_LANGUAGES}
            keyExtractor={(item) => item.code}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[styles.languageItem, { borderBottomColor: theme.colors.border }]}
                onPress={() => handleLanguageSelect(item.code)}
              >
                <Text style={[styles.languageText, { color: theme.colors.text }]}>
                  {item.flag} {item.name}
                </Text>
                {i18n.language === item.code && (
                  <Text style={[styles.checkmark, { color: theme.colors.primary }]}>✓</Text>
                )}
              </TouchableOpacity>
            )}
          />
        </View>
      </Modal>

      {/* Theme Selection Modal */}
      <Modal
        visible={showThemeModal}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowThemeModal(false)}
      >
        <View style={[styles.modalContainer, { backgroundColor: theme.colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: theme.colors.border }]}>
            <TouchableOpacity onPress={() => setShowThemeModal(false)}>
              <Text style={[styles.modalCancel, { color: theme.colors.primary }]}>
                {t('common.cancel')}
              </Text>
            </TouchableOpacity>
            <Text style={[styles.modalTitle, { color: theme.colors.text }]}>
              {t('settings.theme')}
            </Text>
            <View style={styles.modalSpacer} />
          </View>
          <View style={styles.themeOptions}>
            {(['light', 'dark', 'auto'] as ThemeMode[]).map((mode) => (
              <TouchableOpacity
                key={mode}
                style={[styles.themeOption, { borderBottomColor: theme.colors.border }]}
                onPress={() => handleThemeSelect(mode)}
              >
                <Text style={[styles.themeText, { color: theme.colors.text }]}>
                  {mode === 'light' ? t('settings.themeLight') :
                   mode === 'dark' ? t('settings.themeDark') :
                   t('settings.themeAuto')}
                </Text>
                {themeMode === mode && (
                  <Text style={[styles.checkmark, { color: theme.colors.primary }]}>✓</Text>
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
  scrollView: {
    flex: 1,
  },
  userSection: {
    padding: 20,
    marginBottom: 20,
  },
  userInfo: {
    alignItems: 'center',
  },
  userName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 16,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    textTransform: 'uppercase',
    paddingHorizontal: 20,
    paddingBottom: 8,
  },
  sectionContent: {
    marginHorizontal: 20,
    borderRadius: 12,
  },
  settingsItem: {
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  settingsItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  settingsItemText: {
    flex: 1,
  },
  settingsItemTitle: {
    fontSize: 16,
    fontWeight: '500',
  },
  settingsItemSubtitle: {
    fontSize: 14,
    marginTop: 2,
  },
  chevron: {
    fontSize: 20,
    fontWeight: '300',
  },
  separator: {
    height: 0.5,
    marginLeft: 16,
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
  languageItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 0.5,
  },
  languageText: {
    fontSize: 16,
  },
  checkmark: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  themeOptions: {
    paddingTop: 20,
  },
  themeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 0.5,
  },
  themeText: {
    fontSize: 16,
  },
});