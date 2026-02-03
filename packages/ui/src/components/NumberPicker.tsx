import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
} from 'react-native';

export interface NumberPickerProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  label?: string;
  error?: string;
  containerStyle?: ViewStyle;
}

/**
 * Touch-friendly number picker with increment/decrement buttons
 * Large buttons (56x56) for easy kiosk interaction
 */
export function NumberPicker({
  value,
  onChange,
  min = 1,
  max = 20,
  label,
  error,
  containerStyle,
}: NumberPickerProps) {
  const handleDecrement = () => {
    if (value > min) {
      onChange(value - 1);
    }
  };

  const handleIncrement = () => {
    if (value < max) {
      onChange(value + 1);
    }
  };

  const canDecrement = value > min;
  const canIncrement = value < max;

  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}
      <View style={[styles.picker, error && styles.pickerError]}>
        <TouchableOpacity
          style={[styles.button, !canDecrement && styles.buttonDisabled]}
          onPress={handleDecrement}
          disabled={!canDecrement}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Decrease party size"
          accessibilityState={{ disabled: !canDecrement }}
        >
          <Text style={[styles.buttonText, !canDecrement && styles.buttonTextDisabled]}>
            -
          </Text>
        </TouchableOpacity>
        <View style={styles.valueContainer}>
          <Text style={styles.value} accessibilityLabel={`Party size: ${value}`}>
            {value}
          </Text>
        </View>
        <TouchableOpacity
          style={[styles.button, !canIncrement && styles.buttonDisabled]}
          onPress={handleIncrement}
          disabled={!canIncrement}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Increase party size"
          accessibilityState={{ disabled: !canIncrement }}
        >
          <Text style={[styles.buttonText, !canIncrement && styles.buttonTextDisabled]}>
            +
          </Text>
        </TouchableOpacity>
      </View>
      {error && (
        <Text style={styles.errorText} accessibilityRole="alert">
          {error}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333333',
    marginBottom: 8,
  },
  picker: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#DDDDDD',
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    overflow: 'hidden',
  },
  pickerError: {
    borderColor: '#DC3545',
  },
  button: {
    width: 56,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F8F9FA',
  },
  buttonDisabled: {
    backgroundColor: '#F0F0F0',
  },
  buttonText: {
    fontSize: 28,
    fontWeight: '600',
    color: '#007AFF',
  },
  buttonTextDisabled: {
    color: '#CCCCCC',
  },
  valueContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 56,
  },
  value: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333333',
  },
  errorText: {
    color: '#DC3545',
    fontSize: 14,
    marginTop: 4,
  },
});
