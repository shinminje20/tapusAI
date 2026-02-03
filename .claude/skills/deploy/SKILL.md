---
name: deploy
description: Human-approved deployment. Deploy to an environment only after explicit human approval. Summarizes changes, risks, and rollback plan.
disable-model-invocation: true
allowed-tools: Bash, Read, AskUserQuestion
argument-hint: "<environment: dev|staging|production>"
---

# Deployment Request

Deploy to an environment ONLY after explicit human approval.

## Target Environment

$ARGUMENTS

## Environments

| Environment | Approval Required |
|-------------|-------------------|
| dev | No (auto) |
| staging | Yes (human) |
| production | Yes (human + confirmation) |

## Deployment Workflow

### 1. Gather Information

Collect:
- What's being deployed (commits, changes)
- Risk assessment
- Rollback procedure

### 2. Present Summary

```markdown
## Deployment Request: <environment>

### Deployment Info
| Field | Value |
|-------|-------|
| Environment | <env> |
| Branch | <branch> |
| Commit | <sha> |

### Changes Included

#### Features
- **REQ-XXX**: <description>

#### Fixes
- **FIX-XXX**: <description>

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Data migration | Low/Med/High | <mitigation> |

### Rollback Plan

**Automatic triggers:**
- Error rate > 5%
- Health check failures

**Manual rollback:**
```bash
./scripts/rollback.sh <previous-version>
```

---

## Approval Required

**Do you approve this deployment?**

To approve: `APPROVE DEPLOY TO <ENV>`
To reject: `REJECT: <reason>`
```

### 3. Wait for Human Response

**DO NOT PROCEED** until human explicitly approves.

### 4. Execute Deployment (if approved)

```bash
./scripts/deploy.sh <environment> <version>
```

### 5. Post-Deployment

```markdown
## Deployment Complete

✅ **Successfully deployed to <environment>**

### Health Check
✅ API responding: 200 OK
✅ Database connected: OK

### Rollback Command (if needed)
```bash
./scripts/rollback.sh <previous-version>
```
```

## Rules

1. Human approval required for staging and production
2. All deployments are logged
3. Rollback plan required
4. Health checks required post-deploy
5. Cannot skip staging for production
