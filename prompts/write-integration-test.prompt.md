# Write Integration Test

Write hermetic integration tests for a pipeline component using the ports/adapters pattern with Azurite + Postgres Testcontainers.

## When to use

When a unit test with fakes cannot fully verify correctness — specifically:
- Blob path layout / prefix-scan idempotency (real blob endpoint needed)
- DB constraint validation (real schema needed)
- End-to-end CREATE/SOURCE phase correctness against both stores together

Do **not** use this for tests that fakes already cover — check whether a fake adapter already exists in `<app>/adapters/` first.

## Process

### 1. Verify the adapter layer is in place

Before writing any test, confirm:
- A `@runtime_checkable` Protocol exists in `<app>/ports/<service>.py`
- A fake implementation exists in `<app>/adapters/<service>.py` (bottom section)
- The component under test accepts the fake via DI or factory patch

If not, create a service adapter:

1. **Create the port** — `<app>/ports/<service>.py`:
   ```python
   """Protocol defining the <service> boundary.

   Production code should depend on this protocol, never on a concrete adapter directly.
   Wiring (choosing real vs fake) happens in <app>/services.py.
   """
   from __future__ import annotations
   from typing import Protocol, runtime_checkable

   @runtime_checkable
   class MyServicePort(Protocol):
       """Does X.

       Implementations:
           - Real: <app>.adapters.<service>.RealMyService
           - Fake: <app>.adapters.<service>.FakeMyService
       """

       def my_method(self, arg: str) -> str: ...
   ```

2. **Create the adapters file** — `<app>/adapters/<service>.py` with two sections. Real adapter uses lazy imports inside its methods to avoid importing prod dependencies at module load time. Fake adapter holds domain-specific in-memory state:
   ```python
   """<Service> adapters — real and fake — for the <app> app.

   Both satisfy <app>.ports.<service>.MyServicePort.
   Production code wires the real adapter via <app>/services.py.
   Tests inject FakeMyService directly or monkeypatch the factory.
   """
   from __future__ import annotations

   # ---------------------------------------------------------------------------
   # Real adapter
   # ---------------------------------------------------------------------------
   class RealMyService:
       """Satisfies <app>.ports.<service>.MyServicePort."""

       def my_method(self, arg: str) -> str:
           from some.production.lib import do_thing  # lazy import — keeps prod dep out of test collection
           return do_thing(arg)

   # ---------------------------------------------------------------------------
   # Fake adapter
   # ---------------------------------------------------------------------------
   class FakeMyService:
       """In-memory fake satisfying MyServicePort. Inject in tests."""

       def __init__(self) -> None:
           self._store: dict[str, str] = {}  # domain-specific state, not a generic call log

       def my_method(self, arg: str) -> str:
           result = f"fake-{arg}"
           self._store[arg] = result
           return result
   ```

3. **Create `<app>/services.py`** — factory functions that production code calls; tests monkeypatch these:
   ```python
   """Service factories for <app>. Tests monkeypatch these to inject fakes."""
   from __future__ import annotations
   from <app>.ports.<service> import MyServicePort

   def get_my_service() -> MyServicePort:
       """Return the real adapter. In tests, monkeypatch this to return FakeMyService()."""
       from <app>.adapters.<service> import RealMyService
       return RealMyService()
   ```

4. **Wire the component** — production code calls `services.get_my_service()` rather than importing the adapter directly. Tests monkeypatch the factory:
   ```python
   with patch("<app>.my_module.services.get_my_service", return_value=FakeMyService()):
       result = my_function()
   ```

### 2. Decide: fake or real backend?

| Need | Use |
|---|---|
| Logic / output shape | Fake adapter — unit test |
| LLM call (deterministic or multi-call) | `scripted_gpt_call` + `patch("module.async_call_gpt_v2", ...)` |
| Key Vault secret lookup | `_block_key_vault` session guard — automatic, no opt-in |
| Assert on emitted OTel spans | `span_exporter` fixture (in-memory, no Azure) |
| Blob actually written at correct path | `real_services` + Azurite |
| DB constraint / FK / enum validation | `real_services` + Postgres |
| Idempotency via blob prefix scan | `real_services` + Azurite |

