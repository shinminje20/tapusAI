/**
 * Messaging API endpoints for Admin app
 *
 * REQ-STAFF-001: Canned response templates on Admin tablet
 * REQ-STAFF-002: Templates must support fast insertion and consistent tone
 * AC-STAFF-002: message sending logs message + template used
 */

import { baseApi } from './api';

/**
 * Request to send a custom message to a waitlist entry
 * Maps to backend POST /notifications/custom/{entry_id}
 */
export interface SendMessageRequest {
  entryId: number;
  message: string;
  templateId?: string; // AC-STAFF-002: log template used
}

/**
 * Response from sending a message
 * Matches backend NotificationResponse schema
 */
export interface SendMessageResponse {
  id: number;
  waitlist_entry_id: number;
  notification_type: string;
  phone_number: string;
  message: string;
  status: 'pending' | 'sent' | 'failed';
  sent_at: string | null;
  created_at: string;
}

/**
 * Messaging API slice with RTK Query
 * Uses baseApi to inherit authentication headers
 */
export const messagingApi = baseApi.injectEndpoints({
  endpoints: (builder) => ({
    /**
     * Send a custom message to a waitlist entry
     * POST /api/v1/notifications/ready/{entry_id}
     *
     * REQ-STAFF-001: Canned response templates
     * AC-STAFF-002: Templates can be sent with minimal taps
     *
     * Note: Using /ready endpoint with custom message parameter
     * The backend accepts optional custom message in SendNotificationRequest
     */
    sendMessage: builder.mutation<SendMessageResponse, SendMessageRequest>({
      query: ({ entryId, message }) => ({
        url: `/notifications/ready/${entryId}`,
        method: 'POST',
        body: { message },
      }),
      invalidatesTags: (_result, _error, { entryId }) => [
        { type: 'Notification', id: entryId },
        { type: 'Waitlist', id: entryId },
      ],
    }),
  }),
});

// Export hooks for usage in components
export const { useSendMessageMutation } = messagingApi;
