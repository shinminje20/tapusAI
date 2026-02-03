import { baseApi } from './api';
import { KIOSK_SOURCE } from '../app/constants';

/**
 * API request types (matching backend schemas)
 */
export interface AddGuestRequest {
  name: string;
  phone_number: string;
  party_size: number;
  source: typeof KIOSK_SOURCE;
}

/**
 * API response types (matching backend schemas)
 * See: backend/app/api/v1/schemas/waitlist.py
 */
export interface WaitlistEntryResponse {
  id: number;
  guest_id: number;
  party_size: number;
  status: 'waiting' | 'seated' | 'canceled' | 'no_show';
  position: number;
  vip_flag: boolean;
  source: string;
  created_at: string;
  updated_at: string;
  eta_minutes: number | null;
  // Nested guest info for display
  guest_name: string | null;
  guest_phone: string | null;
}

export interface EtaResponse {
  entry_id: number;
  eta_minutes: number | null;
}

/**
 * Waitlist API endpoints for kiosk guest registration
 */
export const waitlistApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    /**
     * Add a new guest to the waitlist
     * POST /api/v1/waitlist/
     */
    addGuest: builder.mutation<WaitlistEntryResponse, Omit<AddGuestRequest, 'source'>>({
      query: (guest) => ({
        url: '/waitlist/',
        method: 'POST',
        body: {
          ...guest,
          source: KIOSK_SOURCE, // Always set source to 'kiosk' [AC-WL-008]
        },
      }),
      invalidatesTags: ['Waitlist'],
    }),

    /**
     * Get current ETA for a waitlist entry
     * GET /api/v1/waitlist/{id}/eta
     */
    getEta: builder.query<EtaResponse, number>({
      query: (id) => `/waitlist/${id}/eta`,
      providesTags: (result, error, id) => [{ type: 'Waitlist', id }],
    }),
  }),
});

// Export hooks for usage in components
export const { useAddGuestMutation, useGetEtaQuery } = waitlistApi;