If the answer is "fake covers it" — stop here.

### 3. Check fixtures in root conftest.py

The root `conftest.py` is the **single source of truth**. Never create a per-folder `conftest.py`.

Available fixtures:
- `real_services` (session-scoped) — `Settings` wired to live `AzuriteContainer` + `PostgresContainer`
- `clean_blob` (function-scoped) — wraps `real_services`; deletes all blobs after each test
- `clean_db` (function-scoped) — wraps `real_services`; truncates all `gt_*` tables after each test

If a new app needs additional teardown, add a new fixture to root `conftest.py` — not a local one.

### 4. Write a _seed() helper

Seed helpers must satisfy all real schema constraints. Before writing, check:
- `<app>/sql/*.sql` — exact `CHECK` constraint values (e.g. `file_type IN ('approved','draft','annotated')`)
- `<app>/db.py` — which fields are required vs optional
- What the pipeline function calls to find eligible rows (e.g. `current_status = 'source_complete'`)

Seed helper pattern:
```python
def _seed(settings, file_id=None):
    fid = file_id or str(uuid.uuid4())
    blob_io.upload_blob(settings, settings.outbox_container, f"checkpoints/source/{fid}.json", payload)
    conn = db.get_connection(settings)
    try:
        db.insert_source_file(conn, file_id=fid, ..., file_type="approved", current_status="source_complete")
        conn.commit()
    finally:
        conn.close()
    return fid
```

### 5. Investigate the feature under test

Before writing a single test, scan the target folder/feature to understand what is actually happening. This step is feature-specific — the test plan that comes out of it will differ for every app.

#### 5a. Scan the folder

Read the following artefacts for the target `<app>`:
- **Entry points** — management commands (`<app>/management/commands/`), views (`views.py`), Celery tasks, LangGraph nodes, or async pipeline functions. What is the public surface?
- **Business logic** — what transformations happen between input and output? Where are the branching conditions (skipping, retrying, overwriting)?
- **Service boundaries** — which external services does this code call? (blob storage, DB, LLM, Key Vault, another Django app). Use `grep_search` for imports of `blob_io`, `db`, `async_call_gpt_v2`, `SecretClient`, `requests`, etc.
- **DB writes** — which tables are written and in what order? What FK/CHECK/UNIQUE constraints apply? Read `<app>/sql/*.sql` and `<app>/db.py`.
- **Existing tests** — check `<app>/tests/` for what unit tests already exist. Integration tests must not duplicate unit test coverage; they must prove something the fakes cannot.

#### 5b. Diagnose the coverage gap before planning

Before listing scenarios, check what the **existing** test suite already asserts. Open every test file in `<app>/tests/` and ask:

- Do any tests assert individual output field values (e.g. `result.title == expected`)? If not, field-level happy-path coverage is missing.
- Do tests only assert aggregate counts, a single status field, or `field is not None`? Those are variant guards, not happy-path coverage — they pass even when the field holds the wrong value.
- Is the outermost entry point (worker, task, view, command) tested at all, or do tests only call internal helpers directly?
- Is there a test that exercises the component with all optional enrichment disabled? If not, the base ingestion / transformation path is uncovered.

> **Signal:** if the existing suite has many tests but none assert a specific output value end-to-end, happy-path coverage is missing regardless of test count.

#### 5c. Produce a test plan

After scanning, write a short test plan **before creating any files**. The plan must:

1. List each high-level scenario in plain English — e.g. "all output fields written correctly on first run"
2. For each scenario state:
   - **What it proves** — the specific invariant, constraint, or service-boundary behaviour
   - **Which backends are exercised** — blob only / DB only / both
   - **What seed data is needed** — which DB rows, blobs, or input files must exist beforehand
   - **What to assert** — specific field values in output records, blob content, return value, or emitted spans
