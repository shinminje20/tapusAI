/**
 * Authentication Navigator for Admin app.
 *
 * Contains screens for unauthenticated users (login flow).
 *
 * NFR-SEC-010: Authentication required for admin access
 * REQ-SEC-004: Role-based access control - entry point to auth
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { AuthStackParamList } from './types';
import { LoginScreen } from '../features/auth';

const Stack = createNativeStackNavigator<AuthStackParamList>();

/**
 * AuthNavigator - Stack navigator for authentication screens.
 * Displays login screen for unauthenticated users.
 *
 * NFR-SEC-010: Gate for admin access authentication
 */
export function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animation: 'fade',
        contentStyle: { backgroundColor: '#F5F5F5' },
      }}
    >
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{
          title: 'Sign In',
        }}
      />
    </Stack.Navigator>
  );
}
