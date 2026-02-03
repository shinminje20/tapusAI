---
name: sync-tasks
description: Sync task state to /logs/tasks/TASKS.md for persistence across sessions. Use after completing tasks, before ending session, or when task status changes.
argument-hint: "[update | status | resume]"
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Task State Synchronization

Maintain persistent task state in `/logs/tasks/TASKS.md` so new sessions can resume work.

## Commands

- `update` - Update TASKS.md with current task status
- `status` - Show current task state from file
- `resume` - Read TASKS.md and restore context (use at session start)

## Action: $ARGUMENTS

## File Location

`/logs/tasks/TASKS.md`

## Update Process

1. Get current date: `TZ=America/Vancouver date +%m/%d/%Y`
2. Read existing TASKS.md if exists
3. Update with current state:
   - Tasks in progress
   - Tasks completed this session
   - Tasks pending
   - Current context/blockers
   - Next actions

## TASKS.md Format

```markdown
# Task State

**Last Updated:** MM/DD/YYYY
**Session:** <brief description of current work>

## Current Focus
<What's actively being worked on>

## In Progress
- [ ] Task description [REQ-XXX]
  - Status: <details>
  - Blockers: <if any>

## Completed (This Phase)
- [x] Task description [REQ-XXX] - MM/DD/YYYY

## Pending
- [ ] Task description [REQ-XXX]
  - Blocked by: <dependency if any>

## Context for Next Session
<Important context that shouldn't be lost>
- Current branch: <branch name>
- Last action: <what was just done>
- Next step: <immediate next action>
- Open questions: <any TBD items>

## Session History
- MM/DD/YYYY: <summary of session work>
```

## Resume Process (New Session)

When starting a new session:
1. Read `/logs/tasks/TASKS.md`
2. Read `/logs/WORKLOG.md` for recent history
3. Check git status for current branch/changes
4. Present summary to human
5. Ask: "Continue with <next step>?"

## Rules

1. Always update before ending a session
2. Include enough context for a fresh session to resume
3. Reference REQ-* and AC-* for traceability
4. Keep concise but complete
