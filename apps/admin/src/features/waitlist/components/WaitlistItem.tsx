import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Button } from '@tapus/ui';
import type { WaitlistEntry, WaitlistStatus } from '../../../services/waitlistApi';
import type { AdminStackParamList } from '../../../navigation/types';
import { StatusBadge } from './StatusBadge';
import { VIPBadge } from './VIPBadge';

type NavigationProp = NativeStackNavigationProp<AdminStackParamList, 'Waitlist'>;

export interface WaitlistItemProps {
  entry: WaitlistEntry;
  onStatusChange: (entryId: number, status: WaitlistStatus) => void;
  onVipToggle: (entryId: number, vip: boolean) => void;
  isUpdating?: boolean;
}

/**
 * Mask phone number for display
 * Shows only last 4 digits for privacy
 */
function maskPhone(phone: string | null): string {
  if (!phone) return '---';
  const digits = phone.replace(/\D/g, '');
  if (digits.length < 4) return '***';
  return `***-***-${digits.slice(-4)}`;
}

/**
 * Format wait time for display
 * AC-WL-007: ETA calculation displayed
 */
function formatWaitTime(minutes: number | null): string {
  if (minutes === null) return '--';
  if (minutes < 1) return '<1 min';
  if (minutes === 1) return '1 min';
  return `${minutes} min`;
}

/**
 * Calculate time since check-in
 */
function formatTimeSinceCheckIn(checkInTime: string): string {
  const checkIn = new Date(checkInTime);
  const now = new Date();
  const diffMs = now.getTime() - checkIn.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins === 1) return '1 min ago';
  if (diffMins < 60) return `${diffMins} min ago`;

  const hours = Math.floor(diffMins / 60);
  if (hours === 1) return '1 hr ago';
  return `${hours} hrs ago`;
}

/**
 * Single waitlist entry row component
 *
 * Displays:
 * - Guest name, party size, phone (masked)
 * - Status badge (color-coded)
 * - VIP indicator with toggle
 * - Wait time / ETA
 * - Action buttons for status changes
 *
 * Props:
 * - entry: WaitlistEntry data
 * - onStatusChange: callback for status transitions [AC-WL-003]
 * - onVipToggle: callback for VIP toggle [AC-WL-006]
 */
export function WaitlistItem({
  entry,
  onStatusChange,
  onVipToggle,
  isUpdating = false,
}: WaitlistItemProps) {
  const navigation = useNavigation<NavigationProp>();
  const isWaiting = entry.status === 'waiting';

  const handleSeat = () => {
    onStatusChange(entry.id, 'seated');
  };

  const handleCancel = () => {
    onStatusChange(entry.id, 'canceled');
  };

  const handleNoShow = () => {
    onStatusChange(entry.id, 'no_show');
  };

  const handleVipToggle = () => {
    onVipToggle(entry.id, !entry.vip_flag);
  };

  /**
   * Navigate to messaging screen to send message to guest
   * REQ-STAFF-001: Canned response templates on Admin tablet
   * AC-STAFF-002: Templates can be inserted with minimal taps
   */
  const handleMessage = () => {
    navigation.navigate('Messaging', {
      entryId: entry.id,
      guestName: entry.guest_name || 'Guest',
      phoneNumber: entry.guest_phone || '',
    });
  };

  return (
    <View
      style={[styles.container, entry.vip_flag && styles.vipContainer]}
      accessible={true}
      accessibilityLabel={`${entry.guest_name || 'Guest'}, party of ${entry.party_size}, ${entry.status}`}
    >
      {/* Left section: Position and Guest Info */}
      <View style={styles.leftSection}>
        <View style={styles.positionContainer}>
          <Text style={styles.position}>#{entry.position}</Text>
        </View>

        <View style={styles.guestInfo}>
          <View style={styles.nameRow}>
            <Text style={styles.guestName} numberOfLines={1}>
              {entry.guest_name || 'Guest'}
            </Text>
            <VIPBadge
              isVip={entry.vip_flag}
              onToggle={handleVipToggle}
              disabled={isUpdating || !isWaiting}
            />
          </View>

          <View style={styles.detailsRow}>
            <Text style={styles.partySize}>
              Party of {entry.party_size}
            </Text>
            <Text style={styles.separator}>|</Text>
            <Text style={styles.phone}>{maskPhone(entry.guest_phone)}</Text>
          </View>

          <View style={styles.timeRow}>
            <Text style={styles.checkInTime}>
              Checked in: {formatTimeSinceCheckIn(entry.created_at)}
            </Text>
          </View>
        </View>
      </View>

      {/* Middle section: Status and ETA */}
      <View style={styles.middleSection}>
        <StatusBadge status={entry.status} />
        {isWaiting && (
          <View style={styles.etaContainer}>
            <Text style={styles.etaLabel}>Est. Wait</Text>
            <Text style={styles.etaValue}>{formatWaitTime(entry.eta_minutes)}</Text>
          </View>
        )}
      </View>

      {/* Right section: Action Buttons */}
      {isWaiting && (
        <View style={styles.actionsSection}>
          <Button
            title="Seat"
            onPress={handleSeat}
            variant="primary"
            size="small"
            disabled={isUpdating}
            loading={isUpdating}
            style={styles.actionButton}
          />
          <Button
            title="Message"
            onPress={handleMessage}
            variant="secondary"
            size="small"
            disabled={isUpdating || !entry.guest_phone}
            style={styles.actionButton}
          />
          <Button
            title="Cancel"
            onPress={handleCancel}
            variant="outline"
            size="small"
            disabled={isUpdating}
            style={styles.actionButton}
          />
          <Button
            title="No Show"
            onPress={handleNoShow}
            variant="outline"
            size="small"
            disabled={isUpdating}
            style={styles.actionButton}
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  vipContainer: {
    borderWidth: 2,
    borderColor: '#FFD60A',
    backgroundColor: '#FFFBEB',
  },
  leftSection: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
  },
  positionContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F2F2F7',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  position: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333333',
  },
  guestInfo: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  guestName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333333',
    flex: 1,
  },
  detailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  partySize: {
    fontSize: 14,
    color: '#666666',
  },
  separator: {
    fontSize: 14,
    color: '#CCCCCC',
    marginHorizontal: 8,
  },
  phone: {
    fontSize: 14,
    color: '#666666',
  },
  timeRow: {
    marginTop: 2,
  },
  checkInTime: {
    fontSize: 12,
    color: '#8E8E93',
  },
  middleSection: {
    flex: 1,
    alignItems: 'center',
    gap: 8,
  },
  etaContainer: {
    alignItems: 'center',
  },
  etaLabel: {
    fontSize: 12,
    color: '#8E8E93',
  },
  etaValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
  },
  actionsSection: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 8,
  },
  actionButton: {
    minWidth: 80,
  },
});
