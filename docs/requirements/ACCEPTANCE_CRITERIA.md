# Acceptance Criteria

This document defines **testable acceptance criteria (AC-\*)** mapped to product requirements (REQ-\*).
These criteria are written to support implementation, QA, and automated testing.

Rule:

- Do not implement behavior that is not covered by AC-\* or explicitly approved by the human.
- If a criterion is marked **TBD**, it requires human decision before implementation.

---

## 0) Scope & Priority

### MVP Priority Areas

- Waitlist management (add, status, reorder, VIP, ETA, real-time updates)
- SMS notifications when ready + basic two-way messaging (confirm, delay, cancel)
- Admin tablet workflows (management + templates)
- Client/Kiosk tablet workflows (registration)
- Security baseline (secure storage, role-based access, encryption)
- Guest SMS link → guest page (status + optional menu browse/stars)

### Not MVP / Later (Explicitly not priority yet)

- Multi-location dashboard, shared customer DB, cross-location reporting (REQ-ML-\*)
- Owner predictive insights & staffing recommendations (REQ-AN-\*)
- Optional KDS/POS integration (REQ-INT-001)
- Soft pre-order behaviors beyond “store preferences” unless approved

---

## 1) Device Model & Role Separation

### AC-DEV-001 — Dual Tablet Roles Exist and Are Separated

**Maps to:** REQ-DEV-001, REQ-DEV-002  
**Given** a location is set up  
**When** staff uses the system  
**Then** there are at least two tablet experiences:

- Client/Kiosk tablet supports **quick guest intake**
- Admin/Host tablet supports **full waitlist management**
  And UI capabilities align to the role (kiosk cannot reorder or mark VIP unless explicitly configured).

### AC-DEV-002 — Admin Actions Are Not Available on Kiosk by Default

**Maps to:** REQ-DEV-002, REQ-SEC-004  
**Given** a kiosk/tablet is operating in client mode  
**When** a user attempts management actions  
**Then** the system blocks access by default (requires admin role/login).

---

## 2) Guest & Waitlist Management

### AC-WL-001 — Add Guest (Minimum Fields) and Display Immediately

**Maps to:** REQ-WL-001, REQ-WL-002  
**Given** a host or kiosk is on the “Add guest” screen  
**When** they submit name, party size, phone number  
**Then**

- a waitlist entry is created
- it appears on the Admin tablet waitlist view immediately
- it has status `waiting` by default
- it includes created time and unique identifier

### AC-WL-002 — Validate Input for Guest Add

**Maps to:** REQ-WL-001
**Given** guest add form submission
**Then**

- party size must be >= 1
- phone number must be present and valid format per locale rules (TBD locale rules if multi-country)
- name is **REQUIRED** (DECIDED: 02/01/2026)

**All three fields are mandatory:** name, phone number, party size.

### AC-WL-003 — Status Transitions Supported

**Maps to:** REQ-WL-005  
**Given** a waitlist entry is in `waiting`  
**When** staff updates status  
**Then** it can become:

- `seated`
- `canceled`
- `no-show`  
  And the system persists the status, timestamp, and actor (for audit).

### AC-WL-004 — Invalid Status Transitions Are Prevented

**Maps to:** REQ-WL-005  
**Given** an entry is `seated`, `canceled`, or `no-show`  
**When** staff tries to change it back to `waiting`  
**Then** the system blocks it unless an explicit “undo” policy exists (TBD undo policy).

### AC-WL-005 — Reordering Updates Position Deterministically

**Maps to:** REQ-WL-004, REQ-WL-002  
**Given** a waitlist contains multiple `waiting` entries  
**When** staff reorders entries  
**Then**

- the ordering is saved
- positions update consistently across devices
- the waitlist view reflects the same order within the real-time update SLA (see performance NFR)

### AC-WL-006 — VIP Flagging and Priority

**Maps to:** REQ-WL-004
**Given** an entry is marked VIP
**Then**

- it is visibly indicated as VIP in the admin UI
- VIP status persists
- VIP priority behavior: **Manual move only** (DECIDED: 02/01/2026)
  - VIP can be moved ahead manually by staff
  - No automatic priority queue adjustment
  - VIP flag is informational for staff awareness

### AC-WL-007 — ETA Calculation Exists and Updates

**Maps to:** REQ-WL-003, REQ-WL-002
**Given** a location has a waitlist and historical/estimated turn times
**Then**

