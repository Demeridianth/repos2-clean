# Test-Driven Development

Build or fix features using strict red-green-refactor TDD. Work in small vertical slices.

## Workflow

### 1. Planning

Before writing any code:
- Understand the feature/bug fully by exploring the codebase
- Identify the public interface (DRF view, service function, orchestration step)
- List the test cases needed, ordered from simplest to most complex
- Confirm the plan with me before proceeding

### 2. Tracer bullet

Write ONE failing test that covers the thinnest possible end-to-end path. Make it pass with the simplest implementation. This proves the wiring works.

### 3. Incremental loop

For each remaining test case:

1. **Red** — Write a failing test. Run it. Confirm it fails for the right reason.
2. **Green** — Write the minimum code to make it pass. No more.
3. **Refactor** — Clean up while all tests stay green. Run the full suite.

### 4. Refactor

After all tests pass, look for:
- Duplication to extract
- Names to improve
- Unnecessary complexity to remove

## Rules

- **Never write production code without a failing test first.**
- Use `pytest` with fixtures from `conftest.py`. Follow `asyncio_mode = auto` for async tests.
- For eval-style tests, use the patterns in `evals/eval_helpers.py`.
- Run tests after every change — use `pytest` (or the repo’s standard test command).
- Keep tests focused on external behaviour, not implementation details.
- One assertion per test where practical.
