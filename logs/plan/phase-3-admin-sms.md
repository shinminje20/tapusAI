# Phase 3: Admin Tablet App & SMS Notifications

**Status:** In Progress
**Started:** 2026-02-03
**Prerequisites:** Phase 2 (Kiosk App) complete

---

## Overview

Implement the Admin/Host tablet application and SMS notification backend services. This completes the dual-tablet MVP by providing full waitlist management capabilities and guest communication.

---

## Task Breakdown

### Phase 3A: Admin Tablet App

| Task | Description | REQ/AC | Status | Branch |
|------|-------------|--------|--------|--------|
| 3A.1 | Admin Expo Project Setup | REQ-DEV-002 | pending | `feature/REQ-DEV-002-admin-setup` |
| 3A.2 | Authentication & RBAC Backend | REQ-SEC-004, AC-SEC-001 | pending | `feature/REQ-SEC-004-auth` |
| 3A.2b | Authentication Frontend (Admin App) | REQ-SEC-004 | pending | (same branch) |
| 3A.3 | Waitlist Management Screen | AC-WL-003..007 | pending | `feature/AC-WL-003-admin-waitlist` |
| 3A.4 | Staff Messaging Templates | AC-STAFF-001, AC-STAFF-002 | pending | `feature/AC-STAFF-001-templates` |
| 3A.5 | Admin Navigation & Integration | REQ-DEV-002 | pending | `feature/REQ-DEV-002-admin-integration` |

### Phase 3B: SMS Notification Backend

| Task | Description | REQ/AC | Status | Branch |
|------|-------------|--------|--------|--------|
| 3B.1 | SMS Service & Table Ready | REQ-NOTIF-001, AC-NOTIF-001..002 | pending | `feature/REQ-NOTIF-001-sms-ready` |
| 3B.2 | Automated Reminders | REQ-NOTIF-002, AC-NOTIF-003 | pending | `feature/REQ-NOTIF-002-reminders` |

---

## Task 3A.1: Admin Expo Project Setup [REQ-DEV-002]

### Objective
Initialize the Admin tablet Expo app with monorepo support, matching the kiosk app patterns.

### Files to Create

```
apps/admin/
├── package.json              # Dependencies (same stack as kiosk)
├── app.json                  # Expo config for "Tapus Admin"
├── metro.config.js           # Monorepo support
├── babel.config.js           # Babel preset
├── tsconfig.json             # TypeScript with @tapus/* paths
├── jest.config.js            # Jest with jest-expo
├── index.ts                  # Expo entry point
├── App.tsx                   # Main app with Redux Provider
└── src/
    ├── app/
    │   ├── store.ts          # Redux store with RTK Query + authSlice
    │   └── constants.ts      # API URL, timeouts
    ├── services/
    │   └── api.ts            # RTK Query base config (with auth headers)
    ├── components/
    │   ├── ErrorBoundary.tsx
    │   └── index.ts
    └── navigation/
        └── (placeholder)
```

### Dependencies
Same as kiosk app:
- expo, react, react-native (latest)
- @reduxjs/toolkit, react-redux (latest)
- @react-navigation/native, @react-navigation/native-stack (latest)
- @react-native-async-storage/async-storage (latest) - for token storage
- @tapus/core, @tapus/ui (workspace)

### Verification
- `npm run test:admin` passes (basic smoke test)
- Metro bundler starts without errors
- @tapus/core and @tapus/ui imports resolve

---

## Task 3A.2: Authentication & RBAC Backend [REQ-SEC-004, AC-SEC-001]

### Objective
Add JWT authentication to FastAPI with role-based access control.

### Backend Files to Create

```
backend/app/
├── core/
│   ├── security.py           # JWT creation/verification, password hashing
│   └── deps.py               # Auth dependencies (get_current_user, require_role)
├── domain/entities/
│   └── user.py               # User entity with roles
├── api/v1/
│   ├── schemas/
│   │   └── auth.py           # LoginRequest, TokenResponse, UserResponse
│   └── endpoints/
│       └── auth.py           # POST /login, POST /refresh, GET /me
└── infrastructure/repositories/
    └── user_repository.py    # User CRUD operations
```

### Roles
- `host` - Can view/manage waitlist, send messages
- `manager` - Host permissions + settings
- `owner` - Full access