- each entry shows an estimated wait time (ETA)
- ETA updates when:
  - entries are added/removed
  - entries are reordered
  - status changes to seated/canceled/no-show

**ETA Algorithm (DECIDED: 02/01/2026):** Simple calculation
- Formula: `ETA = position_in_queue × average_turn_time`
- `average_turn_time` defaults to configurable value (e.g., 15 minutes)
- Can be enhanced later with historical data

### AC-WL-008 — Source is Captured

**Maps to:** REQ-WL-001, REQ-DEV-001  
**Given** entry creation  
**Then** system records source at least:

- `KIOSK` or `ADMIN` (minimum)
  Additional sources may be added later.

---

## 3) Real-Time Waitlist Updates

### AC-RT-001 — Real-Time Propagation for Waitlist Changes

**Maps to:** REQ-WL-002  
**Given** two admin devices are online  
**When** any waitlist change occurs (add, status update, reorder, VIP flag)  
**Then** the other device reflects the change within the SLA defined in NFR-PERF.

### AC-RT-002 — Correctness Over Speed

**Maps to:** REQ-WL-002  
**Given** network jitter or intermittent connectivity  
**Then** system ensures eventual consistency and correct final ordering/state.
Conflict resolution strategy must be deterministic (see PROJECT_PLAN.md).

---

## 4) Guest Notifications (Outbound)

### AC-NOTIF-001 — Send “Table Ready” SMS on Ready Condition

**Maps to:** REQ-NOTIF-001  
**Given** an entry meets the “table ready” condition  
**When** staff triggers readiness (manual or automated per policy)  
**Then** the system sends an SMS to the guest phone number with:

- location/venue identifier (or name if stored)
- brief message that table is ready
- next action guidance (confirm, arrive, cancel)
- guest link (if guest web page is used)

“Ready condition” mechanism (manual button vs automated) is TBD, but must exist.

### AC-NOTIF-002 — Avoid Duplicate Ready Messages

**Maps to:** REQ-NOTIF-001  
**Given** a ready notification has already been sent for an entry  
**When** readiness is triggered again  
**Then** the system prevents duplicate sends or requires confirmation (TBD duplicate policy).

### AC-NOTIF-003 — Automated Reminder / Status Updates

**Maps to:** REQ-NOTIF-002  
**Given** reminder/status updates are enabled for the location  
**Then**

- reminders can be sent based on defined rules (TBD timing rules)
- the system logs that reminder was sent
- reminders must respect opt-out (see security/compliance NFR)

---

## 5) Two-Way Messaging (Inbound)

### AC-NOTIF-004 — Guest Can Cancel by Reply

**Maps to:** REQ-NOTIF-003, REQ-NOTIF-004, REQ-NOTIF-006  
**Given** guest received a message  
**When** guest replies with a recognized cancel intent  
**Then**

- waitlist entry becomes `canceled`
- admin UI updates in real time
- system optionally sends confirmation to the guest (TBD confirm-message policy)

Recognized cancel intents must include at least:

- “cancel”
- “Cancel”
- “CANCEL”
  Additional patterns can be added.

### AC-NOTIF-005 — Guest Can Confirm by Reply

**Maps to:** REQ-NOTIF-003, REQ-NOTIF-004, REQ-NOTIF-006  
**When** guest replies with a recognized confirm intent  
**Then**

- system records guest confirmed
- admin UI reflects confirmed state (could be a flag)
  Exact operational meaning of “confirmed” is TBD (does it hold place?).

### AC-NOTIF-006 — Guest Can Request Delay (“Need 10 more minutes”)

**Maps to:** REQ-NOTIF-003, REQ-NOTIF-004, REQ-NOTIF-006  
**When** guest replies with a recognized delay intent  
**Then**

- system records delay request
- admin UI reflects it
- queue adjustment policy is TBD:
  - Does it bump them down?
  - Does it set a timer/hold?
    This must be defined before implementing automatic reordering.

### AC-NOTIF-007 — Unknown Reply Handling

**Maps to:** REQ-NOTIF-003  
**When** guest replies with unrecognized text  
**Then**

- system does not break
- admin sees “unrecognized message received”
- system can send a fallback response (TBD fallback message policy)

---

## 6) Quick Reply Buttons (Smarter Two-Way)

### AC-NOTIF-008 — Quick Reply Options Exist

**Maps to:** REQ-NOTIF-005  
**Given** guest link experience supports quick replies  
**Then** guest can choose:

