import {
  validateName,
  validatePhone,
  validatePartySize,
  validateGuestForm,
} from '../index';

/**
 * Tests for validation utilities
 * Covers AC-WL-002: name, phone required, party_size >= 1
 */

describe('validateName', () => {
  it('returns valid for non-empty name', () => {
    expect(validateName('John')).toEqual({ isValid: true });
    expect(validateName('J')).toEqual({ isValid: true });
    expect(validateName('John Doe')).toEqual({ isValid: true });
  });

  it('returns invalid for empty name', () => {
    const result = validateName('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Name is required');
  });

  it('returns invalid for whitespace-only name', () => {
    const result = validateName('   ');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Name is required');
  });

  it('trims whitespace from name', () => {
    expect(validateName('  John  ')).toEqual({ isValid: true });
  });

  it('handles undefined/null gracefully', () => {
    expect(validateName(undefined as unknown as string).isValid).toBe(false);
    expect(validateName(null as unknown as string).isValid).toBe(false);
  });
});

describe('validatePhone', () => {
  it('returns valid for valid phone numbers', () => {
    expect(validatePhone('1234567890')).toEqual({ isValid: true });
    expect(validatePhone('123-456-7890')).toEqual({ isValid: true });
    expect(validatePhone('(123) 456-7890')).toEqual({ isValid: true });
    expect(validatePhone('+1 123 456 7890')).toEqual({ isValid: true });
    expect(validatePhone('+82-10-1234-5678')).toEqual({ isValid: true });
  });

  it('returns invalid for empty phone', () => {
    const result = validatePhone('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Phone number is required');
  });

  it('returns invalid for phone with too few digits', () => {
    const result = validatePhone('123456');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Phone number must have at least 7 digits');
  });

  it('returns invalid for non-phone strings', () => {
    const result = validatePhone('abc-def-ghij');
    expect(result.isValid).toBe(false);
  });

  it('handles undefined/null gracefully', () => {
    expect(validatePhone(undefined as unknown as string).isValid).toBe(false);
    expect(validatePhone(null as unknown as string).isValid).toBe(false);
  });
});

describe('validatePartySize', () => {
  it('returns valid for party size >= 1', () => {
    expect(validatePartySize(1)).toEqual({ isValid: true });
    expect(validatePartySize(5)).toEqual({ isValid: true });
    expect(validatePartySize(20)).toEqual({ isValid: true });
  });

  it('returns invalid for party size < 1', () => {
    const result = validatePartySize(0);
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Party size must be at least 1');
  });

  it('returns invalid for negative party size', () => {
    const result = validatePartySize(-1);
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Party size must be at least 1');
  });

  it('returns invalid for non-integer party size', () => {
    const result = validatePartySize(2.5);
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Party size must be a whole number');
  });

  it('returns invalid for party size exceeding max', () => {
    const result = validatePartySize(21);
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Party size cannot exceed 20');
  });

  it('respects custom max size', () => {
    expect(validatePartySize(15, 10).isValid).toBe(false);
    expect(validatePartySize(15, 20).isValid).toBe(true);
  });

  it('handles undefined/null/NaN gracefully', () => {
    expect(validatePartySize(undefined as unknown as number).isValid).toBe(false);
    expect(validatePartySize(null as unknown as number).isValid).toBe(false);
    expect(validatePartySize(NaN).isValid).toBe(false);
  });
});

describe('validateGuestForm', () => {
  it('returns valid for complete valid form', () => {
    const result = validateGuestForm({
      name: 'John Doe',
      phone: '123-456-7890',
      partySize: 4,
    });
    expect(result.isValid).toBe(true);
    expect(result.errors).toEqual({});
  });

  it('returns errors for all invalid fields', () => {
    const result = validateGuestForm({
      name: '',
      phone: '',
      partySize: 0,
    });
    expect(result.isValid).toBe(false);
    expect(result.errors.name).toBeDefined();
    expect(result.errors.phone).toBeDefined();
    expect(result.errors.partySize).toBeDefined();
  });

  it('returns errors only for invalid fields', () => {
    const result = validateGuestForm({
      name: 'John',
      phone: '',
      partySize: 2,
    });
    expect(result.isValid).toBe(false);
    expect(result.errors.name).toBeUndefined();
    expect(result.errors.phone).toBeDefined();
    expect(result.errors.partySize).toBeUndefined();
  });
});
