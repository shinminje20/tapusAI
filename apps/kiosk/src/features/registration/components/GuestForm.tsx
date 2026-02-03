import React, { useState, useCallback } from 'react';
import { View, StyleSheet } from 'react-native';
import { TextInput, Button } from '@tapus/ui';
import { validateGuestForm, GuestFormErrors } from '@tapus/core';
import { PhoneInput } from './PhoneInput';
import { PartySizeSelector } from './PartySizeSelector';

export interface GuestFormData {
  name: string;
  phone: string;
  partySize: number;
}

export interface GuestFormProps {
  onSubmit: (data: GuestFormData) => void;
  isLoading?: boolean;
}

/**
 * Guest registration form for kiosk
 * Validates all fields before submission [AC-WL-002]
 */
export function GuestForm({ onSubmit, isLoading = false }: GuestFormProps) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [partySize, setPartySize] = useState(1);
  const [errors, setErrors] = useState<GuestFormErrors>({});
  const [touched, setTouched] = useState({
    name: false,
    phone: false,
    partySize: false,
  });

  const validateField = useCallback(
    (field: keyof GuestFormData, value: string | number) => {
      const formData = {
        name: field === 'name' ? (value as string) : name,
        phone: field === 'phone' ? (value as string) : phone,
        partySize: field === 'partySize' ? (value as number) : partySize,
      };
      const result = validateGuestForm(formData);
      setErrors((prev) => ({
        ...prev,
        [field]: result.errors[field],
      }));
    },
    [name, phone, partySize]
  );

  const handleNameChange = (value: string) => {
    setName(value);
    if (touched.name) {
      validateField('name', value);
    }
  };

  const handlePhoneChange = (value: string) => {
    setPhone(value);
    if (touched.phone) {
      validateField('phone', value);
    }
  };

  const handlePartySizeChange = (value: number) => {
    setPartySize(value);
    if (touched.partySize) {
      validateField('partySize', value);
    }
  };

  const handleBlur = (field: keyof typeof touched) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
    const value = field === 'name' ? name : field === 'phone' ? phone : partySize;
    validateField(field, value);
  };

  const handleSubmit = () => {
    // Mark all fields as touched
    setTouched({ name: true, phone: true, partySize: true });

    // Validate entire form
    const formData = { name, phone, partySize };
    const result = validateGuestForm(formData);

    if (!result.isValid) {
      setErrors(result.errors);
      return;
    }

    // Submit if valid
    onSubmit(formData);
  };

  return (
    <View style={styles.container}>
      <TextInput
        label="Name"
        value={name}
        onChangeText={handleNameChange}
        onBlur={() => handleBlur('name')}
        placeholder="Enter your name"
        error={touched.name ? errors.name : undefined}
        autoCapitalize="words"
        autoComplete="name"
        textContentType="name"
      />

      <PhoneInput
        value={phone}
        onChangeText={handlePhoneChange}
        onBlur={() => handleBlur('phone')}
        error={touched.phone ? errors.phone : undefined}
      />

      <PartySizeSelector
        value={partySize}
        onChange={handlePartySizeChange}
        error={touched.partySize ? errors.partySize : undefined}
      />

      <View style={styles.buttonContainer}>
        <Button
          title="Join Waitlist"
          onPress={handleSubmit}
          size="large"
          loading={isLoading}
          disabled={isLoading}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
  },
  buttonContainer: {
    marginTop: 24,
  },
});