3. **Happy paths first** — plan these before variant cases:
   - One **base path with no external enrichment** — the component's successful execution with all optional external calls disabled (LLM, third-party API, etc.). Requires no patches. Assert every output field value exactly against the seed data.
   - One **full pipeline e2e path** — the outermost public entry point exercised end-to-end with any external calls scripted. Assert specific values in every output — not just a status field or row count.
   - One **data-volume / boundary path** if the component processes items in batches, chunks, or pages — use a dataset that crosses the boundary and assert that every item survives.
4. **Variant and constraint cases** — plan these after the happy paths:
   - One **guard / skip condition** (idempotency, deduplication, or pre-condition check)
   - One **constraint validation** — a scenario that would fail if the schema changed (FK violation, enum mismatch, UNIQUE conflict)
   - Any additional **external-call failure or partial-failure** path the component handles
5. Omit any scenario that a fake/unit test already covers

Present the plan as a numbered list. **Do not create files until the plan is confirmed.**

#### 5d. Write the tests

With the plan agreed, implement one test per scenario from the plan.

**Rules for all tests:**
- Name each test to map directly back to its scenario (e.g. `test_all_output_fields_written`, `test_pipeline_entry_point_e2e`)
- Use only fixtures and helpers already established in steps 3–4
- Assert on structure and state, never on generated text content

**Additional rules for happy-path and e2e tests:**

- **Assert field values, not presence.** `row.field is not None` is a variant guard. `row.field == expected_value` — where `expected_value` comes from seed data or a scripted external response — is a happy-path assertion.
- **Start from the outermost entry point.** An e2e test must call the top-level public function (worker, task, view, command), not an internal helper. Skipping the outer layer leaves the wiring between orchestrator and implementation untested.
- **Cover every output field, not just the headline one.** If the component writes N columns, the field-fidelity test should assert all N — not only the one the feature is named after.
- **The base path needs no patches.** If the component can run successfully with all optional external calls disabled, test that configuration without any `patch()`. This proves the core transformation is not accidentally coupled to the enrichment path.
- **Data-volume tests only need count assertions.** For batching / chunking tests, `count == N` is the correct assertion — the goal is proving no items are lost at boundaries, not field correctness.

### 6. Place, mark, and document tests

- File: `<app>/tests/integration/test_<phase>.py`
- Mark: `pytestmark = pytest.mark.integration` at module level
- Use `clean_blob` and `clean_db` fixtures (not `real_services` directly) for test isolation
- **No `__init__.py`** in test directories — adding one causes `ModuleNotFoundError: No module named 'tests.integration'` at collection time.
- **No local `conftest.py`** inside an integration subfolder — root `conftest.py` only.

#### Required module docstring

Every integration test file **must** open with a docstring that covers: what the test exercises, why this area is worth testing with a real backend (not mocks), exactly what is patched and why, and what fixtures exist. Use the template below — adapt content freely, but keep the headings.

```python
"""
Integration: <component> → <dependency> (<brief qualification e.g. ×3 pipeline stages>)

Why we are testing this area:
  <One to three sentences stating the specific invariant that only a real backend can
  verify — e.g. SELECT FOR UPDATE atomicity, FK constraint enforcement, multi-call LLM
  sequencing, blob-path layout.  State what the existing test suite already covers and
  what gap these tests fill.  Reference docs/feature_folder_map.md Feature N when the
  boundary is listed there.>

  1. <Short label — what it proves> — <one sentence: the specific invariant, the gap
     in the existing suite, or the code path no other test reaches.>

  2. <Short label — what it proves> — <...>

  3. <Short label — what it proves> — <...>

  (Add one numbered item per test.  Labels must match the test function names.)

Patches:
- <import.path.patched>: <what it's scripted to return and what is asserted on
  it — e.g. call_count, args — so a reader knows what the mock is proving>.
- <import.path.patched>: <why this dependency is stubbed — what it avoids and
  what is therefore NOT under test>.

Fixtures:
- <helper / fixture name>: <what minimal DB-backed or in-memory object it
  creates and why that shape is sufficient>.
- <param>=<value>: <which code path that exercises>.

Skipped: <what is explicitly not tested here and why — or N/A>
"""
```

