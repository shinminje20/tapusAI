// Types
export type WaitlistStatus = "waiting" | "seated" | "canceled" | "no_show";
export type WaitlistSource = "walk_in" | "kiosk" | "web" | "other";

export interface GuestInfo {
  name: string;
  phone: string;
}

export interface WaitlistEntry {
  id: string;
  guest: GuestInfo;
  partySize: number;
  status: WaitlistStatus;
  isVip: boolean;
  position: number;
  estimatedWaitMinutes?: number;
  notes?: string;
  source?: WaitlistSource;
  updatedAt?: string;
  version?: number;
}

// Validation exports
export {
  validateName,
  validatePhone,
  validatePartySize,
  validateGuestForm,
  type ValidationResult,
  type GuestFormData,
  type GuestFormErrors,
} from './validation';
