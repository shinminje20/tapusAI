---
name: prepush
description: Test and validation gate. Run before pushing code. Executes tests, type checks, and linters. Fails hard on any red status.
disable-model-invocation: true
allowed-tools: Bash, Read
argument-hint: "[--fix or --fast]"
---

# Pre-push Validation

Run all validation checks before pushing code.

## Arguments

$ARGUMENTS

- `--fix`: Auto-fix linter issues if possible
- `--fast`: Skip slow tests (not recommended for production)

## Validation Steps

### 1. Test Execution

```bash
# Run full test suite
pytest tests/ -v --tb=short

# With coverage if available
pytest tests/ -v --cov=src --cov-report=term-missing
```

### 2. Type Checking (if configured)

```bash
# MyPy
mypy src/ --strict

# Or Pyright
pyright src/
```

### 3. Linting (if configured)

```bash
# Ruff (preferred)
ruff check src/ tests/

# Or Black format check
black --check src/ tests/
```

### 4. Security Scanning (if available)

```bash
# Bandit for security issues
bandit -r src/
```

## Output Format

```markdown
## Prepush Validation Results

### Test Results
| Metric | Value |
|--------|-------|
| Tests Run | N |
| Passed | N |
| Failed | N |
| Coverage | N% |

### Type Check Results
✅ **PASSED** or ❌ **FAILED**

### Lint Results
✅ **PASSED** or ❌ **FAILED**

---

## Verdict: ✅ READY TO PUSH or ❌ BLOCKED

### Required Actions (if blocked)
1. Fix failing test: `test_name`
2. Re-run /prepush
```

## Gate Rules

| Check | Failure Impact |
|-------|---------------|
| Tests | ❌ BLOCKS push |
| Type Check | ❌ BLOCKS push |
| Lint (errors) | ❌ BLOCKS push |
| Lint (warnings) | ⚠️ Logged |

**DO NOT proceed with /push until all checks pass.**
