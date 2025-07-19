/**
 * Jest setup file for React Native testing
 */
/* eslint-env jest */

import 'react-native-gesture-handler/jestSetup';
import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock';

// Setup testing environment
global.__DEV__ = true;

// Mock MMKV first before any other imports
jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    set: jest.fn(),
  })),
}));

// Mock AsyncStorage first
jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);

// Mock MMKV
jest.mock('react-native-mmkv', () => ({
  MMKV: jest.fn().mockImplementation(() => ({
    getString: jest.fn(),
    set: jest.fn(),
    delete: jest.fn(),
  })),
}));

// Mock React Native gesture handler
jest.mock('react-native-gesture-handler', () => {
  const mockView = 'View';
  return {
    Swipeable: mockView,
    DrawerLayout: mockView,
    State: {},
    ScrollView: mockView,
    Slider: mockView,
    Switch: mockView,
    TextInput: mockView,
    ToolbarAndroid: mockView,
    ViewPagerAndroid: mockView,
    DrawerLayoutAndroid: mockView,
    WebView: mockView,
    NativeViewGestureHandler: mockView,
    TapGestureHandler: mockView,
    FlingGestureHandler: mockView,
    ForceTouchGestureHandler: mockView,
    LongPressGestureHandler: mockView,
    PanGestureHandler: mockView,
    PinchGestureHandler: mockView,
    RotationGestureHandler: mockView,
    RawButton: mockView,
    BaseButton: mockView,
    RectButton: mockView,
    BorderlessButton: mockView,
    FlatList: mockView,
    gestureHandlerRootHOC: (component) => component,
    Directions: {},
  };
});

// Mock React Navigation
jest.mock('@react-navigation/native', () => {
  return {
    NavigationContainer: ({ children }) => children,
    useNavigation: () => ({
      navigate: jest.fn(),
      goBack: jest.fn(),
    }),
    useRoute: () => ({
      params: {},
    }),
    useFocusEffect: jest.fn(),
  };
});

jest.mock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }) => children,
    Screen: ({ children }) => children,
  }),
}));

jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }) => children,
    Screen: ({ children }) => children,
  }),
}));

// Mock Firebase
jest.mock('@react-native-firebase/messaging', () => ({
  __esModule: true,
  default: () => ({
    hasPermission: jest.fn(() => Promise.resolve(true)),
    subscribeToTopic: jest.fn(),
    unsubscribeFromTopic: jest.fn(),
    requestPermission: jest.fn(() => Promise.resolve(true)),
    getToken: jest.fn(() => Promise.resolve('mock-token')),
    onMessage: jest.fn(),
    onNotificationOpenedApp: jest.fn(),
    getInitialNotification: jest.fn(() => Promise.resolve(null)),
  }),
}));

// Mock vector icons
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');

// Mock other React Native modules
jest.mock('react-native-image-picker', () => ({
  launchImageLibrary: jest.fn(),
  launchCamera: jest.fn(),
}));

jest.mock('react-native-localize', () => ({
  getLocales: jest.fn(() => [{ languageCode: 'en', countryCode: 'US' }]),
}));

jest.mock('@react-native-community/netinfo', () => ({
  addEventListener: jest.fn(),
  fetch: jest.fn(() => Promise.resolve({ isConnected: true })),
}));

jest.mock('react-native-permissions', () => ({
  PERMISSIONS: {
    IOS: {
      CAMERA: 'ios.permission.CAMERA',
      PHOTO_LIBRARY: 'ios.permission.PHOTO_LIBRARY',
    },
    ANDROID: {
      CAMERA: 'android.permission.CAMERA',
      WRITE_EXTERNAL_STORAGE: 'android.permission.WRITE_EXTERNAL_STORAGE',
    },
  },
  RESULTS: {
    GRANTED: 'granted',
    DENIED: 'denied',
  },
  request: jest.fn(() => Promise.resolve('granted')),
  check: jest.fn(() => Promise.resolve('granted')),
}));

// Mock i18n
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: {
      changeLanguage: jest.fn(),
    },
  }),
}));

// Silence console warnings during tests
const originalWarn = console.warn;
beforeAll(() => {
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: React.createElement')
    ) {
      return;
    }
    originalWarn(...args);
  };
});

afterAll(() => {
  console.warn = originalWarn;
});