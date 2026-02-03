---
name: start-branch
description: Create a git branch with compliant naming that includes requirement ID for traceability. Use when starting new feature work.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep
argument-hint: "<REQ-id> <brief-description>"
---

# Branch Creation

Create a properly named git branch with requirement traceability.

## Input

$ARGUMENTS

Expected format: `REQ-XXX-NNN description-words` or `feature-keyword`

## Branch Naming Convention

### Format
```
<type>/<REQ-id>-<brief-description>
```

### Types
| Type | Use Case |
|------|----------|
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `refactor/` | Code restructuring |
| `test/` | Test additions |
| `docs/` | Documentation only |

### Examples
```
feature/REQ-WL-004-vip-priority
fix/REQ-WL-001-queue-order-bug
```

## Workflow

1. **Validate Input**
   - If REQ-id provided: Verify it exists in REQUIREMENTS_INDEX.md
   - If keyword provided: Search for matching REQ-* and confirm

2. **Generate Branch Name**
   - Parse REQ-id and description
   - Format as `feature/REQ-XXX-NNN-description`

3. **Create Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/REQ-XXX-NNN-description
   ```

4. **Output Confirmation**
   ```markdown
   ## Branch Created

   ✅ **Branch**: `feature/REQ-XXX-NNN-description`

   ### Traceability
   | Item | Value |
   |------|-------|
   | Requirement | REQ-XXX-NNN |
   | Branch | feature/REQ-XXX-NNN-description |
   | Base | main @ <commit> |

   ### Next Steps
   1. Run /req REQ-XXX-NNN to get requirements
   2. Implement feature
   3. Run /review when complete
   4. Run /prepush before pushing
   ```

## Rules

1. Branch name MUST include REQ-id when implementing requirements
2. Cannot create branch for non-existent requirement
3. Use hyphens for word separation, no spaces
4. Lowercase only (except REQ-ID)
