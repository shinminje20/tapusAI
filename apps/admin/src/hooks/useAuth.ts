/**
 * Custom hook for authentication operations.
 *
 * REQ-SEC-004: Role-based access control - provides role access
 * NFR-SEC-010: Authentication required for admin access - auth state management
 * NFR-SEC-012: Session security - token refresh and logout
 */

import { useCallback, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAppDispatch, useAppSelector } from './useStore';
import {
  setCredentials,
  logout as logoutAction,
  setLoading,
  restoreAuth,
  type User,
} from '../features/auth/authSlice';
import {
  useLoginMutation,
  useRefreshMutation,
  useLazyGetMeQuery,
  type LoginRequest,
} from '../services/authApi';
import {
  ACCESS_TOKEN_KEY,
  REFRESH_TOKEN_KEY,
  USER_DATA_KEY,
} from '../app/constants';

/**
 * Return type for useAuth hook
 */
export interface UseAuthReturn {
  /** Current authenticated user or null */
  user: User | null;
  /** Whether user is authenticated */
  isAuthenticated: boolean;
  /** Whether auth state is loading (e.g., checking stored token) */
  isLoading: boolean;
  /** Login function */
  login: (credentials: LoginRequest) => Promise<void>;
  /** Logout function - clears auth state and tokens */
  logout: () => Promise<void>;
  /** Check and restore auth from stored token */
  checkAuth: () => Promise<void>;
  /** Login mutation loading state */
  isLoginLoading: boolean;
  /** Login error if any */
  loginError: unknown;
}

/**
 * Authentication hook providing login, logout, and auth state management.
 *
 * NFR-SEC-010: Manages authentication state for admin access
 * NFR-SEC-012: Handles token persistence and refresh
 *
 * @returns Authentication state and operations
 */
export function useAuth(): UseAuthReturn {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading } = useAppSelector((state) => state.auth);

  const [loginMutation, { isLoading: isLoginLoading, error: loginError }] = useLoginMutation();
  const [refreshMutation] = useRefreshMutation();
  const [getMe] = useLazyGetMeQuery();

  /**
   * Login with email and password
   * NFR-SEC-010: Authenticate user
   * NFR-SEC-012: Store tokens securely
   */
  const login = useCallback(
    async (credentials: LoginRequest): Promise<void> => {
      const result = await loginMutation(credentials).unwrap();

      dispatch(
        setCredentials({
          accessToken: result.tokens.access_token,
          refreshToken: result.tokens.refresh_token,
          user: result.user,
        })
      );
    },
    [loginMutation, dispatch]
  );

  /**
   * Logout - clear auth state and stored tokens
   * NFR-SEC-012: Session revocation
   */
  const logout = useCallback(async (): Promise<void> => {
    dispatch(logoutAction());
  }, [dispatch]);

  /**
   * Check stored auth and restore session if valid
   * Called on app startup to restore previous session
   * NFR-SEC-012: Session restoration with token validation
   */
  const checkAuth = useCallback(async (): Promise<void> => {
    dispatch(setLoading(true));

    try {
      // Check for stored tokens
      const [accessToken, refreshToken, storedUserData] = await Promise.all([
        AsyncStorage.getItem(ACCESS_TOKEN_KEY),
        AsyncStorage.getItem(REFRESH_TOKEN_KEY),
        AsyncStorage.getItem(USER_DATA_KEY),
      ]);

      if (!accessToken || !refreshToken) {
        // No stored session
        dispatch(restoreAuth(null));
        return;
      }

      // Try to validate token by fetching user info
      try {
        const userResult = await getMe().unwrap();
        dispatch(restoreAuth(userResult));
        return;
      } catch {
        // Access token might be expired, try refresh
      }

      // Try to refresh the token
      try {
        const refreshResult = await refreshMutation({
          refresh_token: refreshToken,
        }).unwrap();

        // Get user info with new token
        // Update stored access token first
        await AsyncStorage.setItem(ACCESS_TOKEN_KEY, refreshResult.access_token);
        await AsyncStorage.setItem(REFRESH_TOKEN_KEY, refreshResult.refresh_token);

        // Now fetch user with new token
        const userResult = await getMe().unwrap();

        dispatch(
          setCredentials({
            accessToken: refreshResult.access_token,
            refreshToken: refreshResult.refresh_token,
            user: userResult,
          })
        );
      } catch {
        // Refresh failed, clear stored data
        // NFR-SEC-012: Clear invalid session
        dispatch(restoreAuth(null));
        await Promise.all([
          AsyncStorage.removeItem(ACCESS_TOKEN_KEY),
          AsyncStorage.removeItem(REFRESH_TOKEN_KEY),
          AsyncStorage.removeItem(USER_DATA_KEY),
        ]);
      }
    } catch (error) {
      console.error('[useAuth] checkAuth error:', error);
      dispatch(restoreAuth(null));
    }
  }, [dispatch, getMe, refreshMutation]);

  /**
   * Auto-check auth on mount
   * NFR-SEC-012: Restore session on app start
   */
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    checkAuth,
    isLoginLoading,
    loginError,
  };
}
