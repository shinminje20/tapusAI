/**
 * Waitlist feature module exports
 *
 * REQ-WL-002: Real-time waitlist updates across devices
 * REQ-WL-003: Estimated wait time calculation
 * REQ-WL-004: Ability to reorder, prioritize, or mark VIP guests
 * REQ-WL-005: Status tracking
 */

// Screen exports
export { WaitlistScreen } from './screens/WaitlistScreen';

// Component exports
export { WaitlistItem } from './components/WaitlistItem';
export { StatusBadge } from './components/StatusBadge';
export { VIPBadge } from './components/VIPBadge';

// Re-export types for convenience
export type {
  WaitlistEntry,
  WaitlistStatus,
  UpdateStatusRequest,
  ToggleVipRequest,
  ReorderEntriesRequest,
} from '../../services/waitlistApi';