### Endpoints
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/login` | Login with email/password | None |
| POST | `/api/v1/auth/refresh` | Refresh access token | Refresh token |
| GET | `/api/v1/auth/me` | Get current user | Access token |

### Security
- Access token: 15 min expiry
- Refresh token: 7 day expiry
- Password hashing: bcrypt via passlib
- JWT: python-jose with HS256

### Dependencies to Add (requirements.txt)
```
python-jose[cryptography]
passlib[bcrypt]
```

### Verification
- Login with valid credentials returns tokens
- Protected endpoint returns 401 without token
- Protected endpoint returns 403 for insufficient role

---

## Task 3A.2b: Authentication Frontend [REQ-SEC-004]

### Objective
Implement auth flow in Admin app.

### Files to Create

```
apps/admin/src/
├── services/
│   └── authApi.ts            # RTK Query auth endpoints
├── features/auth/
│   ├── authSlice.ts          # Token state, login/logout actions
│   └── screens/
│       └── LoginScreen.tsx   # Email/password form
```

### Token Storage
- Use @react-native-async-storage/async-storage
- Store access token and refresh token
- Auto-inject token in API headers

### Auth Flow
1. App loads → check for stored token
2. If token exists and valid → navigate to Main
3. If token expired → try refresh
4. If no token or refresh fails → navigate to Login

---

## Task 3A.3: Waitlist Management Screen [AC-WL-003..007]

### Objective
Build the main waitlist management interface for hosts.

### Frontend Files

```
apps/admin/src/features/waitlist/
├── screens/
│   ├── WaitlistScreen.tsx    # Main list view
│   └── GuestDetailScreen.tsx # Edit single entry
├── components/
│   ├── WaitlistItem.tsx      # Single entry row
│   ├── StatusBadge.tsx       # Status indicator
│   └── VIPToggle.tsx         # VIP flag toggle
└── __tests__/
    └── WaitlistScreen.test.tsx
```

### Backend Endpoints to Add

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/waitlist` | List all entries (with filters) |
| PATCH | `/api/v1/waitlist/{id}/status` | Update status |
| PATCH | `/api/v1/waitlist/{id}/vip` | Toggle VIP flag |
| PATCH | `/api/v1/waitlist/reorder` | Reorder entries |

### Status Transitions
- `waiting` → `seated`, `canceled`, `no_show`
- `seated` is terminal (cannot change back)

### Features
- [x] Real-time list with pull-to-refresh
- [x] Status badges (color-coded)
- [x] ETA display per entry
- [x] Status change actions (swipe or buttons)
- [x] VIP toggle
- [x] Drag-to-reorder (optional for MVP)

---

## Task 3A.4: Staff Messaging Templates [AC-STAFF-001, AC-STAFF-002]

### Objective
Quick-send canned messages to guests.

### Files

```
apps/admin/src/features/messaging/
├── templates.ts              # Default template definitions
├── screens/
│   └── MessagingScreen.tsx   # Template list + custom message
└── components/
    └── TemplateSelector.tsx  # Quick-select template chips
```

### Default Templates
1. "We're running a bit behind, new estimate is 15–20 mins."
2. "We can't hold your table longer than 10 minutes."
3. "Your table is ready! Please come to the host stand."

### UX
- Tap template → preview → send (2 taps max)
- Templates accessible from WaitlistItem context menu

---

## Task 3A.5: Admin Navigation & Integration [REQ-DEV-002]

### Objective
Wire up navigation with auth guards.

### Files

```
apps/admin/src/navigation/
├── AdminNavigator.tsx        # Main navigator (auth check)
├── AuthNavigator.tsx         # Login stack
└── MainNavigator.tsx         # Protected screens
```

### Navigation Structure
```
RootNavigator
├── AuthNavigator (when not logged in)
│   └── LoginScreen
└── MainNavigator (when logged in)
    ├── WaitlistScreen (default)
    ├── GuestDetailScreen
    └── MessagingScreen
```

### Features
- Auto-redirect to Login on 401
- Auto-logout on token expiry
- Loading state while checking auth

---

## Task 3B.1: SMS Service & Table Ready [REQ-NOTIF-001, AC-NOTIF-001..002]

### Objective
Send "table ready" SMS to guests via Twilio.

### Backend Files

```
backend/app/
├── domain/entities/
│   └── notification.py       # Notification entity (tracks sent messages)
├── infrastructure/sms/
│   ├── base.py               # Abstract SMSAdapter interface
│   ├── twilio_adapter.py     # Twilio implementation
│   └── mock_adapter.py       # Testing mock
├── services/
│   └── notification_service.py  # Business logic
└── api/v1/endpoints/
    └── notifications.py      # API endpoints
```

### SMSAdapter Interface
```python
class SMSAdapter(ABC):
    @abstractmethod
    async def send(self, to: str, message: str) -> bool: ...
```

### NotificationService
- `send_table_ready(entry_id)` - Send "table ready" SMS
- Duplicate prevention: check if already sent for this entry
- Log all sent notifications

### API Endpoint
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/notifications/ready/{entry_id}` | Send table ready SMS |

### Dependencies to Add
```
twilio
```

### Environment Variables
```
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=
```

---

## Task 3B.2: Automated Reminders [REQ-NOTIF-002, AC-NOTIF-003]

### Objective
Automatically send reminder SMS before expected seating.

### Backend Files

```
backend/app/
├── tasks/
│   └── reminder_task.py      # Background task
└── services/
    └── notification_service.py  # Extended with reminder logic
