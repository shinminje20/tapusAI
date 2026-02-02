# Product Use Case – Restaurant Waitlist Platform

This document defines the **product-level functional requirements** for the waitlist system.

It describes **what the system must do**, not how it is implemented.

---

## 1. Product Overview

A waitlist and guest-engagement platform for:

- Restaurants
- Cafes
- Fast casual
- Full-service dining
- Any venue managing guest queues

Primary goals:

- Reduce host friction
- Improve guest communication
- Increase table turnover efficiency
- Provide owner insights

---

## 2. Device Model & Responsibilities

### REQ-DEV-001 — Dual Tablet Setup

- At least **two tablets** per location:
  - **Client / Kiosk tablet**: guest registration
  - **Admin / Host tablet**: waitlist & operations management

### REQ-DEV-002 — Tablet Role Separation

- Client/Kiosk tablet must support **quick guest intake**
- Admin/Host tablet must support **full waitlist management**
  - reordering / VIP / status changes
  - communication templates
  - operational visibility

---

## 3. Guest & Waitlist Management

### Core Requirements

- **REQ-WL-001** — Add guests quickly (name, party size, phone number)
- **REQ-WL-002** — Real-time waitlist updates across devices
- **REQ-WL-003** — Estimated wait time calculation
- **REQ-WL-004** — Ability to reorder, prioritize, or mark VIP guests
- **REQ-WL-005** — Status tracking:
  - waiting
  - seated
  - canceled
  - no-show

---

## 4. Guest Notifications & Messaging

### Outbound

- **REQ-NOTIF-001** — SMS/text alerts when table is ready
- **REQ-NOTIF-002** — Automated reminders or status updates

### Inbound / Two-Way Messaging

- **REQ-NOTIF-003** — Guests can reply to messages
- **REQ-NOTIF-004** — Guest replies can:
  - confirm
  - delay
  - cancel
- **REQ-NOTIF-006** — System interprets guest replies and updates the waitlist accordingly
  - Example: guest cancels → status updates to canceled
  - Example: guest needs 10 more minutes → system records intent and adjusts handling rules (exact policy defined in acceptance criteria)

---

## 5. Smart Messaging Enhancements

### Quick Replies

- **REQ-NOTIF-005** — Quick-reply buttons instead of free-text only:
  - ✅ “On my way”
  - ⏱ “Need 10 more minutes”
  - ❌ “Cancel”
- **REQ-NOTIF-007** — Quick replies must map to the same business actions as text replies

---

## 6. Menu Browsing & Soft Pre-Order / Interest

### While Waiting

- **REQ-MENU-001** — Guests can browse an interactive menu
- **REQ-MENU-002** — Guests can “star” items they are interested in

### Optional Soft Pre-Order

- **REQ-MENU-003** — Fast casual:
  - Soft pre-order allowed
  - Kitchen only sees it after seating/confirmation
- **REQ-MENU-004** — Full service:
  - Server sees predicted interests
  - Example: “Table 4 likely to order 2 burgers, 1 salad”

### Required Guest Flow (explicit)

- **REQ-MENU-005** — Flow:
  - Guest receives SMS with a link
  - Guest opens menu page
  - System stores starred items and/or soft pre-order selections

---

## 7. Security & Compliance

- **REQ-SEC-001** — Secure storage of customer data
- **REQ-SEC-002** — GDPR compliance
- **REQ-SEC-003** — CCPA compliance
- **REQ-SEC-004** — Role-based access control
- **REQ-SEC-005** — Encrypted messaging and sensitive fields

---

## 8. Multi-Location Support (Not Priority for MVP)

- **REQ-ML-001** — Central dashboard for multiple venues
- **REQ-ML-002** — Shared customer database
- **REQ-ML-003** — Reporting across locations

---

## 9. Owner Intelligence & Automation

- **REQ-AN-001** — Predictive busy-time insights
- **REQ-AN-002** — Staffing recommendations
  - Example:
    - “Next Friday 7–9pm projected 20% busier than average”
    - “You turned away ~37 parties last Saturday; consider adding one more server for peak hours.”

---

## 10. Staff Convenience

- **REQ-STAFF-001** — Canned response templates on Admin tablet:
  - “We’re running a bit behind, new estimate is 15–20 mins.”
  - “We can’t hold your table longer than 10 minutes.”
- **REQ-STAFF-002** — Templates must support fast insertion and consistent tone

---

## 11. Integration Scope (Explicit)

- **REQ-INT-001** — Optional integration with Kitchen Display System (KDS) and/or POS
  - Details and priority are defined later (not required for MVP)

---

## 12. Architecture / Tech Notes (Non-binding but explicit scope references)

These are included because they were explicitly stated in the business usecase prompt and help align naming and modeling.

- **REQ-TECH-001** — Services: MenuService, PreorderService
- **REQ-TECH-002** — Data model includes:
  - menu_items
  - guest_interests
  - preorders
