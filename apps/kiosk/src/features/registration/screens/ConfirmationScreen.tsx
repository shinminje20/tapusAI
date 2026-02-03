import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '@tapus/ui';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RouteProp } from '@react-navigation/native';
import type { RootStackParamList } from '../../../navigation/KioskNavigator';
import { CONFIRMATION_TIMEOUT_MS } from '../../../app/constants';

type ConfirmationScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Confirmation'>;
  route: RouteProp<RootStackParamList, 'Confirmation'>;
};

/**
 * Confirmation screen - shows position and ETA
 * Auto-resets to Welcome after timeout for next guest
 */
export function ConfirmationScreen({ navigation, route }: ConfirmationScreenProps) {
  const { position, etaMinutes, name } = route.params;
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    // Auto-reset after timeout
    timeoutRef.current = setTimeout(() => {
      navigation.reset({
        index: 0,
        routes: [{ name: 'Welcome' }],
      });
    }, CONFIRMATION_TIMEOUT_MS);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [navigation]);

  const handleDone = () => {
    // Clear timeout and reset immediately
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    navigation.reset({
      index: 0,
      routes: [{ name: 'Welcome' }],
    });
  };

  const formatEta = (minutes: number | null): string => {
    if (minutes === null || minutes === undefined) {
      return 'Calculating...';
    }
    if (minutes < 1) {
      return 'Any moment now!';
    }
    if (minutes === 1) {
      return '~1 minute';
    }
    return `~${minutes} minutes`;
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.checkmark}>
          <Text style={styles.checkmarkText}>✓</Text>
        </View>

        <Text style={styles.title}>You're on the list!</Text>

        <Text style={styles.greeting}>
          Thanks, {name}!
        </Text>

        <View style={styles.infoCard}>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Your position</Text>
            <Text style={styles.infoValue}>#{position}</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Estimated wait</Text>
            <Text style={styles.infoValue}>{formatEta(etaMinutes)}</Text>
          </View>
        </View>

        <Text style={styles.notice}>
          We'll send you a text message when your table is ready.
        </Text>

        <View style={styles.buttonContainer}>
          <Button
            title="Done"
            onPress={handleDone}
            size="large"
            style={styles.button}
          />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  checkmark: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#28A745',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  checkmarkText: {
    fontSize: 40,
    color: '#FFFFFF',
  },
  title: {
    fontSize: 36,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 8,
    textAlign: 'center',
  },
  greeting: {
    fontSize: 20,
    color: '#666666',
    marginBottom: 32,
    textAlign: 'center',
  },
  infoCard: {
    width: '100%',
    maxWidth: 400,
    backgroundColor: '#F8F9FA',
    borderRadius: 16,
    padding: 24,
    marginBottom: 24,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  infoLabel: {
    fontSize: 18,
    color: '#666666',
  },
  infoValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333333',
  },
  divider: {
    height: 1,
    backgroundColor: '#DEE2E6',
    marginVertical: 16,
  },
  notice: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 24,
  },
  buttonContainer: {
    width: '100%',
    maxWidth: 400,
  },
  button: {
    width: '100%',
  },
});
