module.exports = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko', 'ar'],
    localeDetection: false,
  },
  fallbackLng: 'en',
  debug: process.env.NODE_ENV === 'development',
  
  serializeConfig: false,
  strictMode: true,
  
  interpolation: {
    escapeValue: false,
  },
  
  // Support for RTL languages
  rtl: ['ar'],
  
  // Namespace separation
  defaultNS: 'common',
  ns: ['common', 'auth', 'dashboard', 'content', 'analytics', 'settings'],
  
  // Load translations from public folder
  localePath: typeof window === 'undefined' ? 'public/locales' : '/locales',
  
  // Don't load missing translations
  appendNamespaceToMissingKey: false,
  saveMissing: false,
};