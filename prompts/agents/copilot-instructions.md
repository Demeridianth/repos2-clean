# Copilot Instructions

## Project overview

**Nexus** is a Django 5.x application (Python 3.12) that provides LLM-powered medical content generation for ViiV Healthcare. It uses Azure OpenAI via a Kong API gateway, with endpoints and secrets stored in Azure Key Vault and exposed through `viiv/settings.py`.

You have access to the Nexus confluence via /confluence_docs. This contains many developer guides and architecture plans. Always refer to this first if you are trying to find something out about the codebase - if the correct information doesnt exist, then you may do self-investigation. 


### Key tech stack

- **Backend:** Django 5.x, Django REST Framework, uWSGI
- **LLM clients:** `openai` SDK via `TokenRefreshingAzureClient` in `viiv/helpers.py` (supports both sync and async)
- **Orchestration:** LangChain / LangGraph for chat agents
- **Observability:** Phoenix (Arize) for LLM tracing + experiments, OpenTelemetry (pinned to 1.38.0)
- **Testing:** pytest, pytest-asyncio (`asyncio_mode = auto`), pytest-django
- **Evals:** `evals/` directory — pytest + Phoenix Experiments + openevals (LLM-as-judge)
- **CI/CD:** Azure DevOps Pipelines (build/deploy), GitHub Actions (code quality, evals)
- **Dependencies:** Poetry → `pyproject.toml` → `poetry lock` → `poetry export` → `requirements.txt`

---

## Principles

- Put all temporary or local working outputs inside /tmp, add dirs accordingly.
- Put all ad hoc, one off or local scripts inside /scripts. Don't spread them out across the codebase.


### 1. Single source of truth — never duplicate config

Before creating any new config, registry, or constant:
- **Search the codebase** for existing definitions of the same concept.
- If it already exists somewhere, import from there or suggest centralising.
- If you must create a new source of truth, put it in **one file** and have everything else read from it.

Examples:
- Model registry lives in `.github/workflows/endpoint_config.json` — `conftest.py` derives `MODEL_REGISTRY` from it, `evals.yml` references it.
- Django settings come from `viiv/settings.py` (Key Vault) — never hardcode endpoint URLs.
- OTel version is pinned once in `pyproject.toml` — don't pin in multiple places.

### 2. Always finish with a sanity check

Never say "done" or "complete" until the code **actually runs**:
- After code edits, run a quick syntax compile check first: `./venv/Scripts/python.exe -m compileall <changed-files>`.
- After any code change, **run the relevant tests or commands** and show the output.
- If tests fail, fix the issue before declaring completion.
- For multi-file changes, run the full affected test suite, not just one file.

### 3. Verify files on disk, not just in editor

The editor buffer and the file on disk can diverge (unsaved changes, formatter rewrites, folder renames). When debugging import errors or unexpected behaviour:
- Use the terminal (`Get-Content`, `cat`) to read the actual file on disk.
- Clear `__pycache__` directories after renaming or moving files.

### 4. Prefer simplicity and abstraction

- New eval tests should be ~30 lines: dataset + task + scorers + `run_eval()`.
- Don't build custom infrastructure when a library already does it (e.g. openevals for LLM-as-judge, Phoenix Experiments for dataset management).
- When wrapping a library, keep the wrapper thin — pass through kwargs, don't re-implement.


### 5. Prioritise Testable Code Above All Else
Testability is the highest-priority design constraint. When it conflicts with cleverness, brevity, or personal style preferences, testability wins. Code that cannot be tested easily is code that cannot be trusted, refactored safely, or handed off.
Core principles
Write functions that are deterministic and pure wherever possible. Given the same inputs, a function should return the same outputs with no hidden state changes. Push side effects (database writes, API calls, file I/O, logging, time, randomness) to the edges of the system so the core logic remains a pure transformation that is trivial to test.
Separate orchestration from computation. A Django management command, LangGraph node, or API endpoint should be a thin orchestrator that wires together pure functions. The pure functions hold the logic worth testing; the orchestrator just calls them in order. If you find yourself writing complex branching inside an async command or a graph node, extract it.
Depend on abstractions, not concretions. Accept clients, sessions, and configuration as arguments rather than importing them at module level or instantiating them inside functions. An Azure OpenAI client, a PostgreSQL connection, an HTTP session — all should be injectable so tests can pass in fakes or mocks without monkeypatching.
Rules of thumb

