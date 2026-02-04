module.exports = {
  preset: 'jest-expo',
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg|@reduxjs/toolkit|immer|redux|redux-thunk|reselect|react-redux|use-sync-external-store|@tapus/.*)',
  ],
  moduleNameMapper: {
    '^@tapus/core$': '<rootDir>/../../packages/core/src',
    '^@tapus/core/(.*)$': '<rootDir>/../../packages/core/src/$1',
    '^@tapus/ui$': '<rootDir>/../../packages/ui/src',
    '^@tapus/ui/(.*)$': '<rootDir>/../../packages/ui/src/$1',
  },
  testMatch: ['**/__tests__/**/*.test.ts?(x)', '**/*.test.ts?(x)'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**',
  ],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
};
