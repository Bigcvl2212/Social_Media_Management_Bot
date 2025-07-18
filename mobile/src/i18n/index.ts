/**
 * Internationalization (i18n) configuration
 * Supports multiple languages for the Social Media Management Bot
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { getLocales } from 'react-native-localize';
import { MMKV } from 'react-native-mmkv';

// Import translations
import en from './locales/en.json';
import es from './locales/es.json';
import fr from './locales/fr.json';
import de from './locales/de.json';
import it from './locales/it.json';
import pt from './locales/pt.json';
import zh from './locales/zh.json';
import ja from './locales/ja.json';
import ko from './locales/ko.json';
import ar from './locales/ar.json';

const storage = new MMKV();

// Get device language
const deviceLanguage = getLocales()[0]?.languageCode || 'en';

// Available languages
export const AVAILABLE_LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
  { code: 'pt', name: 'Português', flag: '🇵🇹' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦' },
];

// Resources
const resources = {
  en: { translation: en },
  es: { translation: es },
  fr: { translation: fr },
  de: { translation: de },
  it: { translation: it },
  pt: { translation: pt },
  zh: { translation: zh },
  ja: { translation: ja },
  ko: { translation: ko },
  ar: { translation: ar },
};

// Get saved language or fallback to device language
const getSavedLanguage = (): string => {
  const savedLang = storage.getString('app_language');
  if (savedLang && AVAILABLE_LANGUAGES.find(lang => lang.code === savedLang)) {
    return savedLang;
  }
  // Check if device language is supported
  if (AVAILABLE_LANGUAGES.find(lang => lang.code === deviceLanguage)) {
    return deviceLanguage;
  }
  return 'en'; // Default fallback
};

// Save language preference
export const saveLanguage = (languageCode: string) => {
  storage.set('app_language', languageCode);
  i18n.changeLanguage(languageCode);
};

// Initialize i18next
i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getSavedLanguage(),
    fallbackLng: 'en',
    debug: __DEV__,
    
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
    
    // React i18next options
    react: {
      useSuspense: false,
    },
    
    // Namespace
    defaultNS: 'translation',
    ns: ['translation'],
  });

export default i18n;