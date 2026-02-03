/**
 * Validation utilities for guest registration
 * Implements AC-WL-002: name, phone required, party_size >= 1
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

export interface GuestFormData {
  name: string;
  phone: string;
  partySize: number;
}

export interface GuestFormErrors {
  name?: string;
  phone?: string;
  partySize?: string;
}

// Phone number regex - accepts various formats
const PHONE_REGEX = /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{6,}$/;

/**
 * Validate guest name
 * Rules: required, non-empty, min 1 character after trimming
 */
export function validateName(name: string): ValidationResult {
  const trimmed = name?.trim() ?? '';

  if (!trimmed) {
    return { isValid: false, error: 'Name is required' };
  }

  if (trimmed.length < 1) {
    return { isValid: false, error: 'Name must be at least 1 character' };
  }

  return { isValid: true };
}

/**
 * Validate phone number
 * Rules: required, valid format (digits, spaces, dashes, parentheses allowed)
 */
export function validatePhone(phone: string): ValidationResult {
  const trimmed = phone?.trim() ?? '';

  if (!trimmed) {
    return { isValid: false, error: 'Phone number is required' };
  }

  // Remove all formatting to count digits
  const digitsOnly = trimmed.replace(/\D/g, '');

  if (digitsOnly.length < 7) {
    return { isValid: false, error: 'Phone number must have at least 7 digits' };
  }

  if (!PHONE_REGEX.test(trimmed)) {
    return { isValid: false, error: 'Invalid phone number format' };
  }

  return { isValid: true };
}

/**
 * Validate party size
 * Rules: required, must be >= 1, must be an integer
 */
export function validatePartySize(partySize: number, maxSize = 20): ValidationResult {
  if (partySize === undefined || partySize === null || isNaN(partySize)) {
    return { isValid: false, error: 'Party size is required' };
  }

  if (!Number.isInteger(partySize)) {
    return { isValid: false, error: 'Party size must be a whole number' };
  }

  if (partySize < 1) {
    return { isValid: false, error: 'Party size must be at least 1' };
  }

  if (partySize > maxSize) {
    return { isValid: false, error: `Party size cannot exceed ${maxSize}` };
  }

  return { isValid: true };
}

/**
 * Validate entire guest form
 * Returns object with field-specific errors
 */
export function validateGuestForm(data: GuestFormData): {
  isValid: boolean;
  errors: GuestFormErrors;
} {
  const errors: GuestFormErrors = {};

  const nameResult = validateName(data.name);
  if (!nameResult.isValid) {
    errors.name = nameResult.error;
  }

  const phoneResult = validatePhone(data.phone);
  if (!phoneResult.isValid) {
    errors.phone = phoneResult.error;
  }

  const partySizeResult = validatePartySize(data.partySize);
  if (!partySizeResult.isValid) {
    errors.partySize = partySizeResult.error;
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}
