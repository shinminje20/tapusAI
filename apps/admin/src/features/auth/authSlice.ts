/**
 * Authentication Redux slice for Admin app.
 *
 * REQ-SEC-004: Role-based access control - stores user with role
 * NFR-SEC-010: Authentication required for admin access - tracks auth state
 * NFR-SEC-012: Session security - token persistence and clearing
 * AC-SEC-001: RBAC blocks unauthorized actions - role available for checks
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  ACCESS_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  USER_DATA_KEY,
  type UserRole,
} from '../../app/constants';

/**
 * User type matching backend UserResponse schema
 * See: backend/app/api/v1/schemas/auth.py
 */
export interface User {
  id: number;
  email: string;
  role: UserRole;
  restaurant_id: number | null;
}

/**
 * Authentication state structure
 * NFR-SEC-010: Tracks whether user is authenticated
 */
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true, // True initially while checking stored token
};

/**
 * Credentials payload for setCredentials action
 * Contains tokens and user info from login/refresh response
 */
export interface Credentials {
  accessToken: string;
  refreshToken: string;
  user: User;
}

/**
 * Persist tokens and user data to AsyncStorage
 * NFR-SEC-012: Secure session storage
 */
async function persistCredentials(credentials: Credentials): Promise<void> {
  await Promise.all([
    AsyncStorage.setItem(ACCESS_TOKEN_KEY, credentials.accessToken),
    AsyncStorage.setItem(REFRESH_TOKEN_KEY, credentials.refreshToken),
    AsyncStorage.setItem(USER_DATA_KEY, JSON.stringify(credentials.user)),
  ]);
}

/**
 * Clear all auth data from AsyncStorage
 * NFR-SEC-012: Session revocation support
 */
async function clearStoredCredentials(): Promise<void> {
  await Promise.all([
    AsyncStorage.removeItem(ACCESS_TOKEN_KEY),
    AsyncStorage.removeItem(REFRESH_TOKEN_KEY),
    AsyncStorage.removeItem(USER_DATA_KEY),
  ]);
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    /**
     * Set user credentials after successful login or token refresh
     * NFR-SEC-010: Authentication state management
     * NFR-SEC-012: Token persistence
     */
    setCredentials: (state, action: PayloadAction<Credentials>) => {
      const { user } = action.payload;
      state.user = user;
      state.isAuthenticated = true;
      state.isLoading = false;
      // Persist credentials to storage (fire and forget, handled by middleware if needed)
      persistCredentials(action.payload).catch((error) => {
        console.error('[authSlice] Failed to persist credentials:', error);
      });
    },

    /**
     * Clear auth state and stored credentials on logout
     * NFR-SEC-012: Session revocation
     */
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.isLoading = false;
      clearStoredCredentials().catch((error) => {
        console.error('[authSlice] Failed to clear credentials:', error);
      });
    },

    /**
     * Set loading state during auth operations
     */
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    /**
     * Restore auth state from stored data (used on app startup)
     * NFR-SEC-012: Session restoration
     */
    restoreAuth: (state, action: PayloadAction<User | null>) => {
      if (action.payload) {
        state.user = action.payload;
        state.isAuthenticated = true;
      } else {
        state.user = null;
        state.isAuthenticated = false;
      }
      state.isLoading = false;
    },
  },
});

export const { setCredentials, logout, setLoading, restoreAuth } = authSlice.actions;
export default authSlice.reducer;
