/**
 * Navigation type definitions for Admin app.
 *
 * REQ-SEC-004: Role-based access control - auth flow navigation
 * NFR-SEC-010: Authentication required for admin access - auth guard navigation
 */

import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { NavigatorScreenParams } from '@react-navigation/native';

/**
 * Auth stack parameter list
 * Contains screens for unauthenticated users
 */
export type AuthStackParamList = {
  Login: undefined;
};

/**
 * Admin stack parameter list
 * Contains screens for authenticated users
 */
export type AdminStackParamList = {
  Waitlist: undefined;
  Messaging: {
    entryId: number;
    guestName: string;
    phoneNumber: string;
  };
};

/**
 * Root stack parameter list
 * Switches between Auth and Admin based on authentication state
 */
export type RootStackParamList = {
  Auth: NavigatorScreenParams<AuthStackParamList>;
  Admin: NavigatorScreenParams<AdminStackParamList>;
};

// Screen props types
export type LoginScreenProps = NativeStackScreenProps<AuthStackParamList, 'Login'>;
export type WaitlistScreenProps = NativeStackScreenProps<AdminStackParamList, 'Waitlist'>;
export type MessagingScreenProps = NativeStackScreenProps<AdminStackParamList, 'Messaging'>;

/**
 * Type augmentation for React Navigation
 * Enables type-safe navigation throughout the app
 */
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
