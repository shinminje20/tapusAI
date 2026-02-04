import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { VIPBadge } from '../components/VIPBadge';

/**
 * Tests for VIPBadge component
 * AC-WL-006: VIP flagging
 * - Visibly indicated as VIP in admin UI
 * - VIP status persists
 * - Tap to toggle VIP status
 */

describe('VIPBadge', () => {
  const mockOnToggle = jest.fn();

  beforeEach(() => {
    mockOnToggle.mockClear();
  });

  describe('rendering', () => {
    it('renders VIP text', () => {
      const { getByText } = render(
        <VIPBadge isVip={false} onToggle={mockOnToggle} />
      );
      expect(getByText('VIP')).toBeTruthy();
    });

    it('renders filled star when VIP is active', () => {
      const { getByText } = render(
        <VIPBadge isVip={true} onToggle={mockOnToggle} />
      );
      // Unicode filled star
      expect(getByText('\u2605')).toBeTruthy();
    });

    it('renders empty star when VIP is inactive', () => {
      const { getByText } = render(
        <VIPBadge isVip={false} onToggle={mockOnToggle} />
      );
      // Unicode empty star
      expect(getByText('\u2606')).toBeTruthy();
    });
  });

  describe('interaction', () => {
    it('calls onToggle when pressed', () => {
      const { getByRole } = render(
        <VIPBadge isVip={false} onToggle={mockOnToggle} />
      );

      const button = getByRole('button');
      fireEvent.press(button);

      expect(mockOnToggle).toHaveBeenCalledTimes(1);
    });

    it('does not call onToggle when disabled', () => {
      const { getByRole } = render(
        <VIPBadge isVip={false} onToggle={mockOnToggle} disabled={true} />
      );

      const button = getByRole('button');
      fireEvent.press(button);

      expect(mockOnToggle).not.toHaveBeenCalled();
    });
  });

  describe('accessibility', () => {
    it('has correct label when VIP is active', () => {
      const { getByLabelText } = render(
        <VIPBadge isVip={true} onToggle={mockOnToggle} />
      );
      expect(getByLabelText('Remove VIP status')).toBeTruthy();
    });

    it('has correct label when VIP is inactive', () => {
      const { getByLabelText } = render(
        <VIPBadge isVip={false} onToggle={mockOnToggle} />
      );
      expect(getByLabelText('Mark as VIP')).toBeTruthy();
    });

    it('indicates selected state when VIP is active', () => {
      const { getByRole } = render(
        <VIPBadge isVip={true} onToggle={mockOnToggle} />
      );
      const button = getByRole('button');
      expect(button.props.accessibilityState?.selected).toBe(true);
    });

    it('indicates disabled state when disabled', () => {
      const { getByRole } = render(
        <VIPBadge isVip={false} onToggle={mockOnToggle} disabled={true} />
      );
      const button = getByRole('button');
      expect(button.props.accessibilityState?.disabled).toBe(true);
    });
  });
});
