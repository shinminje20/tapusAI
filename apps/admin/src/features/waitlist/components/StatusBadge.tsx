import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { WaitlistStatus } from '../../../services/waitlistApi';

export interface StatusBadgeProps {
  status: WaitlistStatus;
}

/**
 * Color-coded status indicator for waitlist entries
 * AC-WL-003: Status transitions displayed visually
 *
 * Colors:
 * - waiting: blue (active state)
 * - seated: green (completed successfully)
 * - canceled: gray (guest canceled)
 * - no_show: red (guest did not arrive)
 */
export function StatusBadge({ status }: StatusBadgeProps) {
  const getStatusStyle = () => {
    switch (status) {
      case 'waiting':
        return styles.waiting;
      case 'seated':
        return styles.seated;
      case 'canceled':
        return styles.canceled;
      case 'no_show':
        return styles.noShow;
      default:
        return styles.waiting;
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'waiting':
        return 'Waiting';
      case 'seated':
        return 'Seated';
      case 'canceled':
        return 'Canceled';
      case 'no_show':
        return 'No Show';
      default:
        return status;
    }
  };

  return (
    <View
      style={[styles.badge, getStatusStyle()]}
      accessibilityRole="text"
      accessibilityLabel={`Status: ${getStatusLabel()}`}
    >
      <Text style={styles.text}>{getStatusLabel()}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'flex-start',
  },
  text: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
    textTransform: 'capitalize',
  },
  waiting: {
    backgroundColor: '#007AFF', // Blue
  },
  seated: {
    backgroundColor: '#34C759', // Green
  },
  canceled: {
    backgroundColor: '#8E8E93', // Gray
  },
  noShow: {
    backgroundColor: '#FF3B30', // Red
  },
});
