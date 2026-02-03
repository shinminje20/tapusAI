---
name: log-feature
description: Update a per-feature status log under /logs/features with requirements coverage, current status, changes, and next actions.
argument-hint: "[feature key | REQ-* | short slug]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Write, Edit, Grep
---

You are updating the feature status log for: $ARGUMENTS

Rules:

1. Never invent. If a detail is unknown, derive it using tools (git diff, grep REQ/AC, etc.) or mark as TBD.
2. Store logs under:
   - /logs/features/<slug>.md
3. The log must be maintained as "current state", not just appended history.
4. Always include:
   - Date (America/Vancouver)
   - Feature status: Planned | In Progress | Done | Blocked
   - Requirements: list REQ-_ and AC-_ addressed
   - Summary of changes (bullets)
   - Files touched
   - Tests run
   - Risks/Assumptions
   - Next actions (clear, numbered)

Steps:
A) Determine today's date: TZ=America/Vancouver date +%m/%d/%Y
B) Determine changed files: git diff --name-only (or last commit if clean)
C) Extract REQ-_ and AC-_ references from:

- docs/requirements (grep)
- changed files (grep)
  D) Create /logs/features if missing.
  E) Create or update the feature log file:
- If file exists, update sections in place.
- If not, create from template below.
  F) Keep it concise: target <= 40 lines unless the feature is large.

Template (use exactly these headings):

# Feature: <slug or title>

## Status

- Updated: MM/DD/YYYY
- Status: <Planned|In Progress|Done|Blocked>
- Owner: <human name or "TBD">
- Scope: <1 sentence>

## Requirements Coverage

- REQ: <list or "TBD">
- AC: <list or "TBD">

## What Changed

- <bullets>

## Files Touched

- <bullets>

## Validation

- Tests: <commands or "n/a">
- Manual checks: <steps or "n/a">

## Risks / Notes

- <bullets or "none">

## Next Actions

1. <action>
2. <action>
