# Session Context - Phase 2 Kiosk App Implementation

**Last Updated:** 2026-02-02
**Session Status:** ✅ Code Complete + Code Reviewed + Fixes Applied | Pending: git commit, npm install, test

---

## IMMEDIATE ACTION REQUIRED

```bash
# 1. Git commit (code reviewed and fixes applied)
cd /Users/minjaeshin/Desktop/project/tapusAi
git add .
git commit -m "feat(kiosk): implement React Native kiosk app [REQ-DEV-001, REQ-WL-001]

- Add Expo project with Redux Toolkit + RTK Query
- Add waitlist API (addGuest mutation, getEta query) [AC-WL-008]
- Add validation utilities to @tapus/core (20 tests) [AC-WL-002]
- Add UI components: Button, TextInput, NumberPicker
- Add screens: Welcome, Registration, Confirmation [AC-WL-001]
- Add KioskNavigator with auto-reset timeout
- Add ErrorBoundary and LoadingOverlay for polish
- Improved error handling (network, timeout, server errors)
- Fixed: PhoneInput onBlur, API response types match backend

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

# 2. Install dependencies
npm install

# 3. Run tests
npm run test:core   # Expect: 20 passing
npm run test:kiosk  # Expect: 9 passing

# 4. Start app
cd apps/kiosk && npx expo start

# 5. Send Telegram notification
export $(grep -v '^#' .env | xargs) && tools/notify_telegram.sh "✅ Phase 2 Kiosk App committed and ready for testing"
```

---

## Project Overview

**tapusAI** - Restaurant waitlist SaaS with dual tablets (kiosk + admin), offline-first sync, SMS notifications.

| Phase | Status |
|-------|--------|
| Phase 1: Backend | ✅ Complete (45 tests) |
| Phase 2: Kiosk App | ✅ Code Complete (pending commit) |

---

## Code Review Summary (Completed)

### Issues Fixed This Session:
1. ✅ **PhoneInput onBlur** - Added `onBlur` prop, wired in GuestForm
2. ✅ **API type mismatch** - Updated `WaitlistEntryResponse` to match backend:
   - `name` → `guest_name`
   - `is_vip` → `vip_flag`
   - `check_in_time` → `created_at`
   - Added `guest_id`, `updated_at`
   - Fixed `EtaResponse.entry_id`

### Requirements Verified:
- [x] AC-WL-001: Entry appears with status 'waiting'
- [x] AC-WL-002: Validation (name, phone required, party_size >= 1)
- [x] AC-WL-008: Source='kiosk' hardcoded
- [x] AC-DEV-002: No admin routes in kiosk

### Should Fix Later (Non-blocking):
- Add integration tests for source='kiosk' injection
- Add tests for error handling scenarios
- Add mounted ref check in ConfirmationScreen timeout
- Consider stricter phone regex
- Add debounce on form submission

---

## File Structure

