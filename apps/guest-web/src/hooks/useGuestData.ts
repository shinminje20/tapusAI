/**
 * React Query hooks for guest data.
 *
 * REQ-MENU-005: Guest data fetching
 * AC-MENU-001: Guest context access
 * AC-MENU-002: Star functionality
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getGuestContext,
  getGuestMenu,
  getGuestInterests,
  starItem,
  addPreorder,
  removePreorder,
  type GuestContext,
  type MenuResponse,
  type GuestInterestsResponse,
} from '../services/api';

/**
 * Hook for guest context (waitlist status).
 */
export function useGuestContext(token: string) {
  return useQuery<GuestContext, Error>({
    queryKey: ['guestContext', token],
    queryFn: () => getGuestContext(token),
    enabled: !!token,
  });
}

/**
 * Hook for menu data.
 */
export function useGuestMenu(token: string) {
  return useQuery<MenuResponse, Error>({
    queryKey: ['guestMenu', token],
    queryFn: () => getGuestMenu(token),
    enabled: !!token,
  });
}

/**
 * Hook for guest interests (starred/preorder items).
 */
export function useGuestInterests(token: string) {
  return useQuery<GuestInterestsResponse, Error>({
    queryKey: ['guestInterests', token],
    queryFn: () => getGuestInterests(token),
    enabled: !!token,
  });
}

/**
 * Hook for starring/unstarring items.
 */
export function useStarItem(token: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ menuItemId, starred }: { menuItemId: number; starred: boolean }) =>
      starItem(token, menuItemId, starred),
    onSuccess: () => {
      // Invalidate interests to refetch
      queryClient.invalidateQueries({ queryKey: ['guestInterests', token] });
    },
  });
}

/**
 * Hook for adding to preorder.
 */
export function useAddPreorder(token: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ menuItemId, quantity }: { menuItemId: number; quantity?: number }) =>
      addPreorder(token, menuItemId, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guestInterests', token] });
    },
  });
}

/**
 * Hook for removing from preorder.
 */
export function useRemovePreorder(token: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (menuItemId: number) => removePreorder(token, menuItemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guestInterests', token] });
    },
  });
}
