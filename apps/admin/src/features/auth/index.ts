/**
 * Auth feature exports for Admin app.
 *
 * REQ-SEC-004: Role-based access control
 * NFR-SEC-010: Authentication required for admin access
 */

// Redux slice and actions
export {
  default as authReducer,
  setCredentials,
  logout,
  setLoading,
  restoreAuth,
  type AuthState,
  type User,
  type Credentials,
} from './authSlice';

// Screens
export { LoginScreen } from './screens/LoginScreen';