```
apps/kiosk/
├── App.tsx                     # Entry + Redux + ErrorBoundary + StatusBar
├── index.ts                    # Expo entry
├── app.json                    # Expo config
├── babel.config.js
├── metro.config.js             # Monorepo support
├── tsconfig.json
├── jest.config.js
├── package.json                # All deps "latest"
└── src/
    ├── app/
    │   ├── store.ts            # Redux + RTK Query
    │   └── constants.ts        # API_URL, KIOSK_SOURCE, timeouts
    ├── components/
    │   ├── ErrorBoundary.tsx   # Error catch + reset
    │   ├── LoadingOverlay.tsx  # Full-screen loading modal
    │   └── index.ts
    ├── services/
    │   ├── api.ts              # RTK Query base
    │   ├── waitlistApi.ts      # addGuest, getEta (types match backend)
    │   └── __tests__/waitlistApi.test.ts
    ├── navigation/
    │   └── KioskNavigator.tsx  # Welcome → Registration → Confirmation
    └── features/registration/
        ├── screens/
        │   ├── WelcomeScreen.tsx
        │   ├── RegistrationScreen.tsx  # + LoadingOverlay + error handling
        │   ├── ConfirmationScreen.tsx  # + 30s auto-reset
        │   └── index.ts
        ├── components/
        │   ├── GuestForm.tsx           # + onBlur for all fields
        │   ├── PhoneInput.tsx          # + onBlur prop (FIXED)
        │   ├── PartySizeSelector.tsx
        │   └── index.ts
        └── __tests__/GuestForm.test.tsx

packages/core/
├── package.json
├── jest.config.js
├── tsconfig.json
└── src/
    ├── index.ts                # Types + validation exports
    └── validation/
        ├── index.ts            # validateName, validatePhone, validatePartySize
        └── __tests__/validation.test.ts  # 20 tests

packages/ui/
└── src/
    ├── index.tsx               # Button, TextInput, NumberPicker exports
    └── components/
        ├── Button.tsx          # Large touch (48/56/72px), loading
        ├── TextInput.tsx       # 56px, validation error
        └── NumberPicker.tsx    # +/- buttons
```

---

## API Types (Match Backend)

```typescript
// apps/kiosk/src/services/waitlistApi.ts

interface WaitlistEntryResponse {
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
  guest_name: string | null;
  guest_phone: string | null;
}

interface EtaResponse {
  entry_id: number;
  eta_minutes: number | null;
}
```

---

## Screen Flow

```
Welcome → Registration → Confirmation → (30s auto-reset) → Welcome
   │           │              │
   │     Name/Phone/Size      │
   │     [Join Waitlist]   Position + ETA
   │                       [Done]
```

---

## Test Summary

| Package | Tests | Status |
|---------|-------|--------|
| packages/core | 20 | Passing (before shell issue) |
| apps/kiosk | 9 | Passing (before shell issue) |

---

## Task Status

| Task | Description | Status |
|------|-------------|--------|
| 2.1 | Expo Project Setup | ✅ Complete |
| 2.2 | Redux Store & API | ✅ Complete |
| 2.3 | Validation Utils | ✅ Complete (20 tests) |
| 2.4 | UI Components | ✅ Complete |
| 2.5 | Screens & Nav | ✅ Complete (9 tests) |
| 2.6 | Integration & Polish | ✅ Complete |
| - | Code Review | ✅ Complete |
| - | Review Fixes | ✅ Complete |

---

## Git Status

- **Phase 1:** Merged to main (commit 1ad4178)
- **Phase 2:** All code in working directory, NOT YET COMMITTED
- **Action:** Commit required (see top of this file)

---

## Key Files Modified After Review

1. `apps/kiosk/src/features/registration/components/PhoneInput.tsx` - Added onBlur
2. `apps/kiosk/src/features/registration/components/GuestForm.tsx` - Pass onBlur to PhoneInput
3. `apps/kiosk/src/services/waitlistApi.ts` - Fixed types to match backend
4. `apps/kiosk/src/features/registration/screens/RegistrationScreen.tsx` - Use guest_name

---

## Business Rules

- Guest fields: name, phone_number, party_size ALL REQUIRED
- VIP priority: Manual move only
- ETA algorithm: position × avg_turn_time
- Dependencies: Always use "latest" versions
- Source: Always 'kiosk' for kiosk app [AC-WL-008]

---

## Known Issues

1. **Shell Environment** - Bash commands returned exit code 1 (session issue)
2. **Jest Transforms** - ESM modules need transformIgnorePatterns (configured)
3. **Peer Deps** - Removed @testing-library/jest-native due to conflicts

---

## Related Files

- `/logs/WORKLOG.md` - Work history
- `/logs/tasks/TASKS.md` - Task state
- `/logs/plan/PHASE2_KIOSK_APP.md` - Full plan

---

## Next Phase (After Commit)

1. Test kiosk app on simulator/device
2. Test with backend API running
3. Phase 3: Admin app or additional features
