# Triage Issue

Investigate a reported bug or unexpected behaviour by exploring the codebase, identify the root cause, and produce a structured fix plan.

## Process

### 1. Understand the report

Read the issue description. Extract:
- **Observed behaviour** — what's happening
- **Expected behaviour** — what should happen
- **Reproduction steps** — how to trigger it

If any of these are missing, ask me (max 2 questions).

### 2. Explore the codebase

Investigate the relevant area systematically:
- Find the entry point (view, management command, worker, orchestration step)
- Trace the execution path
- Check error handling and edge cases
- Look at related tests — what's covered and what's not

### 3. Identify root cause

Present your findings:
- **Root cause** — what's actually going wrong and why
- **Impact** — what's affected (other features, data integrity, user experience)
- **Confidence** — high/medium/low with reasoning

### 4. Propose fix plan

Structure the fix as a TDD plan:
1. Write a failing test that reproduces the bug
2. Implement the minimal fix
3. Verify all related tests still pass
4. Note any follow-up work needed

### 5. Check for related issues

Before finishing, check:
- Could this same bug pattern exist elsewhere in the codebase?
- Are there related areas with similar fragility?
- Should any existing tests be strengthened?

## Output format

```markdown
## Root Cause

[Clear explanation of what's going wrong]

## Impact

[What's affected and severity]

## Fix Plan

1. [ ] Test: [describe the failing test]
2. [ ] Fix: [describe the code change]
3. [ ] Verify: [what to check passes]

## Related Risks

[Any similar patterns elsewhere that might need attention]
```
