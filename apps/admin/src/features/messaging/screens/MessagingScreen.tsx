/**
 * Messaging screen for sending templates to guests
 *
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * REQ-STAFF-002: Templates must support fast insertion and consistent tone
 * AC-STAFF-001: Canned templates available in admin UI
 * AC-STAFF-002: Templates can be inserted with minimal taps/clicks (2 taps max)
 *
 * UX Flow (2 taps per AC-STAFF-002):
 * 1. Tap template -> selects and shows preview
 * 2. Tap Send -> message sent, return to waitlist
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Alert,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import { TemplateSelector, MessagePreview } from '../components';
import { DEFAULT_TEMPLATES, type MessageTemplate } from '../templates';
import { useSendMessageMutation } from '../../../services/messagingApi';

/**
 * Navigation params for MessagingScreen
 * Expects guest info from WaitlistItem
 */
export type MessagingScreenParams = {
  entryId: number;
  guestName: string;
  phoneNumber: string;
};

// Define the navigation types locally (will be integrated with admin navigator later)
type RootStackParamList = {
  Messaging: MessagingScreenParams;
  [key: string]: object | undefined;
};

type Props = NativeStackScreenProps<RootStackParamList, 'Messaging'>;

/**
 * MessagingScreen - Staff sends messages to guests
 *
 * AC-STAFF-001: Staff can select templates
 * AC-STAFF-002: 2 taps max to send (select template + send)
 */
export function MessagingScreen({ route, navigation }: Props) {
  const { entryId, guestName, phoneNumber } = route.params;

  // State
  const [selectedTemplate, setSelectedTemplate] = useState<MessageTemplate | null>(null);
  const [customMessage, setCustomMessage] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  // API mutation
  const [sendMessage, { isLoading: isSending }] = useSendMessageMutation();

  // Get the message to send (template or custom)
  const messageToSend = selectedTemplate?.message || customMessage;

  // Handle template selection (1st tap)
  const handleTemplateSelect = useCallback((template: MessageTemplate) => {
    setSelectedTemplate(template);
    setCustomMessage(''); // Clear custom when template selected
    setShowPreview(true); // Immediately show preview for 2-tap flow
  }, []);

  // Handle custom message input
  const handleCustomMessageChange = useCallback((text: string) => {
    setCustomMessage(text);
    setSelectedTemplate(null); // Clear template when typing custom
    setShowPreview(false);
  }, []);

  // Show preview for custom message
  const handlePreviewCustom = useCallback(() => {
    if (customMessage.trim()) {
      setShowPreview(true);
    }
  }, [customMessage]);

  // Cancel preview
  const handleCancelPreview = useCallback(() => {
    setShowPreview(false);
    setSelectedTemplate(null);
  }, []);

  // Send message (2nd tap)
  const handleSend = useCallback(async () => {
    if (!messageToSend.trim()) {
      Alert.alert('Error', 'Please select a template or enter a message.');
      return;
    }

    try {
      await sendMessage({
        entryId,
        message: messageToSend,
        templateId: selectedTemplate?.id, // AC-STAFF-002: log template used
      }).unwrap();

      // Success - show confirmation and go back
      Alert.alert(
        'Message Sent',
        `Message sent to ${guestName}.`,
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ],
        { cancelable: false }
      );
    } catch (error) {
      // Handle error
      let errorMessage = 'Failed to send message. Please try again.';
      if (error && typeof error === 'object') {
        if ('status' in error && error.status === 409) {
          errorMessage = 'A notification was already sent recently. Please wait before sending another.';
        } else if ('data' in error) {
          const data = error as { data?: { detail?: string } };
          if (data.data?.detail) {
            errorMessage = data.data.detail;
          }
        }
      }
      Alert.alert('Send Failed', errorMessage);
    }
  }, [entryId, messageToSend, selectedTemplate, guestName, navigation, sendMessage]);

  // Handle back navigation
  const handleBack = useCallback(() => {
    navigation.goBack();
  }, [navigation]);

  return (
    <SafeAreaView style={styles.container} edges={['top', 'left', 'right']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            onPress={handleBack}
            style={styles.backButton}
            accessibilityRole="button"
            accessibilityLabel="Go back"
          >
            <Text style={styles.backButtonText}>Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Send Message</Text>
          <View style={styles.headerSpacer} />
        </View>

        {/* Guest Info */}
        <View style={styles.guestInfoBar}>
          <Text style={styles.guestInfoLabel}>To:</Text>
          <Text style={styles.guestInfoName}>{guestName}</Text>
        </View>

        {/* Message Preview (when template selected or previewing custom) */}
        {showPreview && messageToSend && (
          <View style={styles.previewSection}>
            <MessagePreview
              guestName={guestName}
              phoneNumber={phoneNumber}
              message={messageToSend}
              onSend={handleSend}
              onCancel={handleCancelPreview}
              isSending={isSending}
            />
          </View>
        )}

        {/* Template Selector (hidden when showing preview) */}
        {!showPreview && (
          <>
            <View style={styles.templatesSection}>
              <TemplateSelector
                templates={DEFAULT_TEMPLATES}
                selectedId={selectedTemplate?.id ?? null}
                onSelect={handleTemplateSelect}
              />
            </View>

            {/* Custom Message Input */}
            <View style={styles.customSection}>
              <Text style={styles.sectionTitle}>Or Write Custom Message</Text>
              <TextInput
                style={styles.customInput}
                value={customMessage}
                onChangeText={handleCustomMessageChange}
                placeholder="Type your custom message..."
                placeholderTextColor="#999999"
                multiline
                numberOfLines={4}
                maxLength={500}
                textAlignVertical="top"
                accessibilityLabel="Custom message input"
                accessibilityHint="Type a custom message to send to the guest"
              />
              {customMessage.trim().length > 0 && (
                <TouchableOpacity
                  style={styles.previewButton}
                  onPress={handlePreviewCustom}
                  activeOpacity={0.7}
                  accessibilityRole="button"
                  accessibilityLabel="Preview custom message"
                >
                  <Text style={styles.previewButtonText}>Preview Message</Text>
                </TouchableOpacity>
              )}
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  backButton: {
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  backButtonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#333333',
    textAlign: 'center',
  },
  headerSpacer: {
    width: 50, // Match backButton width for centering
  },
  guestInfoBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 12,
    marginBottom: 20,
  },
  guestInfoLabel: {
    fontSize: 14,
    color: '#666666',
    marginRight: 8,
  },
  guestInfoName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
  },
  previewSection: {
    marginBottom: 20,
  },
  templatesSection: {
    marginBottom: 24,
  },
  customSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 12,
  },
  customInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#333333',
    minHeight: 120,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  previewButton: {
    marginTop: 12,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 8,
    backgroundColor: '#007AFF',
    alignItems: 'center',
  },
  previewButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});
