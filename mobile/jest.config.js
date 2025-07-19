module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|@react-navigation|react-native-vector-icons|react-native-gesture-handler|react-native-reanimated|react-native-screens|react-native-safe-area-context|@react-native-async-storage|@react-native-firebase|@react-native-community|react-native-mmkv|react-native-localize|react-native-permissions|react-native-image-picker|react-native-chart-kit|react-native-svg)/)',
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testEnvironment: 'node',
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/types/*.ts',
  ],
};
