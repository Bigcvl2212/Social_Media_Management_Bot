# Mobile App Development Guide

This guide covers the development setup, architecture, and contribution guidelines for the Social Media Management Bot mobile application.

## Architecture Overview

### Tech Stack
- **Framework**: React Native 0.80.1
- **Language**: TypeScript
- **Navigation**: React Navigation 7.x
- **State Management**: React Query (TanStack Query)
- **Styling**: StyleSheet (React Native)
- **Storage**: MMKV (for secure local storage)
- **Notifications**: Firebase Cloud Messaging
- **Internationalization**: react-i18next

### Project Structure

```
mobile/
├── src/
│   ├── components/           # Reusable UI components
│   ├── contexts/            # React contexts (Theme, Auth)
│   ├── hooks/               # Custom React hooks
│   ├── i18n/                # Internationalization files
│   ├── navigation/          # Navigation configuration
│   ├── screens/             # Screen components
│   │   ├── auth/           # Authentication screens
│   │   └── main/           # Main app screens
│   ├── services/           # API and external services
│   └── types/              # TypeScript type definitions
├── android/                # Android-specific files
├── ios/                    # iOS-specific files
├── scripts/                # Build and deployment scripts
└── __tests__/              # Test files
```

### Key Features

#### 1. Theme System
- **Light/Dark Mode**: Automatic system detection with manual override
- **Persistent Preferences**: Theme choice saved using MMKV
- **Consistent Colors**: Centralized color scheme across all components

```typescript
// Usage example
const { theme, isDark, setThemeMode } = useTheme();

<View style={[styles.container, { backgroundColor: theme.colors.background }]}>
  <Text style={{ color: theme.colors.text }}>Hello World</Text>
</View>
```

#### 2. OAuth Integration
- **Multi-Platform Support**: Instagram, Facebook, Twitter, LinkedIn, YouTube, TikTok
- **Secure Storage**: Credentials stored securely with MMKV
- **Token Management**: Automatic refresh and expiration handling
- **Deep Link Handling**: OAuth callbacks via custom URL schemes

```typescript
// Usage example
import oauthService from '../services/oauthService';

// Start OAuth flow
await oauthService.startOAuthFlow('instagram');

// Check connection status
const isConnected = oauthService.isConnected('instagram');

// Get stored credentials
const credentials = oauthService.getStoredCredentials('instagram');
```

#### 3. Offline Content Management
- **Draft Storage**: Save posts offline for later publishing
- **Sync Mechanism**: Automatic sync when connection is restored
- **Conflict Resolution**: Handle conflicts between local and remote data

```typescript
// Usage example
import offlineStorageService from '../services/offlineStorageService';

// Save draft offline
const draftId = offlineStorageService.saveDraftOffline({
  title: "My Post",
  content: "Post content",
  platforms: ['instagram', 'facebook']
});

// Sync drafts when online
await offlineStorageService.syncDrafts();
```

#### 4. Push Notifications
- **Firebase Integration**: FCM for cross-platform notifications
- **Permission Management**: Proper permission handling for iOS/Android
- **Deep Linking**: Navigate to specific screens from notifications

```typescript
// Usage example
import pushNotificationService from '../services/pushNotificationService';

// Initialize notifications
await pushNotificationService.initialize();

// Subscribe to topics
await pushNotificationService.subscribeToTopic('post_updates');
```

#### 5. Internationalization
- **Multi-Language Support**: 10 languages included
- **RTL Support**: Right-to-left language preparation
- **Persistent Language**: User language preference saved

```typescript
// Usage example
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

<Text>{t('dashboard.welcome')}</Text>

// Change language
await i18n.changeLanguage('es');
```

## Development Setup

### Prerequisites
- Node.js 18+
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Bigcvl2212/Social_Media_Management_Bot.git
cd Social_Media_Management_Bot/mobile
```

2. **Install dependencies**:
```bash
npm install
```

3. **iOS Setup** (macOS only):
```bash
cd ios && pod install && cd ..
```

4. **Environment Configuration**:
```bash
cp .env.development .env
# Edit .env with your configuration
```

5. **Start Metro bundler**:
```bash
npm start
```

6. **Run on device/simulator**:
```bash
# iOS
npm run ios

