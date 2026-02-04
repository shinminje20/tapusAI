/**
 * Login screen for Admin app authentication.
 *
 * REQ-SEC-004: Role-based access control - authenticates users with roles
 * NFR-SEC-010: Authentication required for admin access
 * NFR-SEC-012: Session security - secure login flow
 * AC-SEC-001: RBAC blocks unauthorized actions - login gate
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import { Button, TextInput } from '@tapus/ui';
import { useLoginMutation } from '../../../services/authApi';
import { useAppDispatch } from '../../../hooks/useStore';
import { setCredentials } from '../authSlice';

/**
 * Email validation regex pattern
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * LoginScreen component for admin authentication.
 * NFR-SEC-010: Entry point for admin access authentication.
 */
export function LoginScreen() {
  const dispatch = useAppDispatch();
  const [login, { isLoading }] = useLoginMutation();

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailError, setEmailError] = useState<string | undefined>();
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const [generalError, setGeneralError] = useState<string | undefined>();

  /**
   * Validate form inputs before submission
   */
  const validateForm = useCallback((): boolean => {
    let isValid = true;
    setEmailError(undefined);
    setPasswordError(undefined);
    setGeneralError(undefined);

    if (!email.trim()) {
      setEmailError('Email is required');
      isValid = false;
    } else if (!EMAIL_REGEX.test(email.trim())) {
      setEmailError('Please enter a valid email address');
      isValid = false;
    }

    if (!password) {
      setPasswordError('Password is required');
      isValid = false;
    }

    return isValid;
  }, [email, password]);

  /**
   * Handle login form submission
   * NFR-SEC-010: Authenticate and establish session
   * NFR-SEC-012: Store tokens securely on success
   */
  const handleLogin = useCallback(async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const result = await login({
        email: email.trim(),
        password,
      }).unwrap();

      // Store credentials in Redux and AsyncStorage
      // NFR-SEC-012: Session security - token persistence
      dispatch(
        setCredentials({
          accessToken: result.tokens.access_token,
          refreshToken: result.tokens.refresh_token,
          user: result.user,
        })
      );

      // Navigation to main screen is handled by auth state change
      // in the root navigator
    } catch (error: unknown) {
      // Handle login errors
      // NFR-SEC-010: Show appropriate error messages
      if (error && typeof error === 'object' && 'status' in error) {
        const apiError = error as { status: number; data?: { detail?: string } };
        if (apiError.status === 401) {
          setGeneralError('Invalid email or password');
        } else if (apiError.status === 422) {
          setGeneralError('Please check your email and password format');
        } else if (apiError.data?.detail) {
          setGeneralError(apiError.data.detail);
        } else {
          setGeneralError('Login failed. Please try again.');
        }
      } else {
        setGeneralError('Network error. Please check your connection.');
      }
    }
  }, [email, password, login, dispatch, validateForm]);

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
            <Text style={styles.title}>TapusAI Admin</Text>
            <Text style={styles.subtitle}>Sign in to manage your restaurant</Text>
          </View>

          <View style={styles.form}>
            {generalError && (
              <View style={styles.errorContainer} accessibilityRole="alert">
                <Text style={styles.generalErrorText}>{generalError}</Text>
              </View>
            )}

            <TextInput
              label="Email"
              placeholder="Enter your email"
              value={email}
              onChangeText={(text) => {
                setEmail(text);
                setEmailError(undefined);
                setGeneralError(undefined);
              }}
              error={emailError}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="email-address"
              textContentType="emailAddress"
              autoComplete="email"
              editable={!isLoading}
              accessibilityLabel="Email address"
              accessibilityHint="Enter your email address to log in"
            />

            <TextInput
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                setPasswordError(undefined);
                setGeneralError(undefined);
              }}
              error={passwordError}
              secureTextEntry
              textContentType="password"
              autoComplete="password"
              editable={!isLoading}
              accessibilityLabel="Password"
              accessibilityHint="Enter your password to log in"
            />

            <View style={styles.buttonContainer}>
              <Button
                title={isLoading ? 'Signing in...' : 'Sign In'}
                onPress={handleLogin}
                loading={isLoading}
                disabled={isLoading}
                size="large"
                accessibilityLabel={isLoading ? 'Signing in' : 'Sign in button'}
                accessibilityHint="Double tap to sign in with your credentials"
              />
            </View>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>
              Contact your manager if you need access
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
    backgroundColor: '#F5F5F5',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingVertical: 32,
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
  },
  form: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
  },
  errorContainer: {
    backgroundColor: '#FEE2E2',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#FCA5A5',
  },
  generalErrorText: {
    color: '#DC2626',
    fontSize: 14,
    textAlign: 'center',
  },
  buttonContainer: {
    marginTop: 16,
  },
  footer: {
    marginTop: 48,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    color: '#999999',
  },
});
