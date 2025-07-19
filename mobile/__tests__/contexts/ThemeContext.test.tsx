/**
 * Theme Context Tests
 * Tests for dark/light theme functionality
 */

import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { useColorScheme } from 'react-native';
import { ThemeProvider, useTheme } from '../../../src/contexts/ThemeContext';
import { MMKV } from 'react-native-mmkv';
import { Text, TouchableOpacity } from 'react-native';

// Mock dependencies
jest.mock('react-native', () => ({
  ...jest.requireActual('react-native'),
  useColorScheme: jest.fn(),
}));

jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    set: jest.fn(),
  })),
}));

// Test component that uses theme
const TestComponent = () => {
  const { theme, themeMode, setThemeMode, isDark } = useTheme();
  
  return (
    <>
      <Text testID="theme-mode">{themeMode}</Text>
      <Text testID="is-dark">{isDark.toString()}</Text>
      <Text testID="background-color">{theme.colors.background}</Text>
      <TouchableOpacity testID="toggle-dark" onPress={() => setThemeMode('dark')}>
        <Text>Dark</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="toggle-light" onPress={() => setThemeMode('light')}>
        <Text>Light</Text>
      </TouchableOpacity>
      <TouchableOpacity testID="toggle-auto" onPress={() => setThemeMode('auto')}>
        <Text>Auto</Text>
      </TouchableOpacity>
    </>
  );
};

describe('ThemeContext', () => {
  let mockStorage: any;

  beforeEach(() => {
    jest.clearAllMocks();
    mockStorage = {
      getString: jest.fn(),
      set: jest.fn(),
    };
    (MMKV as jest.Mock).mockImplementation(() => mockStorage);
    (useColorScheme as jest.Mock).mockReturnValue('light');
  });

  it('should provide light theme by default', () => {
    mockStorage.getString.mockReturnValue(null);
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(getByTestId('theme-mode').props.children).toBe('auto');
    expect(getByTestId('is-dark').props.children).toBe('false');
    expect(getByTestId('background-color').props.children).toBe('#f9fafb');
  });

  it('should use stored theme preference', () => {
    mockStorage.getString.mockReturnValue('dark');
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(getByTestId('theme-mode').props.children).toBe('dark');
    expect(getByTestId('is-dark').props.children).toBe('true');
  });

  it('should switch to dark theme when selected', () => {
    mockStorage.getString.mockReturnValue(null);
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.press(getByTestId('toggle-dark'));

    expect(getByTestId('theme-mode').props.children).toBe('dark');
    expect(getByTestId('is-dark').props.children).toBe('true');
    expect(mockStorage.set).toHaveBeenCalledWith('theme_mode', 'dark');
  });

  it('should switch to light theme when selected', () => {
    mockStorage.getString.mockReturnValue('dark');
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.press(getByTestId('toggle-light'));

    expect(getByTestId('theme-mode').props.children).toBe('light');
    expect(getByTestId('is-dark').props.children).toBe('false');
    expect(mockStorage.set).toHaveBeenCalledWith('theme_mode', 'light');
  });

  it('should follow system theme in auto mode', () => {
    (useColorScheme as jest.Mock).mockReturnValue('dark');
    mockStorage.getString.mockReturnValue('auto');
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(getByTestId('theme-mode').props.children).toBe('auto');
    expect(getByTestId('is-dark').props.children).toBe('true');
  });

  it('should provide correct dark theme colors', () => {
    mockStorage.getString.mockReturnValue('dark');
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(getByTestId('background-color').props.children).toBe('#111827');
  });

  it('should provide correct light theme colors', () => {
    mockStorage.getString.mockReturnValue('light');
    
    const { getByTestId } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(getByTestId('background-color').props.children).toBe('#f9fafb');
  });

  it('should throw error when used outside provider', () => {
    // Mock console.error to avoid noise in test output
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    expect(() => {
      render(<TestComponent />);
    }).toThrow('useTheme must be used within a ThemeProvider');
    
    consoleSpy.mockRestore();
  });
});