/**
 * Admin Navigator for authenticated staff members.
 *
 * Contains main admin screens: Waitlist management and Messaging.
 *
 * REQ-WL-002: Real-time waitlist updates across devices
 * REQ-WL-004: Ability to reorder, prioritize, or mark VIP guests
 * REQ-WL-005: Status tracking (waiting, seated, canceled, no-show)
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * REQ-SEC-004: Role-based access control - protected routes
 */

import React, { useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import type { AdminStackParamList } from './types';
import { WaitlistScreen } from '../features/waitlist/screens/WaitlistScreen';
import { MessagingScreen } from '../features/messaging/screens/MessagingScreen';
import { useAuth } from '../hooks';

const Stack = createNativeStackNavigator<AdminStackParamList>();

/**
 * Header component with logout button
 * NFR-SEC-012: Session security - logout capability
 */
function AdminHeader({ title }: { title: string }) {
  const { logout, user } = useAuth();

  const handleLogout = useCallback(() => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: () => logout(),
        },
      ],
      { cancelable: true }
    );
  }, [logout]);

  return (
    <View style={styles.header}>
      <View style={styles.headerLeft}>
        <Text style={styles.headerTitle}>{title}</Text>
        {user && (
          <Text style={styles.headerSubtitle}>
            {user.email} ({user.role})
          </Text>
        )}
      </View>
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}
        accessibilityRole="button"
        accessibilityLabel="Sign out"
      >
        <Text style={styles.logoutButtonText}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
}

/**
 * AdminNavigator - Stack navigator for authenticated admin screens.
 *
 * REQ-WL-002: Provides access to waitlist management
 * REQ-STAFF-001: Provides access to messaging templates
 */
export function AdminNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Waitlist"
      screenOptions={{
        animation: 'slide_from_right',
        contentStyle: { backgroundColor: '#F5F5F5' },
      }}
    >
      <Stack.Screen
        name="Waitlist"
        component={WaitlistScreen}
        options={{
          header: () => <AdminHeader title="TapusAI Admin" />,
        }}
      />
      <Stack.Screen
        name="Messaging"
        component={MessagingScreen}
        options={{
          headerShown: false, // MessagingScreen has its own header
          presentation: 'modal',
        }}
      />
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingTop: 50, // Safe area for status bar
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  headerLeft: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333333',
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#666666',
    marginTop: 2,
  },
  logoutButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    backgroundColor: '#F5F5F5',
  },
  logoutButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666666',
  },
});
