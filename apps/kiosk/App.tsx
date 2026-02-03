import React from 'react';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { store } from './src/app/store';
import { KioskNavigator } from './src/navigation/KioskNavigator';

export default function App() {
  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <KioskNavigator />
      </SafeAreaProvider>
    </Provider>
  );
}
