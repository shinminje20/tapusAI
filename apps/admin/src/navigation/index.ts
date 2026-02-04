/**
 * Navigation exports for Admin app.
 *
 * REQ-SEC-004: Role-based access control - auth-aware navigation
 * NFR-SEC-010: Authentication required for admin access - navigation guards
 */

export { RootNavigator } from './RootNavigator';
export { AuthNavigator } from './AuthNavigator';
export { AdminNavigator } from './AdminNavigator';

// Type exports for screen props
export type {
  RootStackParamList,
  AuthStackParamList,
  AdminStackParamList,
  LoginScreenProps,
  WaitlistScreenProps,
  MessagingScreenProps,
} from './types';
