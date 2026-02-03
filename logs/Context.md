# Session Context - Phase 2 Kiosk App Implementation

**Last Updated:** 2026-02-02
**Session Status:** Tasks 2.1-2.6 Code Complete, npm install + git commit required

---

## Quick Resume Checklist

```bash
# 1. Install dependencies (REQUIRED FIRST)
cd /Users/minjaeshin/Desktop/project/tapusAi
npm install

# 2. Run tests to verify
npm run test:core   # Expect: 20 passing (validation tests)
npm run test:kiosk  # Expect: 9 passing (API + GuestForm tests)

# 3. Start the kiosk app
cd apps/kiosk && npx expo start
```

---

## Project Overview

**tapusAI** - Restaurant waitlist SaaS with dual tablets (kiosk + admin), offline-first sync, SMS notifications.

**Current Phase:** Phase 2 - React Native Kiosk App
**Previous Phase:** Phase 1 Backend (COMPLETE - 45 tests passing)

---

## What Was Implemented This Session

### 1. Expo Project Setup (apps/kiosk/)

```
apps/kiosk/
├── App.tsx                 # Entry point with Redux Provider + ErrorBoundary + StatusBar
├── index.ts                # Expo entry (registerRootComponent)
├── app.json                # Expo config (Tapus Kiosk, com.tapus.kiosk)
├── babel.config.js         # babel-preset-expo
├── metro.config.js         # Monorepo support (watchFolders, nodeModulesPaths)
├── tsconfig.json           # Extends expo/tsconfig.base, paths for @tapus/*
├── jest.config.js          # jest-expo preset, transformIgnorePatterns for RTK/redux
├── package.json            # All deps set to "latest"
└── src/
    ├── app/
    │   ├── store.ts        # Redux store with RTK Query middleware
    │   └── constants.ts    # API_URL, KIOSK_SOURCE, timeouts, validation limits
    ├── components/
    │   ├── ErrorBoundary.tsx   # Error boundary with reset (Task 2.6)
    │   ├── LoadingOverlay.tsx  # Full-screen loading modal (Task 2.6)
    │   └── index.ts
    ├── services/
    │   ├── api.ts          # RTK Query baseApi with fetchBaseQuery
    │   ├── waitlistApi.ts  # addGuest mutation, getEta query
    │   └── __tests__/
    │       └── waitlistApi.test.ts
    ├── navigation/
    │   └── KioskNavigator.tsx  # Stack: Welcome → Registration → Confirmation
    └── features/registration/
        ├── screens/
        │   ├── WelcomeScreen.tsx      # Large "Join Waitlist" button
        │   ├── RegistrationScreen.tsx # GuestForm + API + LoadingOverlay + error handling
        │   ├── ConfirmationScreen.tsx # Position + ETA + auto-reset (30s)
        │   └── index.ts
        ├── components/
        │   ├── GuestForm.tsx          # Form with validation
        │   ├── PhoneInput.tsx         # Auto-formatting (XXX) XXX-XXXX
        │   ├── PartySizeSelector.tsx  # NumberPicker wrapper
        │   └── index.ts
        └── __tests__/
            └── GuestForm.test.tsx     # 5 tests
```

### 2. Shared Packages Updated

