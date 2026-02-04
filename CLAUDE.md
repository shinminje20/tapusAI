# tapusAI - Claude Code Workspace

Restaurant waitlist SaaS with requirements-driven, test-driven, gated engineering workflow.

## Project Context

**tapusAI** is a waitlist and guest-engagement platform for restaurants, cafes, and dining venues. The system uses dual tablets (client kiosk + admin host) with offline-first sync, SMS notifications, and menu browsing capabilities.

## Core Principles (Non-Negotiable)

### 1. No Guessed Business Logic

If business rules, flows, or constraints are unclear, you MUST use `/ask-human`.
Never invent requirements. Never assume behavior.

### 2. Requirements Retrieved, Not Remembered

Before implementing ANY behavioral code, run `/req <feature | REQ-id>`.
All changes must trace to documented REQ-_ and AC-_ identifiers.

### 3. Separation of Concerns

| Role                  | Responsibility              | Cannot Do               |
| --------------------- | --------------------------- | ----------------------- |
| `feature-implementer` | Write code, run tests       | Review own work, deploy |
| `code-reviewer`       | Review code, block pipeline | Write code, deploy      |
| Human                 | Approve, decide, deploy     | -                       |

### 4. Context Isolation

Large operations (searches, reviews, requirement lookups) run in forked subagent contexts to preserve main conversation context.

### 5. Traceability

Every change must have:

- REQ-\* in branch name
- REQ-_ or AC-_ in commit messages
- AC-\* covered by tests

## Requirements Source of Truth

```
docs/requirements/
├── REQUIREMENTS_INDEX.md      # Master index, ID rules, workflow
├── USECASE.md                 # Product requirements (REQ-*)
├── PROJECT_PLAN.md            # Engineering architecture
├── ACCEPTANCE_CRITERIA.md     # Testable criteria (AC-*)
└── NFR_SECURITY_COMPLIANCE.md # Security, privacy, GDPR/CCPA
```

**Before implementing, you MUST:**

1. Run `/req <feature>` to retrieve requirements
2. Build checklist from REQ-_ and AC-_
3. Implement ONLY what is in the checklist
4. If requirements are missing → `/ask-human`

## Available Skills

| Skill              | Purpose                                                         | Invocation                                   |
| ------------------ | --------------------------------------------------------------- | -------------------------------------------- |
| `/analyze-tasks`   | Generate tasks from requirements                                | `/analyze-tasks` or `/analyze-tasks phase 1` |
| `/req`             | Retrieve requirements and acceptance criteria                   | `/req waitlist` or `/req REQ-WL-004`         |
| `/ask-human`       | Pause for human decision when unclear                           | `/ask-human`                                 |
| `/review`          | Independent code review (blocks on ❌)                          | `/review` or `/review src/`                  |
| `/prepush`         | Run tests, types, linters                                       | `/prepush`                                   |
| `/start-branch`    | Create traced branch                                            | `/start-branch REQ-WL-004 vip-priority`      |
| `/push`            | Safe push after gates pass                                      | `/push`                                      |
| `/deploy`          | Human-approved deployment                                       | `/deploy staging`                            |
| `/trace`           | Verify requirement traceability                                 | `/trace REQ-WL-004`                          |
| `/log-work`        | Log completed work to /logs/WORKLOG.md                          | `/log-work`                                  |
| `/log-feature`     | Update per-feature status log                                   | `/log-feature REQ-WL-001`                    |
| `/notify-telegram` | **MUST USE** to alert human (approvals, completions, questions) | `/notify-telegram "✅ Task done"`            |
| `/sync-tasks`      | Persist task state across sessions                              | `/sync-tasks update` or `/sync-tasks resume` |

## Available Subagents

| Agent                 | Purpose                                      | Tools                                      | Mode             |
| --------------------- | -------------------------------------------- | ------------------------------------------ | ---------------- |
| `task-analyzer`       | Analyze requirements and generate tasks      | Read, Glob, Grep                           | plan (read-only) |
| `feature-implementer` | Implement features aligned with requirements | Read, Write, Edit, Bash, Glob, Grep, Skill | default          |
| `code-reviewer`       | Independent read-only review                 | Read, Glob, Grep, Bash                     | plan (read-only) |

## Standard Workflow

```
┌─────────────────────────────────────────────────────────┐
│  0. /analyze-tasks  ← Generate tasks from requirements  │
│         ↓ (human approves task)                         │
│  1. /start-branch REQ-XXX-NNN description               │
│         ↓                                               │
│  2. /req REQ-XXX-NNN                                    │
│         ↓                                               │
│         ├── Requirements unclear? → /ask-human          │
│         ↓                                               │
│  3. Implement (use feature-implementer for complex)     │
│         ↓                                               │
│  4. /review                                             │
│         ├── ❌ Issues? → Fix → /review (loop)           │
│         ↓                                               │
│  5. /prepush                                            │
│         ├── Tests fail? → Fix → /prepush (loop)         │
│         ↓                                               │
│  6. /push                                               │
│         ↓                                               │
│  7. /deploy staging → /deploy production                │
│         ↓                                               │
│  8. /log-work  ← Log completed work                     │
└─────────────────────────────────────────────────────────┘
```

## Engineering Standards

| Aspect           | Standard                          |
| ---------------- | --------------------------------- |
| Backend          | FastAPI (Python, async)           |
| Database         | SQLAlchemy + Alembic              |
| Queue            | Redis + Celery/RQ                 |
| Frontend         | React + TypeScript + Capacitor    |
| Architecture     | SOLID + Clean Architecture        |
| Testing          | pytest, pytest-asyncio (TDD)      |
| Patterns         | Async-first, Offline-first        |
| External Systems | Explicit adapters (SMS, POS, KDS) |

