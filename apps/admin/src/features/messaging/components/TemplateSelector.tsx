/**
 * Template selector component for staff messaging
 *
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * REQ-STAFF-002: Templates must support fast insertion and consistent tone
 * AC-STAFF-002: Templates can be inserted with minimal taps/clicks
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
} from 'react-native';
import type { MessageTemplate } from '../templates';

interface TemplateSelectorProps {
  templates: readonly MessageTemplate[];
  selectedId: string | null;
  onSelect: (template: MessageTemplate) => void;
}

/**
 * Grid/list of template chips for quick selection
 * Tap template -> highlight selected
 *
 * AC-STAFF-002: Fast to send (tap template = 1st tap of 2-tap flow)
 */
export function TemplateSelector({
  templates,
  selectedId,
  onSelect,
}: TemplateSelectorProps) {
  const renderTemplate = ({ item }: { item: MessageTemplate }) => {
    const isSelected = item.id === selectedId;

    return (
      <TouchableOpacity
        style={[
          styles.templateChip,
          isSelected && styles.templateChipSelected,
        ]}
        onPress={() => onSelect(item)}
        activeOpacity={0.7}
        accessibilityRole="button"
        accessibilityState={{ selected: isSelected }}
        accessibilityLabel={`Template: ${item.label}`}
        accessibilityHint="Tap to select this message template"
      >
        <Text
          style={[
            styles.templateLabel,
            isSelected && styles.templateLabelSelected,
          ]}
        >
          {item.label}
        </Text>
        <Text
          style={[
            styles.templatePreview,
            isSelected && styles.templatePreviewSelected,
          ]}
          numberOfLines={2}
        >
          {item.message}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Quick Templates</Text>
      <FlatList
        data={templates}
        renderItem={renderTemplate}
        keyExtractor={(item) => item.id}
        numColumns={1}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 12,
  },
  listContent: {
    paddingBottom: 8,
  },
  templateChip: {
    backgroundColor: '#F5F5F5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  templateChipSelected: {
    backgroundColor: '#E3F2FD',
    borderColor: '#007AFF',
  },
  templateLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 4,
  },
  templateLabelSelected: {
    color: '#007AFF',
  },
  templatePreview: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 20,
  },
  templatePreviewSelected: {
    color: '#555555',
  },
});
