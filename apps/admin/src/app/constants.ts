/**
 * Application constants for the Admin app
 */

// API Configuration
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
export const API_VERSION = 'v1';
export const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Admin Source Identifier
export const ADMIN_SOURCE = 'admin' as const;

// Authentication Token Storage Keys
export const ACCESS_TOKEN_KEY = '@tapus/access_token';
export const REFRESH_TOKEN_KEY = '@tapus/refresh_token';
export const USER_DATA_KEY = '@tapus/user_data';

// Timeouts (in milliseconds)
export const API_TIMEOUT_MS = 30000; // 30 seconds API timeout
export const TOKEN_REFRESH_THRESHOLD_MS = 5 * 60 * 1000; // Refresh token 5 min before expiry

// Session Configuration
export const SESSION_TIMEOUT_MS = 8 * 60 * 60 * 1000; // 8 hours

// User Roles
export const USER_ROLES = {
  HOST: 'host',
  MANAGER: 'manager',
  OWNER: 'owner',
} as const;

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];
