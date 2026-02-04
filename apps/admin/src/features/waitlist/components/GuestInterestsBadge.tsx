import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal, ScrollView } from 'react-native';
import { useGetGuestInterestsQuery } from '../../../services/waitlistApi';

interface GuestInterestsBadgeProps {
  entryId: number;
}

/**
 * Badge showing guest interests summary.
 *
 * REQ-MENU-004: Full service "likely to order" view
 * AC-MENU-004: Admin sees "Likely to order" summary on waitlist item
 *
 * Displays:
 * - Compact badge: "Interested in: Burger, Salad (+2 more)"
 * - Expandable modal with full list
 * - Visual indicator when guest has starred items
 */
export function GuestInterestsBadge({ entryId }: GuestInterestsBadgeProps) {
  const [showModal, setShowModal] = useState(false);
  const { data: interests, isLoading } = useGetGuestInterestsQuery(entryId);

  // Don't show anything if no interests or loading
  if (isLoading || !interests) {
    return null;
  }

  const hasInterests = interests.starred_count > 0 || interests.preorder_count > 0;

  if (!hasInterests) {
    return null;
  }

  // Build compact summary text
  const buildSummaryText = () => {
    const items: string[] = [];

    // Add preorder items first (more important)
    if (interests.preorder_count > 0) {
      interests.preorder_summary.forEach((item) => {
        items.push(`${item.quantity}x ${item.item_name}`);
      });
    }

    // Add starred items
    if (interests.starred_count > 0 && interests.starred_items.length > 0) {
      items.push(...interests.starred_items);
    }

    if (items.length === 0) {
      return 'No items';
    }

    // Show first 2 items, then "+X more" if needed
    const maxShow = 2;
    const shown = items.slice(0, maxShow);
    const remaining = items.length - maxShow;

    let text = shown.join(', ');
    if (remaining > 0) {
      text += ` (+${remaining} more)`;
    }

    return text;
  };

  const summaryText = buildSummaryText();
  const hasPreorder = interests.preorder_count > 0;

  return (
    <>
      <TouchableOpacity
        style={[styles.badge, hasPreorder && styles.preorderBadge]}
        onPress={() => setShowModal(true)}
        accessibilityLabel="View guest interests"
        accessibilityHint="Opens modal with full list of interested items"
      >
        <Text style={styles.icon}>{hasPreorder ? '\u{1F37D}' : '\u2B50'}</Text>
        <Text style={styles.badgeText} numberOfLines={1}>
          {hasPreorder ? 'Pre-order: ' : 'Interested: '}
          {summaryText}
        </Text>
      </TouchableOpacity>

      <Modal
        visible={showModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Guest Interests</Text>
              <TouchableOpacity
                onPress={() => setShowModal(false)}
                style={styles.closeButton}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* Pre-order Section */}
              {interests.preorder_count > 0 && (
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>
                    Pre-Order ({interests.preorder_count} items)
                  </Text>
                  {interests.preorder_summary.map((item, index) => (
                    <View key={index} style={styles.itemRow}>
                      <Text style={styles.itemQuantity}>{item.quantity}x</Text>
                      <Text style={styles.itemName}>{item.item_name}</Text>
                    </View>
                  ))}
                </View>
              )}

              {/* Starred Section */}
              {interests.starred_count > 0 && (
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>
                    Starred Items ({interests.starred_count})
                  </Text>
                  {interests.starred_items.map((name, index) => (
                    <View key={index} style={styles.itemRow}>
                      <Text style={styles.starIcon}>{'\u2B50'}</Text>
                      <Text style={styles.itemName}>{name}</Text>
                    </View>
                  ))}
                </View>
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3CD',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
    marginTop: 8,
    alignSelf: 'flex-start',
  },
  preorderBadge: {
    backgroundColor: '#D4EDDA',
  },
  icon: {
    fontSize: 14,
  },
  badgeText: {
    fontSize: 12,
    color: '#333',
    maxWidth: 200,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    width: '90%',
    maxWidth: 400,
    maxHeight: '80%',
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  closeButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
  },
  closeButtonText: {
    fontSize: 14,
    color: '#666',
  },
  modalBody: {
    padding: 16,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  itemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    marginBottom: 4,
  },
  itemQuantity: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    minWidth: 32,
  },
  starIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  itemName: {
    fontSize: 14,
    color: '#333',
    flex: 1,
  },
});
