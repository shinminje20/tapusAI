---
name: trace
description: Traceability verification. Verify that implementation changes are properly traced to requirements (REQ-*), acceptance criteria (AC-*), tests, and documentation.
context: fork
agent: Explore
allowed-tools: Read, Grep, Glob, Bash
argument-hint: "[REQ-id or --branch or --commit <sha>]"
---

# Traceability Verification

Verify that changes are properly traced to requirements.

## Scope

$ARGUMENTS

- If REQ-id: Check coverage for that requirement
- If --branch: Check current branch
- If --commit: Check specific commit

## Traceability Matrix

Every feature must have:

| Artifact | Must Reference |
|----------|---------------|
| Branch name | REQ-id |
| Commit message | REQ-id or AC-id |
| Test file | AC-id |
| Code comment | REQ-id (if non-obvious) |

## Verification Steps

1. **Get Branch Info**
   ```bash
   git branch --show-current
   git log --oneline main..HEAD
   ```

2. **Check Branch Name**
   - Pattern: `<type>/REQ-XXX-NNN-description`

3. **Check Commits**
   - Pattern: `[REQ-XXX]` or `[AC-XXX]` in message

4. **Check Test Coverage**
   - Find tests referencing AC-*
   - Verify all AC-* have tests

5. **Build Report**

## Output Format

```markdown
## Traceability Report

### Branch: `<branch-name>`

### Requirements Coverage

#### REQ-XXX-NNN: <Title>

| Acceptance Criteria | Test | Status |
|---------------------|------|--------|
| AC-XXX-1 | test_xxx | ✅ |
| AC-XXX-2 | - | ❌ Missing |

### Commit Traceability

| Commit | Message | REQ Reference | Status |
|--------|---------|---------------|--------|
| abc123 | feat: ... [REQ-XXX] | REQ-XXX | ✅ |
| def456 | fix: typo | - | ⚠️ Minor |

### Summary

| Metric | Value | Status |
|--------|-------|--------|
| Requirements traced | N/N | ✅/❌ |
| AC covered by tests | N/N | ✅/❌ |
| Commits with REQ ref | N/N | ✅/❌ |

### Overall: ✅ COMPLETE or ⚠️ INCOMPLETE

### Required Actions (if incomplete)
1. Add test for AC-XXX
2. Update commit message
```

## Validation Patterns

### Branch Name
```regex
^(feature|fix|refactor|test|docs)/REQ-[A-Z]+-\d{3}-[\w-]+$
```

### Commit Message
```regex
\[(REQ|AC)-[A-Z]+-\d{3}(-\d+)?\]
```
