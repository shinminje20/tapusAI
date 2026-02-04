import React from 'react';
import { render } from '@testing-library/react-native';
import { StatusBadge } from '../components/StatusBadge';

/**
 * Tests for StatusBadge component
 * AC-WL-003: Status transitions displayed visually with color coding
 */

describe('StatusBadge', () => {
  describe('rendering', () => {
    it('renders waiting status correctly', () => {
      const { getByText } = render(<StatusBadge status="waiting" />);
      expect(getByText('Waiting')).toBeTruthy();
    });

    it('renders seated status correctly', () => {
      const { getByText } = render(<StatusBadge status="seated" />);
      expect(getByText('Seated')).toBeTruthy();
    });

    it('renders canceled status correctly', () => {
      const { getByText } = render(<StatusBadge status="canceled" />);
      expect(getByText('Canceled')).toBeTruthy();
    });

    it('renders no_show status correctly', () => {
      const { getByText } = render(<StatusBadge status="no_show" />);
      expect(getByText('No Show')).toBeTruthy();
    });
  });

  describe('accessibility', () => {
    it('has accessible label for waiting status', () => {
      const { getByLabelText } = render(<StatusBadge status="waiting" />);
      expect(getByLabelText('Status: Waiting')).toBeTruthy();
    });

    it('has accessible label for seated status', () => {
      const { getByLabelText } = render(<StatusBadge status="seated" />);
      expect(getByLabelText('Status: Seated')).toBeTruthy();
    });

    it('has accessible label for canceled status', () => {
      const { getByLabelText } = render(<StatusBadge status="canceled" />);
      expect(getByLabelText('Status: Canceled')).toBeTruthy();
    });

    it('has accessible label for no_show status', () => {
      const { getByLabelText } = render(<StatusBadge status="no_show" />);
      expect(getByLabelText('Status: No Show')).toBeTruthy();
    });
  });
});