### Dependency Management

- **Always use `requirements.txt`** for dependencies
- **Always use latest versions** (no version pinning unless required for compatibility)
- **Always verify venv is active** before installing dependencies

```bash
# 1. Verify venv is active (check for venv in path)
which python  # Should show: /path/to/tapusAi/venv/bin/python

# 2. If not active, activate it
source /Users/minjaeshin/Desktop/project/tapusAi/venv/bin/activate

# 3. Then install
pip install -r requirements.txt        # Production
pip install -r requirements-dev.txt    # Development
```

```
backend/
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development/test dependencies
```

## Module Structure

```
backend/
├── auth/          # JWT, RBAC (REQ-SEC-004)
├── waitlist/      # Queue logic (REQ-WL-*)
├── notification/  # SMS messaging (REQ-NOTIF-*)
├── menu/          # Menu browsing (REQ-MENU-*)
├── preorder/      # Soft pre-orders (REQ-MENU-003/004)
├── analytics/     # Insights (REQ-AN-*)
└── sync/          # Offline reconciliation
```

## Requirement ID Patterns

| Pattern         | Meaning                   | Example                      |
| --------------- | ------------------------- | ---------------------------- |
| `REQ-WL-###`    | Waitlist requirements     | REQ-WL-004 (VIP priority)    |
| `REQ-NOTIF-###` | Notification requirements | REQ-NOTIF-001 (SMS alerts)   |
| `REQ-MENU-###`  | Menu requirements         | REQ-MENU-001 (browse menu)   |
| `REQ-SEC-###`   | Security requirements     | REQ-SEC-001 (secure storage) |
| `AC-XXX-###`    | Acceptance criteria       | AC-WL-004 (VIP tests)        |
| `NFR-SEC-###`   | Security NFRs             | NFR-SEC-001 (encryption)     |

## Traceability Rules

### Branch Naming

```
feature/REQ-WL-004-vip-priority
fix/REQ-NOTIF-001-sms-delivery
```

### Commit Messages

```
feat(waitlist): add VIP priority logic [REQ-WL-004]
test(waitlist): add VIP priority tests [AC-WL-004]
fix(notification): resolve SMS retry [REQ-NOTIF-002]
```

### Test Coverage

Every AC-\* must have corresponding test(s):

```python
def test_vip_priority_queue():
    """Covers AC-WL-004-1: VIPs are prioritized in queue."""
    ...
```

## Gate Summary

| Gate       | Blocking? | Trigger                                 |
| ---------- | --------- | --------------------------------------- |
| `/req`     | Soft      | Missing requirements → `/ask-human`     |
| `/review`  | Hard      | Any ❌ Must Fix issue                   |
| `/prepush` | Hard      | Test failures, type errors, lint errors |
| `/push`    | Hard      | Failed gates, missing traceability      |
| `/deploy`  | Hard      | No human approval                       |

## Review Severity Levels

| Level        | Symbol | Impact                                                             |
| ------------ | ------ | ------------------------------------------------------------------ |
| Must Fix     | ❌     | **BLOCKS pipeline** - Security, logic errors, missing requirements |
| Should Fix   | ⚠️     | Non-blocking - Architecture, test gaps                             |
| Nice to Have | 💡     | Optional - Style, optimization                                     |

## Quick Reference

```bash
# Starting new feature work
/start-branch REQ-WL-004 vip-priority
/req REQ-WL-004

# After implementation
/review
/prepush
/push

# When requirements unclear
/ask-human

# Verify traceability
/trace
/trace REQ-WL-004
```

## Session Continuity

### Context.md (MANDATORY)

**`Context.md` is the single source of truth for session state.**

**At session start:**

1. Read `Context.md` FIRST - contains all active context
2. Read `logs/plan/<phase name>.md` if referenced
3. Run `git status` to verify current state

**During each task run (MANDATORY):**

- Update `Context.md` after completing each task or subtask
- Track: completed files, remaining files, next actions, blockers
- Run `/sync-tasks update`

- **You MUST send Telegram notifications for each task/session steps for:**

- ✅ Task completions
- ❓ Questions requiring human input
- ⚠️ Blockers or errors
- 🚀 Deployment requests
- Any situation requiring human attention

```bash
export $(grep -v '^#' .env | xargs) && tools/notify_telegram.sh "Your message"
```

**Before ending session (MANDATORY):**

1. Update `Context.md` with final state
2. Update "Last Updated" timestamp
3. Update "Next Actions" section
4. Run `/sync-tasks update`

```
Context.md              # PRIMARY - All session context (MUST update every task run)
logs/
├── plan/<phase>.md     # Phase-specific detailed plans
├── tasks/TASKS.md      # Task state backup
├── WORKLOG.md          # Chronological work log
└── features/           # Per-feature status logs
```

### Context.md Structure

```markdown
# Session Context

- Last Updated: <timestamp>
- Current Phase: <phase>
- Active Tasks: <table with status>
- Task Progress: <completed/remaining files>
- Reference Patterns: <code snippets to follow>
- Next Actions: <numbered list>
- Session History: <date entries>
```

This is how the human monitors progress and responds to requests.

## What NOT To Do

- Do NOT implement features without running `/req` first
- Do NOT guess business rules - use `/ask-human`
- Do NOT complete a task without `/review`
- Do NOT end session without `/review`
- Do NOT push with failing tests
- Do NOT deploy without human approval
- Do NOT add "nice to have" improvements beyond requirements
- Do NOT complete a task without updating `Context.md`
- Do NOT end session without updating `Context.md`
- Do NOT end session without running `/sync-tasks update`
- Do NOT complete a task without sending Telegram notification
- Do NOT end session without sending Telegram notification
