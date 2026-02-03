// Re-export components
export { Button, type ButtonProps } from './components/Button';
export { TextInput, type TextInputProps } from './components/TextInput';
export { NumberPicker, type NumberPickerProps } from './components/NumberPicker';

// Legacy placeholder (for backwards compatibility)
import React from "react";
import { Text } from "react-native";

export const Placeholder = () => {
  return <Text>Tapus UI placeholder</Text>;
};
