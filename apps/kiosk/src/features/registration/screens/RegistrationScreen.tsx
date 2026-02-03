import React from 'react';
import { View, Text, StyleSheet, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../../navigation/KioskNavigator';
import { GuestForm, GuestFormData } from '../components';
import { useAddGuestMutation } from '../../../services/waitlistApi';

type RegistrationScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Registration'>;
};

/**
 * Registration screen - guest enters their information
 * Submits to API and navigates to confirmation on success
 */
export function RegistrationScreen({ navigation }: RegistrationScreenProps) {
  const [addGuest, { isLoading }] = useAddGuestMutation();

  const handleSubmit = async (data: GuestFormData) => {
    try {
      const result = await addGuest({
        name: data.name.trim(),
        phone_number: data.phone.replace(/\D/g, ''), // Send digits only
        party_size: data.partySize,
      }).unwrap();

      // Navigate to confirmation with entry data
      navigation.replace('Confirmation', {
        entryId: result.id,
        position: result.position,
        etaMinutes: result.eta_minutes,
        name: result.name,
      });
    } catch (error) {
      // Handle API errors
      const errorMessage =
        error && typeof error === 'object' && 'data' in error
          ? (error as { data?: { detail?: string } }).data?.detail || 'Failed to join waitlist'
          : 'Failed to join waitlist. Please try again.';

      Alert.alert('Error', errorMessage, [{ text: 'OK' }]);
    }
  };

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.header}>
            <Text style={styles.title}>Join Waitlist</Text>
            <Text style={styles.subtitle}>
              Please enter your information below
            </Text>
          </View>

          <View style={styles.formContainer}>
            <GuestForm onSubmit={handleSubmit} isLoading={isLoading} />
          </View>

          <View style={styles.backContainer}>
            <Text
              style={styles.backText}
              onPress={handleBack}
              accessibilityRole="button"
            >
              Cancel
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 32,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 36,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#666666',
  },
  formContainer: {
    flex: 1,
    maxWidth: 500,
    width: '100%',
    alignSelf: 'center',
  },
  backContainer: {
    alignItems: 'center',
    marginTop: 24,
    paddingBottom: 24,
  },
  backText: {
    fontSize: 16,
    color: '#007AFF',
    padding: 12,
  },
});
