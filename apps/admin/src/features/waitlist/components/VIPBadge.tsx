import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

export interface VIPBadgeProps {
  isVip: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

/**
 * VIP indicator with star icon
 * AC-WL-006: VIP flagging
 * - Visibly indicated as VIP in admin UI
 * - VIP status persists
 * - Tap to toggle VIP status
 */
export function VIPBadge({ isVip, onToggle, disabled = false }: VIPBadgeProps) {
  return (
    <TouchableOpacity
      style={[
        styles.badge,
        isVip ? styles.vipActive : styles.vipInactive,
        disabled && styles.disabled,
      ]}
      onPress={onToggle}
      disabled={disabled}
      activeOpacity={0.7}
      accessibilityRole="button"
      accessibilityLabel={isVip ? 'Remove VIP status' : 'Mark as VIP'}
      accessibilityState={{ selected: isVip, disabled }}
      accessibilityHint="Tap to toggle VIP status for this guest"
    >
      <Text style={[styles.star, isVip ? styles.starActive : styles.starInactive]}>
        {isVip ? '\u2605' : '\u2606'}
      </Text>
      <Text style={[styles.text, isVip ? styles.textActive : styles.textInactive]}>
        VIP
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    gap: 4,
  },
  vipActive: {
    backgroundColor: '#FFD60A',
    borderColor: '#FFD60A',
  },
  vipInactive: {
    backgroundColor: 'transparent',
    borderColor: '#8E8E93',
  },
  disabled: {
    opacity: 0.5,
  },
  star: {
    fontSize: 16,
    fontWeight: '700',
  },
  starActive: {
    color: '#000000',
  },
  starInactive: {
    color: '#8E8E93',
  },
  text: {
    fontSize: 14,
    fontWeight: '600',
  },
  textActive: {
    color: '#000000',
  },
  textInactive: {
    color: '#8E8E93',
  },
});