# Android
npm run android
```

## Code Style and Standards

### TypeScript Configuration

The project uses strict TypeScript configuration with the following key settings:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### ESLint and Prettier

Code formatting is enforced with ESLint and Prettier:

```bash
# Run linter
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Format code
npm run format
```

### Component Structure

Follow this pattern for new components:

```typescript
/**
 * Component Description
 * Brief description of what this component does
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

interface ComponentProps {
  title: string;
  onPress?: () => void;
}

export default function Component({ title, onPress }: ComponentProps) {
  const { theme } = useTheme();

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.surface }]}>
      <Text style={[styles.title, { color: theme.colors.text }]}>
        {title}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
  },
});
```

### State Management Patterns

#### React Query for Server State

```typescript
// Custom hook for fetching data
function useAnalytics(period: string) {
  return useQuery({
    queryKey: ['analytics', period],
    queryFn: () => fetchAnalytics(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Mutation for creating content
function useCreatePost() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
}
```

#### Context for Global UI State

```typescript
// Theme context usage
const { theme, isDark, setThemeMode } = useTheme();

// Auth context usage
const { user, login, logout, isAuthenticated } = useAuth();
```

## Testing Strategy

### Unit Tests
- **Services**: Test all business logic in services
- **Hooks**: Test custom React hooks
- **Utilities**: Test utility functions

```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage
```

### Integration Tests
- **Screen Flows**: Test complete user journeys
- **API Integration**: Test service integrations
- **Navigation**: Test navigation flows

### Example Test Structure

```typescript
describe('OAuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should store credentials securely', () => {
    const credentials = { accessToken: 'token', ... };
    oauthService.storeCredentials('instagram', credentials);
    
    expect(mockStorage.set).toHaveBeenCalledWith(
      'oauth_instagram',
      JSON.stringify(credentials)
    );
  });
});
```

## Performance Optimization

### Bundle Size Optimization
- **Metro Configuration**: Optimized for production builds
- **Tree Shaking**: Unused code elimination
- **Image Optimization**: Proper image sizing and formats

### Memory Management
- **Query Cleanup**: Proper React Query garbage collection
- **Image Caching**: Efficient image loading and caching
- **Component Optimization**: React.memo for expensive components

### Network Optimization
- **Request Batching**: Combine API requests where possible
- **Caching Strategy**: Implement proper caching layers
- **Offline Support**: Graceful offline experience

## Security Considerations

### Data Protection
- **Secure Storage**: MMKV for sensitive data
- **Token Security**: Proper OAuth token handling
- **SSL Pinning**: Certificate validation for production

### API Security
- **Request Signing**: Sign requests to prevent tampering
- **Rate Limiting**: Implement client-side rate limiting
- **Error Handling**: Don't expose sensitive errors to users

### Privacy
- **Data Minimization**: Only collect necessary data
- **Permission Requests**: Clear justification for permissions
- **Analytics Opt-out**: Allow users to disable analytics

## Debugging and Development Tools

### React Native Debugger
- **Redux DevTools**: For state inspection
- **Network Inspector**: Monitor API calls
- **Performance Monitor**: Track render performance

### Flipper Integration
- **Network Plugin**: Debug network requests
- **Layout Inspector**: Examine component hierarchy
- **Crash Reporter**: Debug crashes and errors

### Useful Commands

```bash
# Reset Metro cache
npx react-native start --reset-cache

# Clean builds
npm run clean

# Generate APK for testing
cd android && ./gradlew assembleDebug

# iOS debugging build
npx react-native run-ios --configuration Debug
```

## Contributing Guidelines

### Branch Naming
- `feature/feature-name` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes

### Commit Messages
Follow conventional commits:
```
feat: add OAuth integration for TikTok
fix: resolve theme switching bug on Android
docs: update deployment guide
```

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite
4. Update documentation if needed
5. Submit PR with detailed description
6. Address review comments
7. Merge after approval

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No console logs or debug code
- [ ] Performance impact considered
- [ ] Accessibility guidelines followed
- [ ] Error handling implemented

## Troubleshooting Common Issues

### Build Issues
```bash
# Android build failure
cd android && ./gradlew clean && cd .. && npm start -- --reset-cache

# iOS build failure
cd ios && pod deintegrate && pod install && cd ..
```

### Development Server Issues
```bash
# Port already in use
npx react-native start --port 8082

# Metro bundler issues
rm -rf node_modules && npm install && npm start -- --reset-cache
```

### Device Connection Issues
```bash
# Android device not detected
adb devices
adb kill-server && adb start-server

# iOS simulator issues
xcrun simctl list devices
```

## Resources and Documentation

- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [React Navigation Documentation](https://reactnavigation.org/)
- [Firebase React Native Documentation](https://rnfirebase.io/)

For project-specific questions, check the main repository documentation or reach out to the development team.