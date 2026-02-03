---
name: analyze-tasks
description: Analyze requirements and generate prioritized implementation tasks. Use when starting new work, planning what to build next, or when you need a task breakdown from requirements.
disable-model-invocation: true
context: fork
agent: task-analyzer
allowed-tools: Read, Glob, Grep
argument-hint: "[optional: phase number or REQ-id to focus on]"
---

# Analyze Tasks

Generate actionable implementation tasks from requirements in `docs/requirements/`.

## Focus Area

$ARGUMENTS

- If empty: Analyze all requirements and suggest next tasks based on PROJECT_PLAN.md phases
- If phase number (e.g., "phase 1"): Focus on that implementation phase
- If REQ-id (e.g., "REQ-WL-004"): Break down that specific requirement into tasks

## Process

1. Read all requirement documents in `docs/requirements/`
2. Check existing implementation status in codebase
3. Generate prioritized task list
4. Present for human approval before proceeding

## Output

A prioritized list of tasks with:
- REQ-* and AC-* references
- Scope description
- Dependencies
- Suggested branch name
- Complexity estimate

**Human approval required before implementation begins.**
