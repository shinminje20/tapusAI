import React from 'react';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { store } from './src/app/store';
import { KioskNavigator } from './src/navigation/KioskNavigator';
import { ErrorBoundary } from './src/components';

export default function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <SafeAreaProvider>
          <StatusBar style="dark" />
          <KioskNavigator />
        </SafeAreaProvider>
      </Provider>
    </ErrorBoundary>
  );
}
