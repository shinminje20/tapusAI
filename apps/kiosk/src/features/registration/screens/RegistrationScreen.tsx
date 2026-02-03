import React from 'react';
import { View, Text, StyleSheet, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../../navigation/KioskNavigator';
import { GuestForm, GuestFormData } from '../components';
import { LoadingOverlay } from '../../../components';
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

  const getErrorMessage = (error: unknown): string => {
    // Network error (no connection)
    if (error && typeof error === 'object') {
      if ('status' in error && error.status === 'FETCH_ERROR') {
        return 'Unable to connect. Please check your internet connection and try again.';
      }
      // Timeout error
      if ('status' in error && error.status === 'TIMEOUT_ERROR') {
        return 'Request timed out. Please try again.';
      }
      // Server error with detail
      if ('data' in error) {
        const data = error as { data?: { detail?: string } };
        if (data.data?.detail) {
          return data.data.detail;
        }
      }
      // HTTP status codes
      if ('status' in error && typeof error.status === 'number') {
        if (error.status >= 500) {
          return 'Server error. Please try again in a moment.';
        }
        if (error.status === 409) {
          return 'You may already be on the waitlist. Please check with staff.';
        }
      }
    }
    return 'Failed to join waitlist. Please try again.';
  };

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
        name: result.guest_name || data.name.trim(), // Use input name as fallback
      });
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      Alert.alert(
        'Unable to Join Waitlist',
        errorMessage,
        [{ text: 'OK', style: 'default' }],
        { cancelable: true }
      );
    }
  };

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container}>
      <LoadingOverlay visible={isLoading} message="Joining waitlist..." />
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
              accessibilityLabel="Cancel and go back"
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
