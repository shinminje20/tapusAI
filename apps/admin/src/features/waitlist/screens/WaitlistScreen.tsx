import React, { useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  useGetWaitlistQuery,
  useUpdateStatusMutation,
  useToggleVipMutation,
  type WaitlistEntry,
  type WaitlistStatus,
} from '../../../services/waitlistApi';
import { WaitlistItem } from '../components/WaitlistItem';

/**
 * Waitlist Management Screen for Admin App
 *
 * Features:
 * - FlatList of waitlist entries with pull-to-refresh
 * - Status transitions: waiting -> seated/canceled/no_show [AC-WL-003]
 * - VIP flagging with toggle [AC-WL-006]
 * - ETA display for each entry [AC-WL-007]
 *
 * REQ-WL-002: Real-time waitlist updates across devices
 * REQ-WL-004: Ability to reorder, prioritize, or mark VIP guests
 * REQ-WL-005: Status tracking (waiting, seated, canceled, no-show)
 */
export function WaitlistScreen() {
  // Fetch waitlist data with RTK Query
  const {
    data: entries = [],
    isLoading,
    isFetching,
    refetch,
    error,
  } = useGetWaitlistQuery(undefined, {
    pollingInterval: 30000, // Poll every 30 seconds for updates
  });

  // Mutation hooks
  const [updateStatus, { isLoading: isUpdatingStatus }] = useUpdateStatusMutation();
  const [toggleVip, { isLoading: isTogglingVip }] = useToggleVipMutation();

  const isUpdating = isUpdatingStatus || isTogglingVip;

  /**
   * Handle status change for an entry
   * AC-WL-003: Status transitions (waiting -> seated/canceled/no_show)
   */
  const handleStatusChange = useCallback(
    async (entryId: number, status: WaitlistStatus) => {
      try {
        await updateStatus({ entryId, status }).unwrap();
      } catch (err) {
        const errorMessage = getErrorMessage(err);
        Alert.alert('Status Update Failed', errorMessage, [{ text: 'OK' }]);
      }
    },
    [updateStatus]
  );

  /**
   * Handle VIP toggle for an entry
   * AC-WL-006: VIP flagging
   */
  const handleVipToggle = useCallback(
    async (entryId: number, vip: boolean) => {
      try {
        await toggleVip({ entryId, vip }).unwrap();
      } catch (err) {
        const errorMessage = getErrorMessage(err);
        Alert.alert('VIP Update Failed', errorMessage, [{ text: 'OK' }]);
      }
    },
    [toggleVip]
  );

  /**
   * Extract error message from RTK Query error
   */
  const getErrorMessage = (err: unknown): string => {
    if (err && typeof err === 'object') {
      if ('data' in err) {
        const data = err as { data?: { detail?: string } };
        if (data.data?.detail) {
          return data.data.detail;
        }
      }
      if ('status' in err && typeof err.status === 'number') {
        if (err.status === 404) {
          return 'Entry not found. It may have been removed.';
        }
        if (err.status === 422) {
          return 'Invalid operation. Please try again.';
        }
        if (err.status >= 500) {
          return 'Server error. Please try again in a moment.';
        }
      }
    }
    return 'An unexpected error occurred. Please try again.';
  };

  /**
   * Render individual waitlist item
   */
  const renderItem = useCallback(
    ({ item }: { item: WaitlistEntry }) => (
      <WaitlistItem
        entry={item}
        onStatusChange={handleStatusChange}
        onVipToggle={handleVipToggle}
        isUpdating={isUpdating}
      />
    ),
    [handleStatusChange, handleVipToggle, isUpdating]
  );

  /**
   * Key extractor for FlatList
   */
  const keyExtractor = useCallback((item: WaitlistEntry) => item.id.toString(), []);

  /**
   * Empty state component
   */
  const ListEmptyComponent = useCallback(
    () => (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyIcon}>O</Text>
        <Text style={styles.emptyTitle}>No Guests Waiting</Text>
        <Text style={styles.emptySubtitle}>
          Guests will appear here when they check in at the kiosk
        </Text>
      </View>
    ),
    []
  );

  /**
   * Header component showing count
   */
  const ListHeaderComponent = useCallback(
    () => (
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Waitlist</Text>
        <Text style={styles.headerCount}>
          {entries.length} {entries.length === 1 ? 'guest' : 'guests'} waiting
        </Text>
      </View>
    ),
    [entries.length]
  );

  // Error state
  if (error && !entries.length) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Unable to Load Waitlist</Text>
          <Text style={styles.errorSubtitle}>
            {getErrorMessage(error)}
          </Text>
          <Text style={styles.retryText} onPress={refetch}>
            Tap to Retry
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['left', 'right']}>
      <FlatList
        data={entries}
        renderItem={renderItem}
        keyExtractor={keyExtractor}
        ListHeaderComponent={ListHeaderComponent}
        ListEmptyComponent={!isLoading ? ListEmptyComponent : null}
        refreshControl={
          <RefreshControl
            refreshing={isFetching && !isLoading}
            onRefresh={refetch}
            tintColor="#007AFF"
          />
        }
        contentContainerStyle={[
          styles.listContent,
          entries.length === 0 && styles.emptyListContent,
        ]}
        showsVerticalScrollIndicator={false}
        // Landscape optimization: show 6-8 entries visible
        initialNumToRender={8}
        maxToRenderPerBatch={10}
        windowSize={5}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  listContent: {
    paddingVertical: 8,
  },
  emptyListContent: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#333333',
  },
  headerCount: {
    fontSize: 16,
    color: '#666666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyIcon: {
    fontSize: 64,
    color: '#CCCCCC',
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#FF3B30',
    marginBottom: 8,
  },
  errorSubtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
    marginBottom: 16,
  },
  retryText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
    padding: 12,
  },
});
