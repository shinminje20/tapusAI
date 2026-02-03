import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import {
  WelcomeScreen,
  RegistrationScreen,
  ConfirmationScreen,
} from '../features/registration/screens';

/**
 * Route parameters for the kiosk navigation stack
 */
export type RootStackParamList = {
  Welcome: undefined;
  Registration: undefined;
  Confirmation: {
    entryId: number;
    position: number;
    etaMinutes: number | null;
    name: string;
  };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

/**
 * Main navigation container for the kiosk app
 * Simple stack: Welcome → Registration → Confirmation → (reset) Welcome
 *
 * No admin routes available from kiosk [AC-DEV-002]
 */
export function KioskNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Welcome"
        screenOptions={{
          headerShown: false,
          animation: 'slide_from_right',
          gestureEnabled: false, // Disable swipe back on kiosk
        }}
      >
        <Stack.Screen name="Welcome" component={WelcomeScreen} />
        <Stack.Screen name="Registration" component={RegistrationScreen} />
        <Stack.Screen
          name="Confirmation"
          component={ConfirmationScreen}
          options={{
            gestureEnabled: false, // Prevent going back from confirmation
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
