---
name: req
description: Requirements lookup. Use when implementing features, before writing behavioral code, or when you need to understand what requirements exist for a feature. Retrieves REQ-* and AC-* from docs/requirements/.
argument-hint: "[feature-keyword | REQ-id | topic]"
context: fork
agent: Explore
allowed-tools: Read, Grep, Glob
---

# Requirements Lookup

You are retrieving requirements and acceptance criteria from the documentation source of truth.

## Search Strategy

Search in this order:
1. `docs/requirements/REQUIREMENTS_INDEX.md` - For REQ-* ID mappings
2. `docs/requirements/USECASE.md` - For user stories and flows
3. `docs/requirements/ACCEPTANCE_CRITERIA.md` - For AC-* items
4. `docs/requirements/NFR_SECURITY_COMPLIANCE.md` - For non-functional requirements
5. `docs/requirements/PROJECT_PLAN.md` - For phase/milestone context

## Search Input

Search for: $ARGUMENTS

## Rules

1. Search is case-insensitive
2. If given a REQ-* ID, find exact match first
3. If given a keyword, search all files for relevant sections
4. Include parent context (the section heading containing the match)
5. No summaries without citations - every statement must include file:line reference
6. No fabrication - if a requirement doesn't exist, say so clearly

## Output Format

```markdown
## Requirements Found: <search term>

### Primary Requirements

#### REQ-XXX-NNN: <Title>
- **Source**: `docs/requirements/<filename>.md:L<line>`
- **Description**: <full requirement text>
- **Priority**: <P0/P1/P2 if specified>
- **Phase**: <phase number if specified>

### Acceptance Criteria

- [ ] AC-XXX-NNN-1: <criterion text>
  - Source: `docs/requirements/ACCEPTANCE_CRITERIA.md:L<line>`

### Related Non-Functional Requirements

- NFR-XXX-NNN: <requirement if applicable>

### Implementation Checklist

Based on the above, implement:
- [ ] <actionable item derived from REQ>
- [ ] <test for AC-XXX-NNN>

### Open Questions

If any requirements are unclear or missing:
1. <specific question>

⚠️ If open questions exist, invoke /ask-human before implementing.
```

## If Not Found

```markdown
## Requirements Found: <search term>

❌ **No requirements found matching "<search term>"**

### Suggestions
- Try broader search terms
- Check REQUIREMENTS_INDEX.md for available REQ-* IDs
- Invoke /ask-human to request requirement documentation
```
