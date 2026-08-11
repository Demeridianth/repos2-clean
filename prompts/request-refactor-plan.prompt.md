# Request Refactor Plan

Create a detailed refactor plan with safe, incremental steps via user interview.

## Process

1. **Ask me** for a detailed description of the problem and any ideas for solutions.

2. **Explore the codebase** to verify my assertions and understand the current state. Check:
   - How the code is currently structured
   - What tests exist for this area
   - What other modules depend on this code
   - Whether similar refactors have been done before in the codebase

3. **Ask whether I've considered other options**, and present alternatives with trade-offs.

4. **Interview me** about the implementation. Be extremely detailed and thorough. Cover:
   - Exact scope — what changes and what doesn't
   - Migration strategy — can it be done incrementally?
   - Test coverage — is it sufficient to refactor safely?
   - Rollback plan — what if it goes wrong?

5. **Check test coverage** of this area. If insufficient, ask about testing plans before proceeding.

6. **Produce the refactor plan** using this template:

---

## Problem Statement

What's wrong with the current code and why does it need to change?

## Proposed Solution

High-level description of the target state.

## Incremental Steps

Break into the smallest safe commits. Each step must:
- Leave all tests passing
- Be independently reviewable
- Not break the application

For each step:
- **Step N: [title]**
  - What changes
  - What tests to add/update
  - Risk level (low/medium/high)

## Out of Scope

What we're deliberately NOT changing in this refactor.

## Testing Strategy

How we ensure nothing breaks — before, during, and after.
