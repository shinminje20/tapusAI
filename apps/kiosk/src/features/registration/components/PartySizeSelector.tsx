import React from 'react';
import { NumberPicker } from '@tapus/ui';
import { MIN_PARTY_SIZE, MAX_PARTY_SIZE } from '../../../app/constants';

export interface PartySizeSelectorProps {
  value: number;
  onChange: (value: number) => void;
  error?: string;
}

/**
 * Party size selector for kiosk registration
 * Wraps NumberPicker with kiosk-specific defaults
 */
export function PartySizeSelector({
  value,
  onChange,
  error,
}: PartySizeSelectorProps) {
  return (
    <NumberPicker
      label="Party Size"
      value={value}
      onChange={onChange}
      min={MIN_PARTY_SIZE}
      max={MAX_PARTY_SIZE}
      error={error}
    />
  );
}
