---
name: log-work
description: Append a concise work log entry under /logs after completing a task.
argument-hint: "[short task name or ticket id]"
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Write, Edit
---

You are logging completed work.

Rules:

1. Log file location:
   - Ensure directory exists: /logs
   - Append to: /logs/WORKLOG.md
2. Format MUST be exactly:
   - MM/DD/YYYY: <summary>
   - Optional continuation lines start with two spaces and "- "
3. The summary MUST include:
   - what was completed (1 sentence)
   - files touched (short list)
   - any REQ-_ / AC-_ addressed (if applicable)
   - action items / follow-ups (if any)
4. Keep each entry <= 8 lines total.
5. Never invent. If you don't know a detail (like exact files), determine it using tools.

Steps:
A) Determine today's date in America/Vancouver.

- Use: `TZ=America/Vancouver date +%m/%d/%Y`
  B) Determine changed files and intent.
- Prefer: `git diff --name-only` and/or recent commit message if available.
  C) Append a new entry to /logs/WORKLOG.md.

Implementation guidance:

- Create /logs if missing.
- Create WORKLOG.md if missing.
- Append using Bash redirection (>>).
- Do not overwrite existing logs.

Entry template:

MM/DD/YYYY: <what was completed in one sentence>

- REQ/AC: <REQ-... / AC-... or "n/a">
- Files: <comma-separated short list>
- Tests: <what was run or "n/a">
- Next: <action items or "none">
