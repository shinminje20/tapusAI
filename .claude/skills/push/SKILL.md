---
name: push
description: Safe push to remote. Only pushes if tests pass, review passed, and traceability exists. Use after /review and /prepush have passed.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[--force]"
---

# Safe Push

Push code to remote only after verifying all gates have passed.

## Arguments

$ARGUMENTS

- `--force`: Force push (heavily warned, never to main/master)

## Pre-Push Checklist

Before pushing, verify:

### 1. Review Status
- [ ] /review has been run
- [ ] No ❌ (Must Fix) issues remain

### 2. Test Status
- [ ] /prepush has been run
- [ ] All tests pass
- [ ] Type checks pass
- [ ] Lint checks pass

### 3. Traceability
- [ ] Branch name includes REQ-id
- [ ] Commits reference REQ-id

## Workflow

1. **Check Gates**
   ```bash
   git status
   git log --oneline main..HEAD
   ```

2. **Verify Branch Name**
   - Must match: `<type>/REQ-XXX-NNN-description`

3. **Verify Commits**
   - Must reference REQ-id or AC-id

4. **Push if all pass**
   ```bash
   git push -u origin <branch-name>
   ```

## Output Format

### Success
```markdown
## Push Successful

✅ **Pushed to origin/<branch-name>**

### Summary
| Metric | Value |
|--------|-------|
| Commits Pushed | N |
| Files Changed | N |

### Next Steps
1. Create Pull Request
2. Request code review
3. Await CI pipeline
```

### Blocked
```markdown
## Push Blocked

❌ **Cannot push - gates not passed**

### Gate Status
| Gate | Status |
|------|--------|
| /review | ❌ or ✅ |
| /prepush | ❌ or ✅ |
| Traceability | ❌ or ✅ |

### Required Actions
1. <action to fix>
```

## Rules

1. Gates must pass - Cannot push without /review and /prepush passing
2. Traceability required - Branch and commits must reference REQ-id
3. No force to main - Force push to main/master is NEVER allowed
4. Explicit confirmation for --force
