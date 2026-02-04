import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL, API_TIMEOUT_MS, ACCESS_TOKEN_KEY } from '../app/constants';

/**
 * Custom base query with authentication header injection
 * Reads access token from AsyncStorage and adds to Authorization header
 */
const baseQueryWithAuth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  // Get token from storage
  const token = await AsyncStorage.getItem(ACCESS_TOKEN_KEY);

  // Create the base query
  const rawBaseQuery = fetchBaseQuery({
    baseUrl: API_URL,
    timeout: API_TIMEOUT_MS,
    prepareHeaders: (headers) => {
      headers.set('Content-Type', 'application/json');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  });

  return rawBaseQuery(args, api, extraOptions);
};

/**
 * Base RTK Query API configuration for Admin app
 * Includes authentication header injection
 * All API slices should use injectEndpoints on this base
 */
export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithAuth,
  tagTypes: ['Waitlist', 'User', 'Notification', 'Template'],
  endpoints: () => ({}),
});
