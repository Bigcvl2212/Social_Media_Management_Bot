/**
 * Jest setup file for React Native testing
 */
/* eslint-env jest */

import mockAsyncStorage from '@react-native-async-storage/async-storage/jest/async-storage-mock';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => mockAsyncStorage);

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

// Mock vector icons
jest.mock('react-native-vector-icons/MaterialIcons', () => 'Icon');

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