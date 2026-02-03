import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '@tapus/ui';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../../../navigation/KioskNavigator';

type WelcomeScreenProps = {
  navigation: NativeStackNavigationProp<RootStackParamList, 'Welcome'>;
};

/**
 * Welcome screen - entry point for kiosk
 * Large "Join Waitlist" button for easy touch interaction
 */
export function WelcomeScreen({ navigation }: WelcomeScreenProps) {
  const handleJoinWaitlist = () => {
    navigation.navigate('Registration');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>Welcome!</Text>
          <Text style={styles.subtitle}>
            Join our waitlist and we'll let you know when your table is ready.
          </Text>
        </View>

        <View style={styles.buttonContainer}>
          <Button
            title="Join Waitlist"
            onPress={handleJoinWaitlist}
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
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  title: {
    fontSize: 48,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 16,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 20,
    color: '#666666',
    textAlign: 'center',
    lineHeight: 28,
  },
  buttonContainer: {
    width: '100%',
    maxWidth: 400,
  },
  button: {
    width: '100%',
  },
});
