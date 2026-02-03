import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { API_URL, API_TIMEOUT_MS } from '../app/constants';

/**
 * Base RTK Query API configuration
 * All API slices should use this as their base
 */
export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: API_URL,
    timeout: API_TIMEOUT_MS,
    prepareHeaders: (headers) => {
      headers.set('Content-Type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Waitlist'],
  endpoints: () => ({}),
});
