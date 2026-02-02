# Non-Functional Requirements: Security & Compliance

This document defines non-functional requirements (NFR-\*) for:

- Security
- Privacy
- Compliance (GDPR / CCPA)
- Operational safeguards

It supports REQ-SEC-001..005 in USECASE.md and AC-SEC-\* in ACCEPTANCE_CRITERIA.md.

---

## 1) Definitions & Data Classification

### NFR-SEC-001 — Data Classification

The system must classify and treat data with appropriate protections.

**PII (High sensitivity):**

- phone number
- name (when linked to phone)
- message history (may contain PII)

**Operational data (Medium):**

- waitlist status
- party size
- timestamps
- device identifiers

**Public/low sensitivity:**

- menu items and categories (unless business marks as sensitive)

---

## 2) Authentication & Authorization

### NFR-SEC-010 — Authentication Required for Admin Access

Admin/management features must require authenticated access (except kiosk intake screens).

### NFR-SEC-011 — Role-Based Access Control (RBAC)

Roles must exist at minimum:

- Guest (limited to own guest link view)
- Host (waitlist operations)
- Manager (configuration + overrides)
- Owner (reports/admin-level controls)

Access must follow least privilege:

- kiosk mode cannot access admin operations by default
- sensitive fields (phone numbers) visible only to roles that require it

### NFR-SEC-012 — Session Security

- Tokens/sessions must expire.
- Refresh mechanism must be secure.
- Admin sessions must support logout and revocation (e.g., lost device).

---

## 3) Encryption & Secrets

### NFR-SEC-020 — Transport Encryption

All network communication must use TLS (HTTPS/WSS).
No plaintext credentials or tokens over unsecured channels.

### NFR-SEC-021 — Encryption at Rest

PII (phone numbers, message logs, any identifiers linking to a person) must be encrypted at rest.
Encryption can be database-level or application-level but must be documented.

### NFR-SEC-022 — Secrets Management

- No secrets committed to git.
- Secrets stored via environment variables or secrets manager.
- Rotate secrets (SMS provider credentials, JWT signing keys) on schedule and after incidents.

### NFR-SEC-023 — Key Management

- Encryption keys must be access-controlled.
- Support key rotation without data loss (procedure documented).

---

## 4) Guest Link Security (SMS Link → Web Page)

### NFR-SEC-030 — Signed/Expiring Guest Links

Guest links sent via SMS must:

- be signed or tokenized
- have an expiry policy (TBD default: 24–72 hours recommended)
- not contain raw PII in URL parameters

### NFR-SEC-031 — Replay and Guess Resistance

Tokens must be unguessable (cryptographically random).
System must reject expired or invalid tokens.

---

## 5) Messaging Security & Abuse Prevention

### NFR-SEC-040 — SMS Content Safety

Avoid including unnecessary PII in SMS body.
Messages should not disclose sensitive internal state beyond what is required.

### NFR-SEC-041 — Inbound Message Validation

Inbound messages must be:

- validated against known conversation/guest context
- rate-limited
- sanitized (no command injection risks)

### NFR-SEC-042 — Opt-Out Handling

System must respect opt-out requests (e.g., “STOP”) according to SMS provider and legal requirements.
If guest opts out:

- do not send further messages unless opt-in restored
- record the opt-out state

---

## 6) Audit Logging & Accountability

### NFR-SEC-050 — Audit Log for Admin Actions

Record administrative actions that change guest or waitlist state:

- status changes
- reordering
- VIP marking
- message sends (template used)
- access to sensitive fields (optional but recommended)

Audit logs must include:

- actor identity
- timestamp
- action
- target entity id
- before/after (as feasible)

### NFR-SEC-051 — Log Protection

Logs must not leak secrets or full PII.
Mask or redact phone numbers in logs by default.

---

## 7) Privacy & Compliance (GDPR / CCPA)

### NFR-PRIV-010 — Data Minimization

Collect only what is required for the service:

- name (optional policy)
- party size
- phone number for messaging
  Do not collect unrelated personal attributes by default.

### NFR-PRIV-011 — Purpose Limitation

PII collected is used only for:

- waitlist management
- guest notifications
- related operational needs
  Use for marketing requires separate consent (TBD business decision).

### NFR-PRIV-012 — Retention Policy

Define and enforce retention for:

- waitlist entries
- message logs
- guest profiles (if persistent)

Retention is TBD by business, but system must support:

- automatic deletion after X days
- manual deletion/export on request

### NFR-PRIV-013 — Data Subject Rights (GDPR/CCPA)

System must support:

- access/export of personal data for a guest (by phone number or token proof)
- deletion request handling
- correction (if applicable)

### NFR-PRIV-014 — CCPA “Do Not Sell/Share”

If the business ever shares data with third parties beyond operational providers (e.g., SMS vendor), it must provide required disclosures and controls.
For MVP, default: no sale/sharing beyond essential processors.

### NFR-PRIV-015 — Processor/Vendor Compliance

External providers (SMS gateways, hosting) must be treated as processors.
Keep a record of:

- vendor name
- data processed
- purpose
- retention and security notes

---

## 8) Secure Development & OWASP Baselines

### NFR-SEC-060 — Input Validation

All API inputs must be validated and type-checked.
Reject invalid data with clear errors.

### NFR-SEC-061 — Authorization Checks on Every Sensitive Endpoint

Every endpoint that:

- changes waitlist state
- accesses phone numbers
- sends messages
  must require authorization.

### NFR-SEC-062 — Rate Limiting

Rate limit:

- guest link endpoints
- inbound message endpoints
- login/auth endpoints
  to prevent abuse.

### NFR-SEC-063 — Dependency Hygiene

- Pin dependencies.
- Regularly scan for known vulnerabilities.
- Patch critical issues promptly.

---

## 9) Availability, Reliability, and Offline-Tolerance

### NFR-REL-010 — Offline-First Continuity

If internet drops temporarily:

- Admin tablet must continue to add/update entries locally
- System must sync when connectivity returns
  Conflict strategy must be deterministic.

### NFR-REL-011 — Idempotency for Critical Actions

Actions like:

- status updates
- message send triggers
  should be idempotent to avoid duplicates during retries.

### NFR-REL-012 — Graceful Degradation

If SMS provider is down:

- system must not lose waitlist state
- must show “message failed” clearly in admin UI
- allow retry

---

## 10) Performance Requirements

### NFR-PERF-010 — Real-Time Update Latency

For online devices:

- waitlist changes must appear on other admin devices within a defined SLA.
  Recommended initial SLA:
- 1–3 seconds for UI updates under normal load

### NFR-PERF-011 — Add Guest Response Time

Guest add (admin/kiosk) should complete quickly.
Recommended initial SLA:

- UI confirmation within 1 second (local-first), sync async.

### NFR-PERF-012 — Scale Assumptions (MVP)

Define capacity targets (TBD), e.g.:

- X concurrent devices per location
- Y entries per day
  System must remain stable under these targets.

---

## 11) Incident Response & Business Safety

### NFR-SEC-070 — Incident Logging & Alerting

System must have a way to detect and review:

- message failures
- sync failures
- repeated authorization failures

### NFR-SEC-071 — Breach Response Readiness

Have documented procedures for:

- key rotation
- revoking tokens
- notifying stakeholders if required by law

---

## 12) Compliance Documentation (Minimum Artifacts)

Maintain:

- Data retention policy (business decision)
- Role definitions and permissions matrix
- Vendor list and what data they process
- Basic incident response playbook

These may start as markdown files in `docs/compliance/`.
