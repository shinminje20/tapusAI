/**
 * Message preview component before sending
 *
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * AC-STAFF-002: Templates are fast to send (preview + send = 2nd tap)
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';

interface MessagePreviewProps {
  guestName: string;
  phoneNumber: string;
  message: string;
  onSend: () => void;
  onCancel: () => void;
  isSending?: boolean;
}

/**
 * Preview message before sending
 * Shows: guest name, masked phone, message text
 * Actions: Send (2nd tap of 2-tap flow), Cancel
 *
 * AC-STAFF-002: Templates can be inserted with minimal taps/clicks (2 taps max)
 */
export function MessagePreview({
  guestName,
  phoneNumber,
  message,
  onSend,
  onCancel,
  isSending = false,
}: MessagePreviewProps) {
  // Mask phone number for privacy: 555-123-4567 -> ***-***-4567
  const maskedPhone = phoneNumber.length >= 4
    ? `***-***-${phoneNumber.slice(-4)}`
    : '***-***-****';

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Message Preview</Text>

      {/* Guest info */}
      <View style={styles.guestInfo}>
        <Text style={styles.guestName}>{guestName}</Text>
        <Text style={styles.phoneNumber}>{maskedPhone}</Text>
      </View>

      {/* Message text */}
      <View style={styles.messageBox}>
        <Text style={styles.messageText}>{message}</Text>
      </View>

      {/* Action buttons */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={onCancel}
          disabled={isSending}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Cancel sending message"
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.sendButton, isSending && styles.sendButtonDisabled]}
          onPress={onSend}
          disabled={isSending}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Send message"
          accessibilityHint="Tap to send this message to the guest"
        >
          {isSending ? (
            <ActivityIndicator size="small" color="#FFFFFF" />
          ) : (
            <Text style={styles.sendButtonText}>Send Message</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 16,
  },
  guestInfo: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  guestName: {
    fontSize: 20,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 4,
  },
  phoneNumber: {
    fontSize: 14,
    color: '#666666',
  },
  messageBox: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  messageText: {
    fontSize: 16,
    color: '#333333',
    lineHeight: 24,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
  },
  cancelButton: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 8,
    backgroundColor: '#F5F5F5',
    minWidth: 100,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666666',
  },
  sendButton: {
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 8,
    backgroundColor: '#007AFF',
    minWidth: 140,
    alignItems: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.6,
  },
  sendButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
