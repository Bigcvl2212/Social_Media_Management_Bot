# Mobile App Deployment Guide

This guide covers the complete deployment process for the Social Media Management Bot mobile application to both Android and iOS app stores.

## Prerequisites

### Development Environment
- **Node.js**: Version 18 or higher
- **React Native CLI**: Latest version
- **Android Studio**: For Android development
- **Xcode**: For iOS development (macOS only)
- **Java JDK**: Version 11 or higher for Android

### Accounts Required
- **Google Play Console**: For Android app distribution
- **Apple Developer Account**: For iOS app distribution
- **Firebase Account**: For push notifications
- **Social Media Platform Developer Accounts**: For OAuth integration

## Environment Configuration

### 1. Environment Variables

Copy the appropriate environment template:

```bash
# For production
cp .env.production .env

# For development
cp .env.development .env
```

Update the `.env` file with your actual values:

```bash
# API Configuration
API_BASE_URL=https://your-api-domain.com
FIREBASE_PROJECT_ID=your-firebase-project

# OAuth Credentials
FACEBOOK_APP_ID=your_facebook_app_id
INSTAGRAM_CLIENT_ID=your_instagram_client_id
TWITTER_CLIENT_ID=your_twitter_client_id
LINKEDIN_CLIENT_ID=your_linkedin_client_id
GOOGLE_CLIENT_ID=your_google_client_id
TIKTOK_CLIENT_ID=your_tiktok_client_id
```

### 2. Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Add Android and iOS apps to your project
3. Download configuration files:
   - `google-services.json` for Android (place in `android/app/`)
   - `GoogleService-Info.plist` for iOS (place in `ios/SocialMediaBot/`)
4. Enable Firebase Cloud Messaging

### 3. Social Media Platform Setup

#### Instagram/Facebook
1. Create a Facebook App at [Facebook Developer Console](https://developers.facebook.com)
2. Add Instagram Basic Display product
3. Configure OAuth redirect URIs: `socialmediabot://oauth/instagram`

#### Twitter/X
1. Create an app at [Twitter Developer Portal](https://developer.twitter.com)
2. Enable OAuth 2.0 with PKCE
3. Configure callback URL: `socialmediabot://oauth/twitter`

#### LinkedIn
1. Create an app at [LinkedIn Developer Portal](https://developer.linkedin.com)
2. Add necessary products and scopes
3. Configure redirect URL: `socialmediabot://oauth/linkedin`

#### YouTube (Google)
1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable YouTube Data API v3
3. Configure OAuth consent screen
4. Set redirect URI: `socialmediabot://oauth/youtube`

#### TikTok
1. Apply for TikTok for Developers account
2. Create an app and get API credentials
3. Configure redirect URL: `socialmediabot://oauth/tiktok`

## Android Deployment

### 1. Prepare Release Build

```bash
# Navigate to mobile directory
cd mobile

# Make build script executable
chmod +x scripts/build-android.sh

# Run build script
./scripts/build-android.sh
```

### 2. Configure Signing

Create a release keystore:

```bash
keytool -genkeypair -v -storetype PKCS12 \
  -keystore android/app/release.keystore \
  -alias social-media-bot \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

Update `android/gradle.properties`:

```properties
MYAPP_RELEASE_STORE_FILE=release.keystore
MYAPP_RELEASE_KEY_ALIAS=social-media-bot
MYAPP_RELEASE_STORE_PASSWORD=your_keystore_password
MYAPP_RELEASE_KEY_PASSWORD=your_key_password
```

### 3. Build Release APK/AAB

```bash
cd android
./gradlew assembleRelease  # For APK
./gradlew bundleRelease    # For AAB (Play Store)
```

### 4. Upload to Google Play Console

1. Create app listing in Google Play Console
2. Upload AAB file (`android/app/build/outputs/bundle/release/app-release.aab`)
3. Configure app details, screenshots, and descriptions
4. Set up release management and testing
5. Submit for review

## iOS Deployment

### 1. Prepare Xcode Project

```bash
# Navigate to mobile directory
cd mobile

# Install iOS dependencies
cd ios && pod install && cd ..

# Make build script executable
chmod +x scripts/build-ios.sh
```

### 2. Configure Signing & Capabilities

1. Open `ios/SocialMediaBot.xcworkspace` in Xcode
2. Select the project in navigator
3. Go to "Signing & Capabilities" tab
4. Enable "Automatically manage signing"
5. Select your Team and Bundle Identifier
6. Add capabilities:
   - Push Notifications
   - Associated Domains (for deep links)
   - Background Modes (for background sync)

### 3. Update Info.plist

Add URL schemes for OAuth:

```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>socialmediabot</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>socialmediabot</string>
        </array>
    </dict>
</array>
```

### 4. Build and Archive

```bash
# Run build script
./scripts/build-ios.sh
```

Or manually in Xcode:
1. Select "Any iOS Device" as target
2. Product > Archive
3. Distribute App > App Store Connect
4. Upload to App Store Connect

### 5. Submit to App Store

1. Configure app metadata in App Store Connect
2. Add screenshots and app preview videos
3. Set pricing and availability
4. Submit for App Store review

## Post-Deployment Setup

### 1. Analytics Setup

Configure analytics tracking:
- Set up Google Analytics for Firebase
- Configure custom events for key user actions
- Set up crash reporting with Firebase Crashlytics

### 2. Monitoring

Set up monitoring for:
- App performance metrics
- API response times
- Error rates and crash reports
- User engagement metrics

### 3. Push Notification Testing

Test push notifications:
```bash
# Test FCM token retrieval
# Test notification delivery
# Test deep link handling from notifications
```

### 4. OAuth Flow Testing

Test OAuth flows for each platform:
- Verify redirect URLs work correctly
- Test token storage and refresh
- Verify API calls with stored tokens

## Maintenance and Updates

### App Updates

For subsequent releases:

1. Update version numbers in:
   - `package.json`
   - `android/app/build.gradle` (versionCode and versionName)
   - `ios/SocialMediaBot/Info.plist` (CFBundleVersion and CFBundleShortVersionString)

2. Build and deploy using the same scripts
3. Update release notes in app stores

### Certificate Management

- **Android**: Keep keystore file secure and backed up
- **iOS**: Renew certificates before expiration
- **Firebase**: Monitor service account key rotation

### Security Updates

Regular security maintenance:
- Update dependencies regularly
- Monitor for security vulnerabilities
- Rotate API keys and secrets periodically
- Review and update OAuth app settings

## Troubleshooting

### Common Build Issues

**Android Build Failures:**
```bash
# Clean build
cd android && ./gradlew clean && cd ..

# Clear Metro cache
npx react-native start --reset-cache
```

**iOS Build Failures:**
```bash
# Clean build folder
rm -rf ios/build

# Clear derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Reinstall pods
cd ios && pod deintegrate && pod install && cd ..
```

### OAuth Issues

- Verify redirect URLs match exactly in platform settings
- Check URL scheme configuration in app manifests
- Ensure proper SSL certificates for API endpoints
- Verify client IDs and secrets are correct

### Push Notification Issues

- Verify Firebase configuration files are included
- Check device permissions for notifications
- Test on physical devices (simulators may have limitations)
- Verify FCM server key configuration

## Support and Resources

- [React Native Documentation](https://reactnative.dev/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Android Developer Guides](https://developer.android.com/)
- [iOS Developer Resources](https://developer.apple.com/)

For additional support, refer to the main project documentation or contact the development team.