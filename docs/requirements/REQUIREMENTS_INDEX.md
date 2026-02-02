# Requirements Index

This directory contains the **single source of truth** for product, business, and system requirements.

Claude Code and human contributors MUST consult these documents before implementing or reviewing any behavior-changing code.

---

## 1. Canonical Requirement Documents

### Product & Business

- **USECASE.md**
  - High-level product vision
  - Business use cases and flows
  - Functional requirements (REQ-\*)
  - Scope boundaries and priorities

### Engineering & Architecture

- **PROJECT_PLAN.md**
  - Engineering principles (TDD, SOLID)
  - System architecture direction
  - Module responsibilities
  - Implementation roadmap

### Acceptance & Validation

- **ACCEPTANCE_CRITERIA.md**
  - Testable acceptance criteria (AC-\*)
  - Maps AC-_ → REQ-_

### Non-Functional Requirements

- **NFR_SECURITY_COMPLIANCE.md**
  - Security
  - Privacy (GDPR / CCPA)
  - Data handling & encryption
  - Role-based access control

---

## 2. Requirement Identification Rules

### Requirement IDs

- Functional requirements: `REQ-<AREA>-###`
  - Example: `REQ-WL-004` (Waitlist – VIP prioritization)
- Acceptance criteria: `AC-<AREA>-###`
  - Example: `AC-WL-004`
- Non-functional requirements: `NFR-SEC-###`, `NFR-PRIV-###`, etc.

IDs are **stable** and should be referenced in:

- Branch names
- PR descriptions
- Tests (recommended where practical)

---

## 3. Mandatory Workflow Rule

If a task affects:

- Business behavior
- User flow
- Data model
- Security
- Messaging
- API contracts

Then the contributor (human or AI) MUST:

1. Identify relevant REQ-\* from this directory
2. Identify corresponding AC-\*
3. Implement ONLY what is covered
4. Ask the human if requirements are missing or unclear

**Guessing business logic is not allowed.**

---

## 4. Definition of Done (Global)

A change is considered “done” only if:

- All relevant REQ-\* are satisfied
- All related AC-\* are covered by tests (or explicitly deferred with approval)
- Security and privacy constraints are respected
- Code review passes with no ❌ issues