```

### Reminder Logic
- Trigger: X minutes before estimated seating time
- Default: 10 minutes before
- Configurable per location
- Opt-out tracking (guests can reply STOP)

### Implementation Options
1. **Simple polling:** Background task runs every minute, checks for reminders due
2. **Celery/RQ:** Proper job queue (deferred to Phase 4)

For MVP, use simple polling with FastAPI BackgroundTasks.

---

## Dependencies Summary

### Backend (requirements.txt additions)
```
python-jose[cryptography]
passlib[bcrypt]
twilio
```

### Admin App (package.json)
```json
{
  "dependencies": {
    "@react-native-async-storage/async-storage": "latest",
    // ... same as kiosk
  }
}
```

---

## Verification Checklist

### Unit Tests
- [ ] `pytest backend/tests/unit/test_security.py` - JWT, password hashing
- [ ] `pytest backend/tests/unit/test_notification_service.py` - SMS logic
- [ ] `npm run test:admin` - Admin app components

### Integration Tests
- [ ] Auth flow: login → token → protected endpoint
- [ ] Waitlist status changes via API
- [ ] SMS sends via mock adapter

### Manual Testing
1. Start backend: `cd backend && python run.py`
2. Start admin: `cd apps/admin && npx expo start`
3. Login as host
4. View waitlist, change status
5. Send "table ready" notification

---

## Implementation Order

1. **3A.1** Admin Expo setup (unblocks all frontend tasks)
2. **3A.2** Auth backend (unblocks protected endpoints)
3. **3B.1** SMS service (can be parallel with 3A.2b)
4. **3A.2b** Auth frontend (needs 3A.1 + 3A.2)
5. **3A.3** Waitlist screen (needs 3A.1 + 3A.2)
6. **3A.4** Messaging templates (needs 3A.1)
7. **3A.5** Navigation integration (needs all above)
8. **3B.2** Automated reminders (needs 3B.1)

---

## Current Progress

| Task | Status | Notes |
|------|--------|-------|
| 3A.1 | **COMPLETE** | All files created, TS passes |
| 3A.2 | **IN PROGRESS** | Agent running - Auth backend |
| 3A.2b | pending | Blocked by 3A.2 |
| 3A.3 | pending | Blocked by 3A.2 |
| 3A.4 | pending | No blockers |
| 3A.5 | pending | Blocked by 3A.2b |
| 3B.1 | **IN PROGRESS** | Agent running - SMS service |
| 3B.2 | pending | Blocked by 3B.1 |

---

## Session Context (for continuity)

### Task 3A.1 Files Created (COMPLETE)
```
apps/admin/
├── package.json          ✅ Created (with all dependencies)
├── app.json              ✅ Created (landscape orientation)
├── metro.config.js       ✅ Created (monorepo support)
├── babel.config.js       ✅ Created
├── tsconfig.json         ✅ Updated (expo paths)
├── jest.config.js        ✅ Created
├── jest.setup.js         ✅ Created
├── index.ts              ✅ Created
├── App.tsx               ✅ Created (with providers)
└── src/
    ├── app/
    │   ├── constants.ts  ✅ Created (API_URL, token keys, roles)
    │   └── store.ts      ✅ Created (RTK Query store)
    ├── services/
    │   └── api.ts        ✅ Created (with auth headers)
    └── components/
        ├── ErrorBoundary.tsx ✅ Created
        └── index.ts      ✅ Created
```

### Task 3B.1 Files to Create (SMS Service)
1. `backend/app/infrastructure/sms/__init__.py`
2. `backend/app/infrastructure/sms/base.py` - Abstract adapter
3. `backend/app/infrastructure/sms/twilio_adapter.py`
4. `backend/app/infrastructure/sms/mock_adapter.py`
5. `backend/app/domain/entities/notification.py`
6. `backend/app/services/notification_service.py`
7. `backend/app/api/v1/endpoints/notifications.py`
8. `backend/app/api/v1/schemas/notification.py`

### Backend Dependencies to Add
```
python-jose[cryptography]
passlib[bcrypt]
twilio
```

### Reference: Kiosk App Patterns
- Store: `apps/kiosk/src/app/store.ts`
- API: `apps/kiosk/src/services/api.ts`
- Constants: `apps/kiosk/src/app/constants.ts`
- ErrorBoundary: `apps/kiosk/src/components/ErrorBoundary.tsx`

---

## Notes

- All dependencies use "latest" per project standards
- Follow kiosk app patterns for consistency
- Admin app uses same @tapus/core and @tapus/ui packages
- Authentication is shared backend, separate frontend flows
