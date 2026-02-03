import React from 'react';
import { TextInput } from '@tapus/ui';

export interface PhoneInputProps {
  value: string;
  onChangeText: (value: string) => void;
  onBlur?: () => void;
  error?: string;
}

/**
 * Format phone number with masking
 * Formats as: (XXX) XXX-XXXX for US numbers
 */
function formatPhoneNumber(input: string): string {
  // Remove all non-digits
  const digits = input.replace(/\D/g, '');

  // Limit to 10 digits for US format
  const limited = digits.slice(0, 10);

  // Apply mask based on length
  if (limited.length <= 3) {
    return limited;
  }
  if (limited.length <= 6) {
    return `(${limited.slice(0, 3)}) ${limited.slice(3)}`;
  }
  return `(${limited.slice(0, 3)}) ${limited.slice(3, 6)}-${limited.slice(6)}`;
}

/**
 * Phone input with automatic masking for kiosk
 */
export function PhoneInput({
  value,
  onChangeText,
  onBlur,
  error,
}: PhoneInputProps) {
  const handleChange = (text: string) => {
    // Store raw digits but display formatted
    const formatted = formatPhoneNumber(text);
    onChangeText(formatted);
  };

  return (
    <TextInput
      label="Phone Number"
      value={value}
      onChangeText={handleChange}
      onBlur={onBlur}
      placeholder="(555) 123-4567"
      keyboardType="phone-pad"
      error={error}
      autoComplete="tel"
      textContentType="telephoneNumber"
      maxLength={14} // (XXX) XXX-XXXX
    />
  );
}
