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
 */
export interface WaitlistEntryResponse {
  id: number;
  name: string;
  phone_number: string;
  party_size: number;
  position: number;
  eta_minutes: number | null;
  status: 'waiting' | 'seated' | 'canceled' | 'no_show';
  source: string;
  check_in_time: string;
  notes: string | null;
  is_vip: boolean;
}

export interface EtaResponse {
  id: number;
  position: number;
  eta_minutes: number | null;
  status: string;
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
