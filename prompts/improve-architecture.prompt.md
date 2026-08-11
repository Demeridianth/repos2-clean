# Improve Codebase Architecture

Explore the Nexus codebase for architectural improvement opportunities, focusing on reducing coupling, deepening shallow modules, and improving testability.

## Process

### 1. Explore the codebase

Navigate organically and note where you experience friction:
- Where does understanding one concept require bouncing between many files?
- Where are modules so shallow that the interface is nearly as complex as the implementation?
- Where are things tightly coupled that shouldn't be?
- Which parts are untested or hard to test?
- Where are Django apps doing too much or too little?

### 2. Present candidates

Present a numbered list of improvement opportunities. For each:
- **Cluster** — which modules/concepts are involved
- **Why it's a problem** — coupling, complexity, testability, or clarity
- **Impact** — what breaks or gets harder because of this
- **Effort** — rough size (small/medium/large)

Do NOT propose solutions yet. Ask me which candidate to explore.

### 3. Deep dive

For the selected candidate:
- Map all the dependencies (who calls what, who imports what)
- Identify the "information hiding" opportunity — what complexity can be pushed behind a simpler interface
- Check what tests exist and what boundary tests would replace them

### 4. Propose options

Present 2-3 different approaches with trade-offs:
- **Option A:** Minimal change — least disruption
- **Option B:** Clean solution — best architecture
- **Option C:** Pragmatic middle ground

For each, show: interface sketch, what callers change, what tests change, migration path.

### 5. Plan

Once we agree on an approach, produce an incremental refactor plan (same format as `request-refactor-plan.prompt.md`, invoked as `#request-refactor-plan`).

## Architectural planning layers

When analysing a candidate in step 3 and designing options in step 4, reason through these layers in order. Decisions at upper layers constrain lower ones — skipping layers is how refactors end up solving the wrong problem.

1. **Data requirements** — What information does this part of the system actually need to do its job? What's the canonical shape of the domain objects involved (claims, citations, documents, chunks, users)? What's incidental representation versus essential structure? Often the root cause of shallow modules is that the data model leaked outward instead of being owned by one place.

2. **Storage requirements** — Where does that data live and why? PostgreSQL tables, vector stores, blob storage, in-memory caches, session state. What are the access patterns (read-heavy, write-heavy, transactional, analytical)? What consistency guarantees are needed? Refactors often fail because callers assume synchronous strong consistency from something that should be eventually consistent, or vice versa.

3. **Domain / business logic** — What are the invariants and rules that must hold regardless of transport or storage? This is the layer that should be most testable in isolation. If business logic is tangled with Django ORM calls, HTTP concerns, or LLM API calls, that's usually the deepest refactor opportunity.

4. **Integration boundaries** — Where does this code talk to things it doesn't own? LLM APIs, Azure services, other Django apps, external HTTP services. Each boundary should have a clear seam with a typed interface, error contract, and a fake/stub for tests. Shallow modules often appear here because thin wrappers pass through without adding abstraction.

5. **Orchestration / control flow** — How are steps sequenced? Management commands, LangGraph nodes, Celery tasks, request handlers, async pipelines. Is the control flow explicit and inspectable, or hidden in implicit call chains? Async silent failures (the kind you've debugged before) usually live at this layer.

6. **Transport / interface** — HTTP views, CLI commands, chatbot tool definitions, internal Python APIs. This should be the thinnest layer — just adapting an external protocol to the domain. If views contain business logic, or if tool definitions know about database schemas, the layering has collapsed.

7. **Cross-cutting concerns** — Logging, auth, observability, error handling, retries, caching. These should compose onto the layers above without the core logic knowing about them. Ask: can I turn off logging/caching/auth without the business logic changing?

8. **Observability and evaluation** - For AI related components specifically, observability and evaluation are CORE. we need to be able to define "good" before we start. Measuring against "good" is a system requirements - hence a focus on observability. 
.
For each candidate, state explicitly which layer the problem primarily lives at, and which layers the fix will touch. A refactor that claims to be at one layer but ends up modifying five is a warning sign the diagnosis was wrong.