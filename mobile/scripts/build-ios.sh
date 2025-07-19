#!/bin/bash

# iOS Release Build Script for Social Media Management Bot
# This script builds a signed IPA for production deployment

set -e

echo "🚀 Starting iOS release build..."

# Check if we're in the mobile directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the mobile app directory"
    exit 1
fi

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: iOS builds require macOS"
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode is not installed or not in PATH"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Install iOS pods
echo "🍎 Installing iOS pods..."
cd ios
pod install --repo-update
cd ..

# Set build configuration
SCHEME="SocialMediaBot"
CONFIGURATION="Release"
WORKSPACE="ios/SocialMediaBot.xcworkspace"
ARCHIVE_PATH="build/SocialMediaBot.xcarchive"
EXPORT_PATH="build/ipa"
EXPORT_OPTIONS_PLIST="scripts/ExportOptions.plist"

# Create build directory
mkdir -p build

# Clean previous builds
echo "🧹 Cleaning previous builds..."
xcodebuild clean -workspace "$WORKSPACE" -scheme "$SCHEME" -configuration "$CONFIGURATION"

# Build and archive
echo "🔨 Building and archiving..."
xcodebuild archive \
    -workspace "$WORKSPACE" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -archivePath "$ARCHIVE_PATH" \
    -destination "generic/platform=iOS" \
    -allowProvisioningUpdates

# Export IPA
echo "📱 Exporting IPA..."
if [ -f "$EXPORT_OPTIONS_PLIST" ]; then
    xcodebuild -exportArchive \
        -archivePath "$ARCHIVE_PATH" \
        -exportPath "$EXPORT_PATH" \
        -exportOptionsPlist "$EXPORT_OPTIONS_PLIST"
else
    echo "⚠️  ExportOptions.plist not found, using default export method"
    xcodebuild -exportArchive \
        -archivePath "$ARCHIVE_PATH" \
        -exportPath "$EXPORT_PATH" \
        -exportOptionsPlist /dev/stdin <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>uploadBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
</dict>
</plist>
EOF
fi

echo "✅ iOS release build completed!"
echo ""
echo "📁 Build outputs:"
echo "   Archive: $ARCHIVE_PATH"
echo "   IPA: $EXPORT_PATH/SocialMediaBot.ipa"
echo ""
echo "🚀 Next steps:"
echo "   1. Test the IPA on physical devices"
echo "   2. Upload to App Store Connect using Xcode or Transporter"
echo "   3. Configure app metadata and screenshots"
echo "   4. Submit for App Store review"
echo ""