**Guidance on each section:**

- **Opening line** — `Integration: <what> → <what it calls>` gives grep-friendly context at a glance.
- **Why we are testing this area** — the most important section. Split into two parts:
  - A grounding paragraph: name the specific service-boundary behaviour that makes a real backend necessary, what the existing suite covers, and what gap these tests fill.
  - A numbered list: one item per test, each with a short label that matches the test function name and one sentence explaining what invariant it proves.  This lets a reader trace any test back to its rationale without opening the test body.
- **Patches** — list every `patch(...)` call. For each one say what it returns *and* what is asserted on it (or "not asserted — avoids X dependency"). A patch with no assertion note is a smell.
- **Fixtures** — explain the shape of seed data and which code path each param exercises. Don't just name the fixture; say why that shape.
- **Skipped** — explicitly document what is out of scope so future authors don't add redundant tests.

---

## Azure OpenAI LLM calls

When a component under test calls an LLM, patch `async_call_gpt_v2` — **never hit real Azure in CI**.

### Pattern: `scripted_gpt_call` + `patch`

```python
from unittest.mock import patch
from slide.adapters.llm import scripted_gpt_call

# Single response — any object whose attributes the code-under-test reads
with patch("my.module.async_call_gpt_v2", scripted_gpt_call(MyModel(field="value"))):
    result = await my_function()

# Multiple responses returned in order
with patch("my.module.async_call_gpt_v2", scripted_gpt_call(resp1, resp2, resp3)):
    ...
```

The patch target is the **import site in the caller's module**, not `slide.utils`:

```python
# my/module.py imports:  from slide.utils import async_call_gpt_v2
# → patch target:        "my.module.async_call_gpt_v2"
```

`scripted_gpt_call` returns an `AsyncMock`:
- Single value → `return_value=value` (repeated on every call)
- Multiple values → `side_effect=[v1, v2, ...]` (consumed in order; `StopAsyncIteration` if exhausted)

**Policy: assert on structure, never on generated text content.** Generated content quality is an eval concern.

### Where things live

| Artefact | Path |
|---|---|
| `scripted_gpt_call` helper | `slide/adapters/llm.py` |
| Canonical usage examples | `slide/tests/integration/test_llm_adapters.py` |
| Real LLM call function | `slide/utils.py` → `async_call_gpt_v2` |

### No `__init__.py` in test directories

Test directories under an app (`review/tests/`, `review/tests/integration/`) must **not** have `__init__.py`. The top-level `tests/` package already owns that namespace — adding `__init__.py` in a nested `tests/` folder causes `ModuleNotFoundError: No module named 'tests.integration'` at collection time.

---

## Rules

- Never add a `conftest.py` inside an integration test subfolder — root only.
- Never touch prod code (`db.py`, `blob_io.py`, `pipeline.py`, SQL files) to make tests pass.
- If a SQL file has a BOM or encoding issue, strip it from the file itself — not by changing the reader.
- Seed data must use valid enum values from the real schema — read the SQL files, not the unit test mocks.
- Blob path assertions must use the real `output_blob_path()` helper or check the correct prefix — never hardcode assumed paths.
- `AzuriteContainer.get_connection_string()` — use this, never build the connection string manually.
- psycopg3 URL format: `postgresql://` not `postgresql+psycopg2://` — strip the driver suffix from `get_connection_url()`.
- If migrations reference a schema (`SET search_path TO gt`), pre-create it in `real_services` before calling `db.migrate()`.
- LLM tests: assert on structure (which candidate, did parsing succeed), never on generated text. Zero real OpenAI calls in CI.
- OTel tests: use `span_exporter` fixture; never assert on text content of span attributes. `configure_azure_monitor` is always a no-op in tests.

