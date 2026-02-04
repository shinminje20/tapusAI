/**
 * Root Navigator for Admin app.
 *
 * Handles authentication state and switches between Auth and Admin navigators.
 *
 * NFR-SEC-010: Authentication required for admin access - auth gate
 * REQ-SEC-004: Role-based access control - route protection
 * AC-SEC-001: RBAC blocks unauthorized actions - navigation guard
 */

import React from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { RootStackParamList } from './types';
import { AuthNavigator } from './AuthNavigator';
import { AdminNavigator } from './AdminNavigator';
import { useAuth } from '../hooks';

const Stack = createNativeStackNavigator<RootStackParamList>();

/**
 * Loading screen shown while checking authentication state
 */
function LoadingScreen() {
  return (
    <View style={styles.loadingContainer}>
      <ActivityIndicator size="large" color="#007AFF" />
      <Text style={styles.loadingText}>Loading...</Text>
    </View>
  );
}

/**
 * RootNavigator - Main navigation container.
 *
 * Switches between:
 * - AuthNavigator: When user is not authenticated
 * - AdminNavigator: When user is authenticated
 *
 * NFR-SEC-010: Enforces authentication for admin access
 * AC-SEC-001: Blocks access to admin screens without authentication
 */
export function RootNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading screen while checking auth state
  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          animation: 'fade',
        }}
      >
        {isAuthenticated ? (
          // Authenticated - show admin screens
          <Stack.Screen
            name="Admin"
            component={AdminNavigator}
            options={{
              animationTypeForReplace: 'push',
            }}
          />
        ) : (
          // Not authenticated - show login
          <Stack.Screen
            name="Auth"
            component={AuthNavigator}
            options={{
              animationTypeForReplace: 'pop',
            }}
          />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666666',
  },
});
