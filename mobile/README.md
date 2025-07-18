# Social Media Management Bot - Mobile App

React Native mobile application for managing social media accounts across multiple platforms.

## Features

### Authentication
- User registration and login
- JWT token-based authentication
- Secure token storage
- Automatic token refresh

### Core Functionality
- **Dashboard**: Overview of connected accounts and recent activity
- **Social Accounts**: Connect and manage multiple social media platforms
- **Content Calendar**: Schedule and manage posts (Coming Soon)
- **Create Post**: AI-powered content creation (Coming Soon)
- **Analytics**: Performance insights and reporting (Coming Soon)
- **Profile**: User account management

### Supported Platforms
- Instagram
- TikTok
- YouTube
- Twitter/X
- Facebook
- LinkedIn

## Technical Stack

- **Framework**: React Native 0.80.1
- **Language**: TypeScript
- **Navigation**: React Navigation v6
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Storage**: AsyncStorage
- **Authentication**: JWT with refresh tokens

## Project Structure

```
mobile/
├── src/
│   ├── components/          # Reusable UI components
│   ├── hooks/              # Custom React hooks
│   │   └── useAuth.tsx     # Authentication hook
│   ├── navigation/         # Navigation configuration
│   │   └── AppNavigator.tsx
│   ├── screens/           # Screen components
│   │   ├── auth/          # Authentication screens
│   │   └── main/          # Main app screens
│   ├── services/          # API and external services
│   │   ├── api.ts         # API client configuration
│   │   └── auth.ts        # Authentication service
│   ├── types/             # TypeScript type definitions
│   └── utils/             # Utility functions
├── android/               # Android-specific files
├── ios/                   # iOS-specific files
└── __tests__/            # Test files
```

## Setup Instructions

### Prerequisites
- Node.js 18+
- npm or yarn
- React Native development environment
- Android Studio (for Android development)
- Xcode (for iOS development - macOS only)

### Installation

1. **Navigate to mobile directory**:
   ```bash
   cd mobile
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Install iOS dependencies** (iOS only):
   ```bash
   cd ios && pod install && cd ..
   ```

### Running the App

1. **Start Metro bundler**:
   ```bash
   npm start
   ```

2. **Run on Android**:
   ```bash
   npm run android
   ```

3. **Run on iOS**:
   ```bash
   npm run ios
   ```

### Development Commands

- **Lint code**: `npm run lint`
- **Run tests**: `npm test`
- **Type check**: `npx tsc --noEmit`

## API Integration

The mobile app connects to the FastAPI backend at:
- **Development**: `http://localhost:8000/api/v1`
- **Production**: Configure in `src/services/api.ts`

### Authentication Flow
1. User logs in with email/password
2. Backend returns JWT access and refresh tokens
3. Tokens are stored securely in AsyncStorage
4. API requests include Authorization header
5. Automatic token refresh on expiration

### Supported Endpoints
- `/auth/login` - User authentication
- `/auth/register` - User registration
- `/auth/refresh` - Token refresh
- `/users/me` - User profile
- `/social-accounts` - Social media account management
- `/content` - Content management
- `/analytics` - Analytics data

## Testing

The app includes Jest testing setup with:
- AsyncStorage mocking
- React Navigation mocking
- React Native gesture handler mocking

Run tests with:
```bash
npm test
```

## Deployment

### Android
1. Generate signed APK:
   ```bash
   cd android && ./gradlew assembleRelease
   ```

2. Upload to Google Play Store

### iOS
1. Build for release in Xcode
2. Archive and upload to App Store Connect

## Next Steps

### Upcoming Features
- [ ] Push notifications
- [ ] Offline content drafting
- [ ] AI content generation
- [ ] Advanced analytics widgets
- [ ] Dark/light theme toggle
- [ ] Multi-language support

### Integration Tasks
- [ ] Complete social media platform OAuth flows
- [ ] Implement content scheduling
- [ ] Add media upload functionality
- [ ] Build analytics dashboard
- [ ] Set up push notification service