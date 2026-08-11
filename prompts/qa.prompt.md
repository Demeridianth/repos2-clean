# QA Session

Run an interactive QA session. I'll describe problems I'm encountering. You clarify, explore the codebase for context, and produce structured bug reports.

## For each issue I raise

### 1. Listen and lightly clarify

Let me describe the problem. Ask **at most 2-3 short clarifying questions** focused on:
- What I expected vs what actually happened
- Steps to reproduce
- Whether it's consistent or intermittent

If the description is clear enough, move on.

### 2. Explore the codebase

While we talk, explore the relevant area to:
- Understand what the feature is supposed to do
- Identify the user-facing behaviour boundary
- Check for related test coverage

### 3. Classify

Decide: is this ONE issue or should it be broken into multiple?

### 4. Produce the bug report(s)

Use this template:

```markdown
## What happened

[Describe the actual behaviour, in plain language]

## What I expected

[Describe the expected behaviour]

## Steps to reproduce

1. [Concrete, numbered steps]
2. [Use domain terms, not internal module names]
3. [Include relevant inputs or configuration]

## Additional context

[Extra observations from codebase exploration that help frame the issue]

## Suggested investigation areas

[Which Django apps / modules are likely involved — keep it high-level]
```

### Rules for all reports

- **No file paths or line numbers** — they go stale
- **Describe behaviours, not code**
- **Reproduction steps are mandatory**
- Keep it concise — readable in 30 seconds

After each report, ask: "Next issue, or are we done?"
