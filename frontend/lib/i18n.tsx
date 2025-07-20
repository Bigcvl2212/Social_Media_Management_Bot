/**
 * i18n Provider and Hooks for Frontend
 * Provides internationalization support for the Social Media Management Bot frontend
 */

import { createContext, useContext, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useRouter } from 'next/router';

// Available languages configuration
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

// RTL languages
export const RTL_LANGUAGES = ['ar'];

// Language context
interface LanguageContextType {
  currentLanguage: string;
  changeLanguage: (languageCode: string) => void;
  isRtl: boolean;
  availableLanguages: typeof AVAILABLE_LANGUAGES;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Language provider component
export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { i18n } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState('en');

  useEffect(() => {
    // Initialize language from router locale
    if (router.locale && i18n.language !== router.locale) {
      i18n.changeLanguage(router.locale);
      setCurrentLanguage(router.locale);
    }
  }, [router.locale, i18n]);

  const changeLanguage = async (languageCode: string) => {
    // Save to localStorage
    localStorage.setItem('preferred-language', languageCode);
    
    // Change i18n language
    await i18n.changeLanguage(languageCode);
    setCurrentLanguage(languageCode);
    
    // Navigate to new locale route
    router.push(router.pathname, router.asPath, { locale: languageCode });
  };

  const isRtl = RTL_LANGUAGES.includes(currentLanguage);

  return (
    <LanguageContext.Provider
      value={{
        currentLanguage,
        changeLanguage,
        isRtl,
        availableLanguages: AVAILABLE_LANGUAGES,
      }}
    >
      <div dir={isRtl ? 'rtl' : 'ltr'}>
        {children}
      </div>
    </LanguageContext.Provider>
  );
}

// Custom hook to use language context
export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// Custom hook for translations with namespace support
export function useI18n(namespace = 'common') {
  const { t, i18n } = useTranslation(namespace);
  const language = useLanguage();
  
  return {
    t,
    i18n,
    currentLanguage: language.currentLanguage,
    changeLanguage: language.changeLanguage,
    isRtl: language.isRtl,
    availableLanguages: language.availableLanguages,
  };
}