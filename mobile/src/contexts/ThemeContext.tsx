/**
 * Theme Context for Dark/Light mode support
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useColorScheme } from 'react-native';
import { MMKV } from 'react-native-mmkv';

export type ThemeMode = 'light' | 'dark' | 'auto';

interface Colors {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  background: string;
  surface: string;
  card: string;
  text: string;
  textSecondary: string;
  border: string;
  error: string;
  success: string;
  warning: string;
  info: string;
}

export interface Theme {
  mode: 'light' | 'dark';
  colors: Colors;
}

interface ThemeContextType {
  theme: Theme;
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  isDark: boolean;
}

const storage = new MMKV();

const lightTheme: Theme = {
  mode: 'light',
  colors: {
    primary: '#3b82f6',
    primaryLight: '#60a5fa',
    primaryDark: '#2563eb',
    background: '#f9fafb',
    surface: '#ffffff',
    card: '#ffffff',
    text: '#1f2937',
    textSecondary: '#6b7280',
    border: '#e5e7eb',
    error: '#ef4444',
    success: '#10b981',
    warning: '#f59e0b',
    info: '#3b82f6',
  },
};

const darkTheme: Theme = {
  mode: 'dark',
  colors: {
    primary: '#60a5fa',
    primaryLight: '#93c5fd',
    primaryDark: '#3b82f6',
    background: '#111827',
    surface: '#1f2937',
    card: '#374151',
    text: '#f9fafb',
    textSecondary: '#d1d5db',
    border: '#4b5563',
    error: '#f87171',
    success: '#34d399',
    warning: '#fbbf24',
    info: '#60a5fa',
  },
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const systemColorScheme = useColorScheme();
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    const savedMode = storage.getString('theme_mode') as ThemeMode;
    return savedMode || 'auto';
  });

  const isDark = themeMode === 'dark' || (themeMode === 'auto' && systemColorScheme === 'dark');
  const theme = isDark ? darkTheme : lightTheme;

  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode);
    storage.set('theme_mode', mode);
  };

  useEffect(() => {
    // Listen for system theme changes when in auto mode
    if (themeMode === 'auto') {
      // Theme will automatically update based on systemColorScheme
    }
  }, [systemColorScheme, themeMode]);

  const value: ThemeContextType = {
    theme,
    themeMode,
    setThemeMode,
    isDark,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

export { lightTheme, darkTheme };