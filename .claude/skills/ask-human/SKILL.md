---
name: ask-human
description: Human-in-the-loop gate. Use when requirements are missing, ambiguous, or contradictory. Use for security decisions, architecture choices, or any decision requiring human approval.
disable-model-invocation: true
argument-hint: "[optional question context]"
allowed-tools: Bash, AskUserQuestion
---

# Human Input Required

You must pause and ask the human for input. This skill is for situations where:
- Requirements are missing, ambiguous, or contradictory
- Security decisions need to be made
- Architecture choices require human judgment
- Deployment or other critical approvals are needed

## Context

$ARGUMENTS

## Question Rules

All questions MUST be:
1. **Specific** - Not vague or open-ended
2. **Numbered** - For easy reference in response
3. **Answerable** - Can be resolved with a concrete decision
4. **Contextual** - Include relevant background

## Output Format

Present questions using the AskUserQuestion tool with this structure:

### Questions

1. **[Category]**: <Specific question>
   - Option A: <description and implications>
   - Option B: <description and implications>
   - Current assumption: <what you'd do without guidance>

2. **[Category]**: <Specific question>
   - Details needed: <what specifically is missing>
   - Impact: <what can't proceed without this>

### Blocked Work

The following cannot proceed until questions are answered:
- <task or implementation item>

## Behavior

1. **Send Telegram notification** - Alert human that input is needed:
   ```bash
   export $(grep -v '^#' .env | xargs) && tools/notify_telegram.sh "❓ Human input required: $ARGUMENTS"
   ```
2. **Pause execution** - Do not proceed with implementation
3. **Present questions** - Using AskUserQuestion tool
4. **Wait for response** - Human must provide answers
5. **Resume with answers** - Continue implementation using provided decisions
