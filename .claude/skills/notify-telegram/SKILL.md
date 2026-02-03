---
name: notify-telegram
description: Send Telegram notification to human. USE PROACTIVELY when needing approval, completing tasks, asking questions, or requiring human input. This is the primary way to alert the human.
argument-hint: "[message]"
allowed-tools: Bash
---

Send a Telegram notification with the provided message.

## When to Use (MUST use in these cases)

1. **Need approval** - Before proceeding with significant changes
2. **Task completed** - When finishing a task or milestone
3. **Question for human** - When using /ask-human or AskUserQuestion
4. **Blocked** - When work cannot proceed without human input
5. **Important status update** - Errors, test results, deployment status

## Rules

- Keep message short and actionable
- Never include secrets or sensitive data
- Include context: what happened, what's needed
- Use emojis for quick scanning:
  - ✅ Completed
  - ❓ Question/Approval needed
  - ⚠️ Warning/Blocked
  - 🚀 Deployment/Major milestone

## Command

```bash
export $(grep -v '^#' .env | xargs) && tools/notify_telegram.sh "$ARGUMENTS"
```

## Examples

- `"✅ Task 1.2 complete: Domain models with 13 tests passing"`
- `"❓ Approval needed: Proceed with WaitlistService implementation?"`
- `"⚠️ Blocked: Missing requirement for VIP auto-priority policy"`
- `"🚀 Ready to deploy to staging - awaiting approval"`
