/**
 * Admin App entry point.
 *
 * REQ-DEV-002: Admin tablet for waitlist management
 * REQ-SEC-004: Role-based access control
 * NFR-SEC-010: Authentication required for admin access
 */

import React from 'react';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { store } from './src/app/store';
import { ErrorBoundary } from './src/components';
import { RootNavigator } from './src/navigation';

export default function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <SafeAreaProvider>
          <StatusBar style="dark" />
          <RootNavigator />
        </SafeAreaProvider>
      </Provider>
    </ErrorBoundary>
  );
}
