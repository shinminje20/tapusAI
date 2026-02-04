import { baseApi } from './api';

/**
 * Waitlist entry types matching backend schemas
 * See: backend/app/api/v1/schemas/waitlist.py
 */
export type WaitlistStatus = 'waiting' | 'seated' | 'canceled' | 'no_show';

export interface WaitlistEntry {
  id: number;
  guest_id: number;
  guest_name: string | null;
  guest_phone: string | null;
  party_size: number;
  status: WaitlistStatus;
  position: number;
  vip_flag: boolean;
  source: string;
  created_at: string;
  updated_at: string;
  eta_minutes: number | null;
}

/**
 * Request type for status updates
 * AC-WL-003: Status transitions (waiting -> seated/canceled/no_show)
 */
export interface UpdateStatusRequest {
  entryId: number;
  status: WaitlistStatus;
}

/**
 * Request type for VIP toggle
 * AC-WL-006: VIP flagging
 */
export interface ToggleVipRequest {
  entryId: number;
  vip: boolean;
}

/**
 * Request type for reordering
 * AC-WL-005: Reordering updates position
 */
export interface ReorderEntriesRequest {
  entry_ids: number[];
}

/**
 * Waitlist API endpoints for admin waitlist management
 *
 * REQ-WL-002: Real-time waitlist updates across devices
 * REQ-WL-003: Estimated wait time calculation
 * REQ-WL-004: Ability to reorder, prioritize, or mark VIP guests
 * REQ-WL-005: Status tracking
 */
export const waitlistApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    /**
     * Get all waiting entries
     * GET /api/v1/waitlist/
     * REQ-WL-002: Real-time queue display
     */
    getWaitlist: builder.query<WaitlistEntry[], void>({
      query: () => '/waitlist/',
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Waitlist' as const, id })),
              { type: 'Waitlist', id: 'LIST' },
            ]
          : [{ type: 'Waitlist', id: 'LIST' }],
    }),

    /**
     * Update entry status
     * PATCH /api/v1/waitlist/{id}/status
     * AC-WL-003: Status transitions (waiting -> seated/canceled/no_show)
     */
    updateStatus: builder.mutation<WaitlistEntry, UpdateStatusRequest>({
      query: ({ entryId, status }) => ({
        url: `/waitlist/${entryId}/status`,
        method: 'PATCH',
        body: { status },
      }),
      invalidatesTags: (result, error, { entryId }) => [
        { type: 'Waitlist', id: entryId },
        { type: 'Waitlist', id: 'LIST' },
      ],
    }),

    /**
     * Toggle VIP flag
     * PATCH /api/v1/waitlist/{id}/vip
     * AC-WL-006: VIP flagging - informational flag, manual move only
     */
    toggleVip: builder.mutation<WaitlistEntry, ToggleVipRequest>({
      query: ({ entryId, vip }) => ({
        url: `/waitlist/${entryId}/vip`,
        method: 'PATCH',
        params: { vip },
      }),
      invalidatesTags: (result, error, { entryId }) => [
        { type: 'Waitlist', id: entryId },
        { type: 'Waitlist', id: 'LIST' },
      ],
    }),

    /**
     * Reorder waitlist entries
     * POST /api/v1/waitlist/reorder
     * AC-WL-005: Reordering updates position deterministically
     */
    reorderEntries: builder.mutation<WaitlistEntry[], ReorderEntriesRequest>({
      query: (body) => ({
        url: '/waitlist/reorder',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Waitlist', id: 'LIST' }],
    }),
  }),
});

// Export hooks for usage in components
export const {
  useGetWaitlistQuery,
  useUpdateStatusMutation,
  useToggleVipMutation,
  useReorderEntriesMutation,
} = waitlistApi;
