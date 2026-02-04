/**
 * Authentication API endpoints using RTK Query.
 *
 * REQ-SEC-004: Role-based access control - user role in response
 * NFR-SEC-010: Authentication required for admin access - login endpoint
 * NFR-SEC-012: Session security - token refresh mechanism
 */

import { baseApi } from './api';
import type { User } from '../features/auth/authSlice';

/**
 * Login request payload
 * Matches backend LoginRequest schema
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Token response from backend
 * Matches backend TokenResponse schema
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/**
 * Refresh token request payload
 * Matches backend RefreshTokenRequest schema
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * User response from /auth/me endpoint
 * Matches backend UserResponse schema
 */
export interface UserResponse {
  id: number;
  email: string;
  role: string;
  restaurant_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Combined login response with tokens and user info
 * Used by the login mutation to return all necessary data
 */
export interface LoginResponse {
  tokens: TokenResponse;
  user: User;
}

/**
 * Authentication API endpoints
 * Injected into baseApi for token header handling
 */
export const authApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    /**
     * Login with email and password
     * POST /api/v1/auth/login
     * NFR-SEC-010: Authentication required for admin access
     */
    login: builder.mutation<LoginResponse, LoginRequest>({
      async queryFn(credentials, _queryApi, _extraOptions, fetchWithBQ) {
        // First, get tokens
        const tokenResult = await fetchWithBQ({
          url: '/auth/login',
          method: 'POST',
          body: credentials,
        });

        if (tokenResult.error) {
          return { error: tokenResult.error };
        }

        const tokens = tokenResult.data as TokenResponse;

        // Then fetch user info with the new token
        const userResult = await fetchWithBQ({
          url: '/auth/me',
          method: 'GET',
          headers: {
            Authorization: `Bearer ${tokens.access_token}`,
          },
        });

        if (userResult.error) {
          return { error: userResult.error };
        }

        const userResponse = userResult.data as UserResponse;

        // Transform to User type (REQ-SEC-004: role-based access)
        const user: User = {
          id: userResponse.id,
          email: userResponse.email,
          role: userResponse.role as User['role'],
          restaurant_id: userResponse.restaurant_id,
        };

        return {
          data: {
            tokens,
            user,
          },
        };
      },
      invalidatesTags: ['User'],
    }),

    /**
     * Refresh access token using refresh token
     * POST /api/v1/auth/refresh
     * NFR-SEC-012: Secure token refresh mechanism
     */
    refresh: builder.mutation<TokenResponse, RefreshTokenRequest>({
      query: (refreshData) => ({
        url: '/auth/refresh',
        method: 'POST',
        body: refreshData,
      }),
    }),

    /**
     * Get current authenticated user info
     * GET /api/v1/auth/me
     * REQ-SEC-004: Role-based access control
     */
    getMe: builder.query<User, void>({
      query: () => '/auth/me',
      transformResponse: (response: UserResponse): User => ({
        id: response.id,
        email: response.email,
        role: response.role as User['role'],
        restaurant_id: response.restaurant_id,
      }),
      providesTags: ['User'],
    }),
  }),
});

// Export hooks for usage in components
export const {
  useLoginMutation,
  useRefreshMutation,
  useGetMeQuery,
  useLazyGetMeQuery,
} = authApi;