If a function needs more than two mocks to test, it is doing too much. Split it.
If testing a function requires spinning up the full Django app, the function belongs in a plain module, not a view or command.
No hidden I/O. A function named calculate_x must not write to the database. If it does, rename it or remove the side effect.
Every async function should be testable with pytest-asyncio and explicit fakes — not by patching asyncio internals.
Avoid datetime.now(), uuid.uuid4(), and random.* inside logic. Inject a clock or ID generator.
Prefer returning data over mutating it. Return the new state; let the caller persist it.
Error handling paths must be as testable as happy paths. If you cannot easily trigger a retry or a timeout in a test, restructure the code.

#### What to avoid
Do not reach for module-level singletons, global configuration objects, or class-level mutable state. Do not hide dependencies inside decorators or middleware when they are genuinely part of the function's contract. Do not write code that can only be tested end-to-end — that is a failure of design, not a feature.
When in doubt
Write the test first. If the test is painful to write, the code is wrong. Fix the code, not the test.


---

## Codebase conventions

### Python

- **Imports:** Use absolute imports (`from ai.queries import ...`, `from evals.eval_helpers import ...`).
- **Async:** Tests are `def` (sync), task functions are `async def`. Phoenix's `run_experiment` manages the event loop. `asyncio_mode = auto` in `pytest.ini`.
- **Type hints:** Use them for public functions. Use `from __future__ import annotations` for modern syntax.
- **Django settings:** Access via `from django.conf import settings` then `settings.AZURE_OPENAI_4O_API_ENDPOINT`, never via `os.environ` for Key Vault values.

### OpenAI clients

- **Async client:** `from viiv.helpers import initialise_oai_client` → returns `TokenRefreshingAzureClient` wrapping `AsyncAzureOpenAI`
- **Sync client:** `from viiv.helpers import initialise_oai_client_sync` → returns `TokenRefreshingAzureClient` wrapping `AzureOpenAI`
- Both require `api_version=settings.AZURE_OPENAI_API_VERSION` and `base_url=<endpoint>`.

### Evals (`evals/`)

- **Test authors import from `evals/eval_helpers.py` only** — that's the public API.
- **Scorers:** `exact_match`, `contains`, `match_any`, `valid_format`, `llm_judge`.
- **Datasets:** JSON files in `evals/datasets/`, loaded via `load_dataset("name")`.
- **Models:** Defined in `.github/workflows/endpoint_config.json`, selected via `--model` / `--judge-model` CLI flags.
- **Categories:** Tag with `@pytest.mark.eval_category("name")` + `category="name"` in `run_eval()`.

### Dependencies

- **Always update `pyproject.toml` first**, then `poetry lock`, then `poetry export -f requirements.txt --output requirements.txt`.
- Never manually edit `requirements.txt` — it's generated.
- Watch for Python version constraints in transitive dependencies (e.g. `arize-phoenix` requires `<3.14`).

### OpenTelemetry

- **All OTel core packages must be on the same version** (currently 1.38.0). Mismatched versions cause silent tracing failures.
- `slide/utils.py` has a guard that skips its OTel setup when `PHOENIX_COLLECTOR_ENDPOINT` is set — don't remove this.

---

## Environment

- **OS:** Windows (PowerShell)
- **Python:** 3.12.9, venv at `viiv_venv_2/`
- **Shell encoding:** Set `$env:PYTHONIOENCODING="utf-8"` before running Phoenix-related commands (emoji output).
- **Env vars:** Loaded from `.env` via `python-dotenv` in `evals/conftest.py`. Phoenix vars: `PHOENIX_COLLECTOR_ENDPOINT`, `PHOENIX_API_KEY`, `PHOENIX_CLIENT_HEADERS`, `PHOENIX_PROJECT_NAME`.

---

## Common pitfalls (learned the hard way)

| Pitfall | Fix |
|---|---|
| `ModuleNotFoundError` after renaming a directory | Clear `__pycache__`, update `pytest.ini` testpaths, fix all imports |
| Phoenix tracing not working | Check OTel version alignment, verify endpoint has `/v1/traces` suffix, ensure `slide/utils.py` isn't overriding the TracerProvider |
| `openevals` Protocol check fails on `TokenRefreshingAzureClient` | The client needs an explicit `chat` property — `__getattr__` proxy doesn't satisfy `@runtime_checkable` |
| `poetry lock` fails with Python range error | Add `python = ">=3.10,<3.14"` constraint to the offending dependency |
| Editor shows different content than disk | Use terminal to read the actual file, don't trust cached editor state |
| GitHub Actions `choice` inputs can't be dynamic | Hardcode options in YAML, add comment pointing to the source of truth file |


DON'T look inside .env ever. 

Always offer a PR description and title at the end of a block of work or before pushing everything to remote. you can find the template in PULL_REQUEST_TEMPLATE.md