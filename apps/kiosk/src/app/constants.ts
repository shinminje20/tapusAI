/**
 * Application constants for the Kiosk app
 */

// API Configuration
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
export const API_VERSION = 'v1';
export const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Kiosk Configuration
export const KIOSK_SOURCE = 'kiosk' as const;

// Timeouts (in milliseconds)
export const CONFIRMATION_TIMEOUT_MS = 30000; // 30 seconds before auto-reset
export const API_TIMEOUT_MS = 10000; // 10 seconds API timeout

// Validation Constants
export const MIN_PARTY_SIZE = 1;
export const MAX_PARTY_SIZE = 20;
export const PHONE_REGEX = /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$/;
