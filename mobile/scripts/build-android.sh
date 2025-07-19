#!/bin/bash

# Android Release Build Script for Social Media Management Bot
# This script builds a signed APK/AAB for production deployment

set -e

echo "🚀 Starting Android release build..."

# Check if we're in the mobile directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the mobile app directory"
    exit 1
fi

# Check if Android SDK is installed
if [ -z "$ANDROID_HOME" ]; then
    echo "❌ Error: ANDROID_HOME environment variable is not set"
    echo "Please install Android SDK and set ANDROID_HOME"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Clean previous builds
echo "🧹 Cleaning previous builds..."
cd android
./gradlew clean
cd ..

# Generate release keystore if it doesn't exist
KEYSTORE_PATH="android/app/release.keystore"
if [ ! -f "$KEYSTORE_PATH" ]; then
    echo "🔑 Generating release keystore..."
    echo "⚠️  IMPORTANT: Save the keystore and password information securely!"
    read -p "Enter keystore password: " -s KEYSTORE_PASSWORD
    echo
    read -p "Enter key alias: " KEY_ALIAS
    read -p "Enter key password: " -s KEY_PASSWORD
    echo
    
    keytool -genkeypair -v -storetype PKCS12 \
        -keystore "$KEYSTORE_PATH" \
        -alias "$KEY_ALIAS" \
        -keyalg RSA \
        -keysize 2048 \
        -validity 10000 \
        -storepass "$KEYSTORE_PASSWORD" \
        -keypass "$KEY_PASSWORD" \
        -dname "CN=Social Media Bot, OU=Mobile, O=Company, L=City, ST=State, C=US"
    
    echo "✅ Keystore generated successfully!"
    echo "📝 Remember to update gradle.properties with your keystore details"
fi

# Build release APK
echo "🔨 Building release APK..."
cd android
./gradlew assembleRelease

# Build release AAB (for Google Play Store)
echo "📱 Building release AAB for Play Store..."
./gradlew bundleRelease

cd ..

echo "✅ Android release build completed!"
echo ""
echo "📁 Build outputs:"
echo "   APK: android/app/build/outputs/apk/release/app-release.apk"
echo "   AAB: android/app/build/outputs/bundle/release/app-release.aab"
echo ""
echo "🚀 Next steps:"
echo "   1. Test the APK on physical devices"
echo "   2. Upload AAB to Google Play Console"
echo "   3. Configure release notes and metadata"
echo ""