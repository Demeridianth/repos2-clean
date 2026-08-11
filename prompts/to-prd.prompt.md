# To PRD

Synthesise the current conversation context and codebase understanding into a PRD. Do NOT interview me — just produce the document from what you already know. If critical information is missing, note it as an open question rather than asking.

## Output format

Use this template:

---

## Problem Statement

What problem are we solving and why does it matter for Nexus / ViiV?

## Solution

High-level description of the approach. Reference existing Nexus patterns where applicable.

## User Stories

A numbered list of user stories:

1. As a [actor], I want [feature], so that [benefit]

Be extensive — cover happy paths, edge cases, error states, and admin/ops scenarios.

## Implementation Decisions

- Django apps and models affected
- API contracts (DRF serializers, endpoints)
- LLM integration details (prompts, models, orchestration)
- Architectural decisions and trade-offs
- Schema/migration changes

Do NOT include specific file paths or code snippets — they go stale.

## Testing Decisions

- What makes a good test for this feature
- Which modules need unit tests vs evals
- Prior art in the codebase (similar test patterns)

## Observability

- What should be traced (Phoenix/OTel)?
- What metrics or logs matter?

## Out of Scope

What we are deliberately NOT doing.

## Open Questions

Anything unresolved that needs a decision before implementation.
