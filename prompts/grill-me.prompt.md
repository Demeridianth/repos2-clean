# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one by one. For each question, provide your recommended answer.

Ask the questions **one at a time**, waiting for feedback on each before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead of asking me.

## Focus areas

- Does this fit within the existing Nexus architecture (Django apps, DRF views, LangChain orchestration)? 
- Are there existing patterns in the codebase that should be followed or deliberately broken?
- What are the edge cases for LLM-dependent features (timeouts, token limits, content filtering)?
- How will this be tested? (pytest, evals, or both?)
- Does this touch settings/secrets that come from Key Vault?
- What's the migration/rollback story?
- How does this affect observability (Phoenix tracing, OTel)?

## Rules

- Be specific — reference actual files, Django apps, and existing patterns you find.
- Challenge vague answers — "it depends" is not acceptable without listing what it depends on.
- If I haven't considered an option, present it with pros/cons.
- When we reach agreement on a decision, summarise it clearly before moving on.