---

## OpenTelemetry / App Insights

Telemetry is a **no-op** in all tests. No network calls, no App Insights data.

### Why this matters

`configure_azure_monitor(connection_string="")` makes a real network call to the Azure VM metadata endpoint (`169.254.169.254`) even with an empty connection string — it probes for Azure resource context before validating. The call times out after 0.2 s and raises `ValueError`, which `_setup_otel()` catches. But because `_otel_initialised` never becomes `True`, every LLM call in tests re-triggers this 0.2 s timeout.

### How it is blocked

The `_configure_test_telemetry` session autouse fixture in `conftest.py`:
1. Installs an `opentelemetry.sdk.trace.TracerProvider` with an `InMemorySpanExporter` as the global provider
2. Sets `slide.utils._otel_initialised = True` so `_setup_otel()` exits immediately
3. Patches `slide.utils.configure_azure_monitor` to a `MagicMock` — no calls reach the real function

### Testing code that emits spans

Request the `span_exporter` fixture (function-scoped, clears state between tests):

```python
def test_worker_emits_span(span_exporter):
    span_exporter.clear()  # optional — fixture already clears
    my_worker_function()
    spans = span_exporter.get_finished_spans()
    assert any(s.name == "slide.generate" for s in spans)
    assert spans[0].attributes["job_id"] == "expected-job-id"
```

**Rules:**
- Assert on span names and structured attributes (job_id, user_id, chat_id). Never assert on text content of span attributes — that's an eval concern.
- Never call `trace.set_tracer_provider()` inside a test — it can only be set once per process (OTel SDK guard).
- Never patch `configure_azure_monitor` inside individual tests — the session fixture handles this globally.

### Where things live

| Artefact | Path |
|---|---|
| Session guard + `span_exporter` fixture | `conftest.py` → `_configure_test_telemetry`, `span_exporter` |
| OTel setup code under test | `slide/utils.py` → `_setup_otel()`, `_otel_initialised` |
| Infrastructure tests | `slide/tests/integration/test_otel.py` |

---

## Azure Key Vault secret lookups

When a component under test calls Key Vault (directly or via a helper), **never let real Azure auth run in CI**.

### Two-layer defence

**Layer 1 — session guard (automatic)**
`conftest.py` has a session-wide autouse fixture `_block_key_vault` that patches:
- `viiv.helpers.SecretClient` — the module-level import in `helpers.py`
- `azure.keyvault.secrets.SecretClient` — catches any lazy imports
- `viiv.helpers.get_sp_credential` — prevents `ClientSecretCredential` from running with `None` env vars

This fixture fires for every test automatically. No opt-in required.

**Layer 2 — patching legacy code that creates SecretClient directly**

For functions that call Key Vault directly (e.g. `viiv.helpers.get_speech_service_token`), patch all three call sites explicitly:

```python
from unittest.mock import MagicMock, patch

with patch("viiv.helpers.SecretClient") as mock_kv, \
     patch("viiv.helpers.requests.post") as mock_post, \
     patch("viiv.helpers.get_sp_credential", return_value=MagicMock()):
    mock_kv.return_value.get_secret.return_value.value = "fake-resource-id"
    mock_post.return_value.json.return_value = {"access_token": "fake-token"}

    result = get_speech_service_token()

assert result == "aad#fake-resource-id#fake-token"
```

**Why `get_sp_credential` must also be patched:** `SecretClient(credential=get_sp_credential())` — the credential is evaluated *before* the patched `SecretClient` is called. Patching only `SecretClient` still lets `ClientSecretCredential` run with `None` env vars and raise `ValueError`.

### Where things live

| Artefact | Path |
|---|---|
| Session guard | `conftest.py` → `_block_key_vault` |
