/**
 * Main navigation configuration for Social Media Management Bot
 */

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Import screens
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import DashboardScreen from '../screens/main/DashboardScreen';
import CalendarScreen from '../screens/main/CalendarScreen';
import CreatePostScreen from '../screens/main/CreatePostScreen';
import AnalyticsScreen from '../screens/main/AnalyticsScreen';
import ProfileScreen from '../screens/main/ProfileScreen';
import SocialAccountsScreen from '../screens/main/SocialAccountsScreen';
import SettingsScreen from '../screens/main/SettingsScreen';

import { RootStackParamList, MainTabParamList } from '../types';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../contexts/ThemeContext';

const RootStack = createStackNavigator<RootStackParamList>();
const MainTab = createBottomTabNavigator<MainTabParamList>();

// Main Tab Navigator
function MainTabNavigator() {
  const { theme } = useTheme();

  return (
    <MainTab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopWidth: 1,
          borderTopColor: theme.colors.border,
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
        tabBarIcon: ({ color, size }) => {
          let iconName = '';

          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Calendar':
              iconName = 'event';
              break;
            case 'Create':
              iconName = 'add-circle';
              break;
            case 'Analytics':
              iconName = 'analytics';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
      })}
    >
      <MainTab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
        }}
      />
      <MainTab.Screen 
        name="Calendar" 
        component={CalendarScreen}
        options={{
          tabBarLabel: 'Calendar',
        }}
      />
      <MainTab.Screen 
        name="Create" 
        component={CreatePostScreen}
        options={{
          tabBarLabel: 'Create',
        }}
      />
      <MainTab.Screen 
        name="Analytics" 
        component={AnalyticsScreen}
        options={{
          tabBarLabel: 'Analytics',
        }}
      />
      <MainTab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',
        }}
      />
    </MainTab.Navigator>
  );
}

// Auth Stack Navigator
function AuthStackNavigator() {
  const { theme } = useTheme();

  return (
    <RootStack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: theme.colors.background },
      }}
    >
      <RootStack.Screen name="Login" component={LoginScreen} />
      <RootStack.Screen name="Register" component={RegisterScreen} />
    </RootStack.Navigator>
  );
}

// Main App Navigator
function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();
  const { theme, isDark } = useTheme();

  // TODO: Add loading screen
  if (isLoading) {
    return null;
  }

  return (
    <NavigationContainer
      theme={{
        dark: isDark,
        colors: {
          primary: theme.colors.primary,
          background: theme.colors.background,
          card: theme.colors.surface,
          text: theme.colors.text,
          border: theme.colors.border,
          notification: theme.colors.primary,
        },
      }}
    >
      <StatusBar barStyle={isDark ? 'light-content' : 'dark-content'} backgroundColor={theme.colors.background} />
      {isAuthenticated ? (
        <RootStack.Navigator 
          screenOptions={{ 
            headerShown: false,
            cardStyle: { backgroundColor: theme.colors.background },
          }}
        >
          <RootStack.Screen name="Main" component={MainTabNavigator} />
          <RootStack.Screen 
            name="SocialAccounts" 
            component={SocialAccountsScreen}
            options={{ 
              headerShown: true, 
              title: 'Social Accounts',
              headerStyle: { backgroundColor: theme.colors.surface },
              headerTintColor: theme.colors.text,
            }}
          />
          <RootStack.Screen 
            name="Settings" 
            component={SettingsScreen}
            options={{ 
              headerShown: true, 
              title: 'Settings',
              headerStyle: { backgroundColor: theme.colors.surface },
              headerTintColor: theme.colors.text,
            }}
          />
        </RootStack.Navigator>
      ) : (
        <AuthStackNavigator />
      )}
    </NavigationContainer>
  );
}

export default AppNavigator;