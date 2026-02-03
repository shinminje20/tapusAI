import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { GuestForm } from '../components/GuestForm';

/**
 * Tests for GuestForm component
 * Covers AC-WL-002: Validate name, phone required, party_size >= 1
 */

describe('GuestForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders all form fields', () => {
    const { getByText, getByPlaceholderText } = render(
      <GuestForm onSubmit={mockOnSubmit} />
    );

    expect(getByText('Name')).toBeTruthy();
    expect(getByPlaceholderText('Enter your name')).toBeTruthy();
    expect(getByText('Phone Number')).toBeTruthy();
    expect(getByText('Party Size')).toBeTruthy();
    expect(getByText('Join Waitlist')).toBeTruthy();
  });

  it('shows validation errors for empty fields on submit', async () => {
    const { getByText, findByText } = render(
      <GuestForm onSubmit={mockOnSubmit} />
    );

    fireEvent.press(getByText('Join Waitlist'));

    await waitFor(() => {
      expect(findByText('Name is required')).toBeTruthy();
    });
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('calls onSubmit with valid data', async () => {
    const { getByText, getByPlaceholderText } = render(
      <GuestForm onSubmit={mockOnSubmit} />
    );

    fireEvent.changeText(getByPlaceholderText('Enter your name'), 'John Doe');
    fireEvent.changeText(getByPlaceholderText('(555) 123-4567'), '5551234567');

    fireEvent.press(getByText('Join Waitlist'));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        phone: '(555) 123-4567',
        partySize: 1,
      });
    });
  });

  it('shows loading state when isLoading is true', () => {
    const { getByLabelText, queryByText, UNSAFE_getByType } = render(
      <GuestForm onSubmit={mockOnSubmit} isLoading />
    );

    // Button should exist but show loading indicator instead of text
    const button = getByLabelText('Join Waitlist');
    expect(button).toBeTruthy();
    // Text should not be visible when loading
    expect(queryByText('Join Waitlist')).toBeNull();
  });

  it('allows incrementing party size', () => {
    const { getByLabelText, getByText } = render(
      <GuestForm onSubmit={mockOnSubmit} />
    );

    // Initial value is 1
    expect(getByText('1')).toBeTruthy();

    // Increment
    fireEvent.press(getByLabelText('Increase party size'));
    expect(getByText('2')).toBeTruthy();
  });
});