- ✅ On my way
- ⏱ Need 10 more minutes
- ❌ Cancel

### AC-NOTIF-009 — Quick Reply Actions Map to Same Domain Commands

**Maps to:** REQ-NOTIF-007, REQ-NOTIF-006  
**Given** guest uses quick reply  
**Then** system executes the same business action as the equivalent SMS reply:

- Cancel → canceled
- Delay → delay request recorded (policy applies)
- On my way → confirmed/on-the-way recorded (policy applies)

---

## 7) Menu Browsing & Guest Interest

### AC-MENU-001 — Guest Accesses Menu From SMS Link

**Maps to:** REQ-MENU-005  
**Given** guest receives SMS with a link  
**When** guest opens the link  
**Then** menu page loads for that venue/location context.

### AC-MENU-002 — Guests Can Star Items (Interest Capture)

**Maps to:** REQ-MENU-002  
**When** guest stars items  
**Then** system stores the set of starred items tied to the guest/waitlist entry.

### AC-MENU-003 — Soft Pre-Order Capture (If Enabled)

**Maps to:** REQ-MENU-003  
**Given** fast casual mode enables soft pre-order  
**When** guest selects items to soft pre-order  
**Then** system stores selections but does not expose to kitchen until seating/confirmation rules apply.

Visibility trigger rule is TBD and must be defined for kitchen exposure.

### AC-MENU-004 — Full-Service “Likely to Order” Visibility (If Enabled)

**Maps to:** REQ-MENU-004  
**Given** full-service mode  
**Then** admin/staff view shows guest interest summary such as:

- “Likely to order: 2 burgers, 1 salad”
  Exact display rules are TBD.

### AC-MENU-005 — Data Model Exists for Menu & Interest

**Maps to:** REQ-TECH-002  
System must have persisted representations for:

- menu_items
- guest_interests
- preorders (if enabled)

---

## 8) Staff Convenience Templates

### AC-STAFF-001 — Canned Templates Available in Admin UI

**Maps to:** REQ-STAFF-001, REQ-STAFF-002  
**Given** admin tablet is in messaging mode  
**Then** staff can select templates such as:

- “We’re running a bit behind, new estimate is 15–20 mins.”
- “We can’t hold your table longer than 10 minutes.”

### AC-STAFF-002 — Templates Are Fast to Send and Consistent

**Maps to:** REQ-STAFF-002  
**Then**

- templates can be inserted with minimal taps/clicks
- templates preserve consistent tone
- message sending logs message + template used

---

## 9) Security & Compliance (Functional Facets)

These are functional checks that connect to NFR_SECURITY_COMPLIANCE.md.

### AC-SEC-001 — RBAC Blocks Unauthorized Actions

**Maps to:** REQ-SEC-004  
**Given** a user is not authorized  
**Then** they cannot:

- view private guest phone numbers unless role permits
- reorder or seat guests unless role permits
- access admin features from kiosk mode

Roles must be defined (at least Guest/Host/Manager/Owner) in security doc.

### AC-SEC-002 — Secure Storage and Transport Baseline

**Maps to:** REQ-SEC-001, REQ-SEC-005  
**Then**

- sensitive fields are encrypted at rest (per NFR)
- API uses TLS (per NFR)
- messaging links do not expose PII directly (per NFR)

### AC-SEC-003 — GDPR/CCPA-Related Behaviors Are Supported

**Maps to:** REQ-SEC-002, REQ-SEC-003  
**Then**

- system supports data export/delete workflows (admin-only or system process)
  Exact operational process is defined in NFR doc.

---

## 10) Multi-Location Support (Deferred)

### AC-ML-001 — Multi-Location Features Are Not Required for MVP

**Maps to:** REQ-ML-001..003  
MVP is allowed to be single-location.
If multi-location is implemented later, acceptance criteria will be expanded.

---

## 11) Owner Intelligence & Automation (Deferred)

### AC-AN-001 — Predictive Insights Deferred

**Maps to:** REQ-AN-001, REQ-AN-002  
Analytics and staffing predictions are not required for MVP.
When implemented, must be testable with historical data.

---

## 12) Integration Scope (Optional / Later)

### AC-INT-001 — KDS/POS Integration Is Optional

**Maps to:** REQ-INT-001  
No integration is required for MVP.
If implemented, integration must:

- be behind an interface
- not break core operations when unavailable