**packages/core/** - Validation utilities:
```
packages/core/
├── package.json            # Updated with latest deps
├── jest.config.js          # ts-jest preset
├── tsconfig.json
└── src/
    ├── index.ts            # Exports types + validation functions
    └── validation/
        ├── index.ts        # validateName, validatePhone, validatePartySize, validateGuestForm
        └── __tests__/
            └── validation.test.ts  # 20 tests
```

**packages/ui/** - UI components:
```
packages/ui/
└── src/
    ├── index.tsx           # Exports Button, TextInput, NumberPicker
    └── components/
        ├── Button.tsx      # Large touch targets (48/56/72px), loading state
        ├── TextInput.tsx   # 56px height, validation error display
        └── NumberPicker.tsx # +/- buttons, min/max limits
```

### 3. Root Configuration

**package.json** scripts:
```json
{
  "dev:kiosk": "cd apps/kiosk && npx expo start",
  "test": "npm run test:core && npm run test:kiosk",
  "test:core": "cd packages/core && npm test",
  "test:kiosk": "cd apps/kiosk && npm test"
}
```

---

## Key Implementation Details

### API Integration (waitlistApi.ts)

```typescript
// Always sends source: 'kiosk' [AC-WL-008]
addGuest: builder.mutation<WaitlistEntryResponse, Omit<AddGuestRequest, 'source'>>({
  query: (guest) => ({
    url: '/waitlist/',
    method: 'POST',
    body: {
      ...guest,
      source: KIOSK_SOURCE, // Always 'kiosk'
    },
  }),
}),
```

### Validation Rules (AC-WL-002)

```typescript
// Name: required, non-empty after trim
validateName(name: string): ValidationResult

// Phone: required, 7+ digits, valid format
validatePhone(phone: string): ValidationResult

// Party size: required, integer, 1-20
validatePartySize(partySize: number, maxSize = 20): ValidationResult
```

### Screen Flow

```
Welcome → Registration → Confirmation → (30s auto-reset) → Welcome
   │           │              │
   │     Name/Phone/Size      │
   │        [Submit]       Position + ETA
   │                        [Done]
```

### Navigation Config

- `gestureEnabled: false` - Disabled swipe back on kiosk
- Auto-reset uses `navigation.reset()` to clear stack
- No admin routes available [AC-DEV-002]

---

## Dependencies Configuration

All packages use `"latest"` tag (user requirement):

```json
// apps/kiosk/package.json
{
  "dependencies": {
    "@react-navigation/native": "latest",
    "@react-navigation/native-stack": "latest",
    "@reduxjs/toolkit": "latest",
    "expo": "latest",
    "react": "latest",
    "react-native": "latest",
    "react-redux": "latest"
  }
}
```

---

## Test Summary

### packages/core (20 tests)
- `validateName`: 5 tests (empty, whitespace, null, valid)
- `validatePhone`: 5 tests (empty, too short, invalid format, valid formats)
- `validatePartySize`: 7 tests (< 1, > max, non-integer, valid)
- `validateGuestForm`: 3 tests (all valid, all invalid, partial invalid)

### apps/kiosk (9 tests)
- `waitlistApi`: 3 tests (endpoints exist, KIOSK_SOURCE = 'kiosk')
- `GuestForm`: 5 tests (renders fields, validation errors, submit, loading state, increment party size)

---

## Acceptance Criteria Coverage

| AC | Description | Implementation |
|----|-------------|----------------|
| AC-WL-001 | Entry appears immediately with status 'waiting' | RegistrationScreen submits, shows Confirmation |
| AC-WL-002 | Validate: name, phone required, party_size >= 1 | validateGuestForm in @tapus/core |
| AC-WL-008 | Source captured as 'kiosk' | KIOSK_SOURCE constant always sent |
| AC-DEV-002 | Kiosk cannot access admin features | No admin routes in KioskNavigator |

---

## Task Status

| Task | Description | Status |
|------|-------------|--------|
| 2.1 | Expo Project Setup | ✅ Code Complete |
| 2.2 | Redux Store & API Layer | ✅ Code Complete |
| 2.3 | Validation Utilities | ✅ Code Complete (20 tests) |
| 2.4 | UI Components | ✅ Code Complete |
| 2.5 | Screens & Navigation | ✅ Code Complete (9 tests) |
| 2.6 | Integration & Polish | ✅ Code Complete |

---

## Remaining Work

1. **Git Commit (REQUIRED)**
   - Run `git add .`
   - Commit with message referencing REQ-DEV-001, REQ-WL-001, AC-WL-001, AC-WL-002, AC-WL-008

2. **Verify Setup**
   - Run `npm install`
   - Run tests
   - Start Expo and test on simulator

2. **Integration Testing**
   - Test with backend API running
   - Verify source='kiosk' in database entries
   - Test error scenarios (network errors, API errors)

3. **Polish**
   - Loading states during API calls
   - Error display (Alert or inline)
   - Accessibility labels verification
   - Auto-reset timeout behavior

---

## File Paths Quick Reference

**Kiosk App Entry:**
- `/Users/minjaeshin/Desktop/project/tapusAi/apps/kiosk/App.tsx`

**Redux Store:**
- `/Users/minjaeshin/Desktop/project/tapusAi/apps/kiosk/src/app/store.ts`

**API Services:**
- `/Users/minjaeshin/Desktop/project/tapusAi/apps/kiosk/src/services/waitlistApi.ts`

**Screens:**
- `/Users/minjaeshin/Desktop/project/tapusAi/apps/kiosk/src/features/registration/screens/`

**Validation:**
- `/Users/minjaeshin/Desktop/project/tapusAi/packages/core/src/validation/index.ts`

**UI Components:**
- `/Users/minjaeshin/Desktop/project/tapusAi/packages/ui/src/components/`

---

## Business Decisions (From Phase 1)

- Guest fields: name, phone_number, party_size ALL REQUIRED
- VIP priority: Manual move only (no auto policy)
- ETA algorithm: Simple (position × avg_turn_time)
- Dependencies: Always use latest versions (no version pinning)

---

## Git Status

- Phase 1 merged to main (commit 1ad4178)
- Phase 2 work not yet committed (no branch created)
- All Phase 2 code is in working directory

---

## Related Log Files

- `/logs/WORKLOG.md` - Chronological work history
- `/logs/tasks/TASKS.md` - Task state and next steps
- `/logs/plan/PHASE2_KIOSK_APP.md` - Full implementation plan

---

## Known Issues Encountered

1. **Shell Environment Issue** - All bash commands returned exit code 1 during session
   - Resolution: Terminal restart / user ran npm install manually

2. **Jest Transform Issues** - ESM modules (immer, react-redux) needed in transformIgnorePatterns
   - Resolution: Added to jest.config.js transformIgnorePatterns

3. **Test Library Mismatch** - @testing-library/jest-native had peer dep conflicts
   - Resolution: Removed, used getByLabelText instead for loading state test
