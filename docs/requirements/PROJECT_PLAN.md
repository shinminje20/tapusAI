# Engineering Project Plan

This document defines **how the system is built**, not what it does.

It is subordinate to USECASE.md for product/business behavior.

---

## 1. Engineering Principles

### 1.1 Test-Driven Development (TDD)

- Write tests before implementation
- Implement minimum code to pass tests
- Refactor after green

Test levels:

- Unit tests for domain services
- API tests for key flows
- Integration tests for messaging & sync

---

### 1.2 SOLID Principles (Applied)

#### SRP — Single Responsibility

- WaitlistService: queue logic only
- NotificationService: messaging only
- SyncService: offline/online reconciliation
- UI components: either layout OR logic

#### OCP — Open/Closed

- Pluggable providers:
  - SmsProvider
  - WhatsAppProvider (future)
- Add channels without modifying core logic

#### LSP

- All providers must respect interface contracts

#### ISP

- Separate read vs write interfaces
- Admin tablet permissions differ from kiosk/guest

#### DIP

- Business logic depends on abstractions
- Frameworks wired at composition root

---

## 2. Architecture Decisions (Initial Direction)

### Backend

- FastAPI (Python, async)
- SQLAlchemy + Alembic
- Redis + background workers (Celery/RQ)

### Frontend

- React + TypeScript
- Capacitor for kiosk/admin tablets
- Offline-first local DB (SQLite)

---

## 3. Offline-First Strategy

- All tablet actions write locally first
- Background sync pushes changes to server
- Conflict resolution (v1):
  - last_write_wins using `updated_at + version`

---

## 4. Messaging Architecture

- MessageChannel abstraction
- SMS initially (provider behind interface)
- Inbound messages mapped to domain commands
- Quick replies (buttons) should map to the same domain commands as SMS replies

---

## 5. Module Breakdown

### Backend

- AuthModule (JWT, RBAC)
- WaitlistModule
- NotificationModule
- MenuModule (MenuService)
- PreorderModule (PreorderService)
- AnalyticsModule
- SyncModule

### Frontend

- Admin Tablet App (management)
- Client/Kiosk Tablet App (registration)
- Guest Web App (via SMS link)
  - Menu browsing
  - Stars / soft pre-order

---

## 6. Data Model Direction (High Level)

Key entities:

- waitlist_entries
- guests
- tables
- menu_items
- guest_interests
- preorders
- device_sync_states
- change_log

---

## 7. Step-by-Step Implementation Roadmap

1. Domain core (pure Python)
2. FastAPI layer + repositories
3. Notifications & messaging
4. Offline sync (admin tablet first)
5. Menu + guest-interest / soft pre-order flows
6. Analytics & recommendations

Each step must:

- Reference REQ-_ and AC-_
- Be covered by tests
