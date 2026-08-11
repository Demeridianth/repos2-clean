# Copilot Usage Guide — Nexus App Testing & UAT

## Overview
This guide documents workflows for using Copilot while performing UAT on the Nexus Unified Chatbot application, reviewing test cases in a test pack file, and debugging issues locally.

> **Note:** This guide is intentionally generic. Test pack filenames, sheet names, and column layouts vary per project — Copilot will always confirm these details before starting.

---

## 1. Testing Workflows

### 1.1 Test Execution
**Context:** Running functional test cases from a test pack (Excel, CSV, JSON, or plain text) against the live Nexus Unified Chatbot.

**Before Copilot starts running any tests, it must ask:**
1. **Fresh run or continue from previous results?** — If previous Actual Result / Status values already exist in the test pack, Copilot must ask: *"I can see existing results in the file. Do you want to start a fresh run (overwrite everything) or rely on the previous results and only re-run tests that are empty or failed?"* Never overwrite existing results without explicit confirmation.
2. **What format is the test pack, and which file?** — Copilot must ask the user which format their test pack uses. Options:
   - **Option 1 (default): Excel** — e.g. `UC Testing_Template_copy.xlsx`, `test-cases-v2.xlsx`. Copilot reads and writes using `openpyxl`.
   - **Option 2: CSV** — e.g. `test-cases.csv`. Copilot reads and writes using Python's `csv` module.
   - **Option 3: JSON** — e.g. `test-cases.json`. Copilot reads and writes using Python's `json` module.
   - **Option 4: Plain text / other** — Copilot asks for the structure and adapts accordingly.

   If the user does not specify, Copilot defaults to Excel and confirms before proceeding.
3. **Which sheet contains the test cases?** — e.g. `Functional Test Cases`, `Sheet1`
4. **Which column is Test ID, Expected Result, Actual Result, Status?** — Copilot reads the header row and confirms column mapping before writing anything.
5. **Should results be written back to the file?** — Some sessions are read-only (just report); others write Pass/Fail to the file.
6. **Test documents — will you provide them or should Copilot generate them?** — Copilot scans the test pack for any tests that reference a specific source file (e.g. a non-English document, a large file, a specific format). For each required file that is not already provided, Copilot must ask: *"Some tests need source documents that haven't been supplied (e.g. a French-language PDF for LN-08). Do you want to upload your own files, or should I generate realistic synthetic ones?"* Copilot must ask this once upfront for the whole run — not case-by-case mid-execution. If the user chooses to generate, Copilot creates the files using `reportlab` (PDF) or plain text and confirms each one before use.

**Copilot must ask these questions before running tests — never assume filenames, column positions, whether to overwrite existing results, or whether test documents are available.**

**Copilot Usage Pattern:**
- **Share browser page:** Open the chatbot at the app URL and share the page with Copilot using the browser attachment tool.
- **Reference test cases:** Read test pack rows directly or have Copilot extract test steps from the file.
- **Execute and report:** 
  - Copilot interacts with the UI (clicks, types, reads page state).
  - User observes and validates behavior.
  - Copilot records results (Pass/Fail) with error descriptions.
  - If any test **fails**, Copilot must:
    1. Record the actual result and mark it as Fail.
    2. Report the failure to the developer clearly: test ID, expected result, actual result.
    3. **Ask the developer: "This test failed — do you want me to continue with the remaining tests?"**
    4. Wait for an explicit yes/no before proceeding.
    5. Only continue if the developer confirms.
  - If any test **cannot be executed** (skipped, blocked, missing pre-condition, or environment limitation), Copilot must:
    1. Record the reason it could not be tested and mark it as N/A in the Status column.
    2. Report it to the developer clearly: test ID, reason it was skipped (e.g. "no non-English source document available"). Note: **network simulation is NOT a valid skip reason** — use the Playwright approaches in Section 3.3 instead.
    3. **Ask the developer: "[Test ID] was skipped — do you want me to continue with the remaining tests, or should we address the blocker first?"**
    4. Wait for an explicit yes/no/address-blocker response before proceeding.
    5. Only continue if the developer confirms. Do not silently skip tests and carry on.

**Example Request:**
```
"Run the File Upload test cases"
→ Copilot asks: which file? which sheet? which columns? write results?
→ Copilot reads test steps, executes in browser, reports result per test
→ On failure: reports Test ID + expected vs actual result, then asks:
   "FU-09 failed: expected all files accepted, actual: second file not shown.
    Do you want me to continue with the remaining tests?"
→ Waits for developer response before proceeding

→ On skip/not-tested: reports Test ID + reason it could not run, then asks:
   "LN-08 was skipped: no non-English source document available in the test files.
    Do you want me to continue with the remaining tests, or should we address this first?"
→ Waits for developer response before proceeding
```

### 🔴 Session expiry (app logout)
**Copilot detects session expiry after every navigation:**
- Page URL changes to `https://login.microsoftonline.com/...`
- Page title contains "Sign in to your account"

**When detected, Copilot MUST:**
1. **Stop the run immediately** — do not attempt any further test steps.
2. **Mark the interrupted test as N/A** with reason "Session expired mid-execution; re-run required."
3. **Report to the user clearly:**
   > *"⚠️ Session expired — the app has redirected to the Microsoft login page.*
   > *Testing has stopped. The last fully completed test was [last-passed Test ID].*
   > *[interrupted Test ID] was in progress and could not be completed — it will be re-run.*
   > *Please log back in, then tell me to continue and I will restart from [interrupted Test ID]."*
4. **Wait for explicit confirmation** from the user before doing anything else.
5. **On resume:** re-run the interrupted test from the beginning, then continue with the remaining tests in order.

**Do NOT:** mark the interrupted test as Fail, skip it, or attempt to continue while the login redirect is active.

### 1.2 Test Pack Review
**Context:** Reviewing, updating, or analyzing test cases in any test pack file (Excel, CSV, JSON, or plain text).

**Copilot Usage Pattern:**
- **Bulk updates:** Ask Copilot to populate result columns based on test execution summary.
- **Extraction:** Request Copilot to extract failing test IDs or group tests by category.
- **Mapping:** Link test IDs to code locations or backend functions.

**Before writing results back, Copilot always:**
1. Reads and prints the header row (or top-level keys for JSON) to confirm field names.
2. Confirms which fields map to Actual Result and Status (by name, not position).
3. Asks whether to overwrite existing values or skip already-filled rows.
4. Uses the appropriate library for the confirmed format: `openpyxl` for Excel, `csv` for CSV, `json` for JSON.

**Example Request:**
```
"Fill in the results for the tests we just ran"
→ Copilot asks: which file? what format? confirm field mapping → writes only after confirmation
```

---

## 2. Browser Interaction Patterns

### 2.1 Chatbot Navigation
**Best Practices:**
- Always share the browser page first (`open_browser_page` or drag existing tab).
- Use `read_page` to get current UI state before making assumptions.
- Chain interactions logically: upload → request → wait → verify response.
- Check for status spinners or "processing" indicators before declaring completion.

**Common Interactions:**
```
1. Upload file → type a message → send together → read response
2. Select option (audience/language) → confirm
3. Await generation completion → extract result
```

**Important: File Upload in UC Requires a Message**
The Unified Chatbot send button is disabled until there is text in the input box. When asking Copilot to upload a file, Copilot must also type a message in the same submit action — otherwise the send button will not fire and the file will never be sent to the backend.

**Correct approach (always use this):**
```javascript
// 1. Attach the file to the input
await page.locator('input[type="file"]').setInputFiles('/path/to/file.pdf');
// 2. Type a message in the textarea
await page.getByRole('textbox', { name: 'Type a message' }).fill('Please summarise this document');
// 3. Press Enter to send file + message together
await page.getByRole('textbox', { name: 'Type a message' }).press('Enter');
```

**Wrong approach (will silently fail):**
```javascript
// ❌ Setting the file without typing a message — send button won't trigger
await page.locator('input[type="file"]').setInputFiles('/path/to/file.pdf');
await page.getByRole('img', { name: 'Send' }).click(); // times out
```

### 2.2 Multi-Thread Testing
**Pattern:**
- Each thread is isolated; files uploaded in one thread don't appear in others.
- Use thread names to track state (e.g., "Thread 6: HIV Specialist, German, One-page").
- Create new threads for testing different personas/languages/summary types.

**Copilot Assistance:**
```
"In Thread 3, request a one-page summary for General Public in French"
→ Copilot navigates threads, types request, reports result
```

### 2.3 File Upload Capability
**Copilot can upload files from anywhere on your local system** — not just from the repo directory.

**File Sources:**
- ✅ Project repository: `./` or relative path from cloned repo
- ✅ Downloads folder: `~/Downloads/` (or equivalent per OS)
- ✅ Desktop: `~/Desktop/` (or equivalent per OS)
- ✅ Any absolute or relative path on disk with read permissions

**Platform-Specific Absolute Paths:**
| OS | Downloads | Desktop |
|---|---|---|
| **macOS** | `/Users/{user}/Downloads/` | `/Users/{user}/Desktop/` |
| **Windows** | `C:\Users\{user}\Downloads\` | `C:\Users\{user}\Desktop\` |
| **Linux** | `/home/{user}/Downloads/` | `/home/{user}/Desktop/` |

> **Note:** Replace `{user}` with the actual username, or use `os.homedir()` (Node) / `Path.home()` (Python) to resolve it programmatically. Never use `~` — it is a shell shorthand only and is not expanded by Playwright, Node.js, or Python's file APIs.

**How It Works:**
Copilot uses Playwright's `setInputFiles()` method, which requires an **absolute path** — `~` is a shell shorthand and is **not** expanded by Node.js or Python. Always resolve the home directory explicitly before passing it to `setInputFiles()`.

```javascript
// ✅ Correct — explicit absolute path
await page.locator('input[type="file"]').setInputFiles('/Users/sk797885/Downloads/document.pdf');

// ✅ Correct — programmatic home directory expansion (Node.js)
const path = require('path');
const os   = require('os');
await page.locator('input[type="file"]').setInputFiles(
  path.join(os.homedir(), 'Downloads', 'document.pdf')
);

// ❌ Wrong — ~ is NOT expanded by Playwright/Node; resolves to a literal ~ folder
await page.locator('input[type="file"]').setInputFiles('~/Downloads/document.pdf');
```

```python
# ✅ Correct — programmatic home directory expansion (Python)
from pathlib import Path
await page.locator('input[type="file"]').set_input_files(
    Path.home() / 'Downloads' / 'document.pdf'
)
```

**Example Requests (Universal Format):**
```
"Upload the PDF from Downloads and test file upload"
→ Copilot resolves the absolute path first, then:
   await fileInput.setInputFiles(path.join(os.homedir(), 'Downloads', 'document.pdf'));

"Upload a test file from the repo and generate summary"
→ Copilot uses an absolute repo path, e.g. '/Users/sk797885/dev/viiv_gen_ai_nexus/file.pdf'
```

**Practical Use Cases:**
- Test with files from different locations to validate upload handling
- Use test documents stored locally without copying to repo
- Share test data across team members on different machines using relative paths
- Automate batch uploads from various sources during UAT

#### Missing Test Files (mid-run)
If a required file is discovered to be missing during test execution (i.e. it was not caught in the upfront question), Copilot must **stop and ask** rather than skip or mark N/A immediately:

```
"[Test ID] requires a [description] file (e.g. a French-language source document).
 Do you want to:
  (a) supply your own file — tell me the path and I'll use it, or
  (b) have me generate a synthetic one?"
```

If the user chooses **(b) generate**, Copilot:
1. Creates a realistic synthetic document using `reportlab` (for PDF) or writes a plain-text `.txt` file — matching the language, domain, and file format the test requires.
2. Saves it to `./tmp/uat/` (already gitignored via `tmp` in `.gitignore`) by default, so it never pollutes the working tree or risks accidental commits. Only saves to the repo root if the user explicitly asks for a reproducible, committed artefact.
3. Notes in the Actual Result cell that a synthetic file was used and the path where it was saved, so the result is reproducible.

**Example — LN-08 (cross-language source):**
```python
# Copilot generates a French HIV study PDF using reportlab
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate('ln08-french-source.pdf', pagesize=A4)
styles = getSampleStyleSheet()
story = [
    Paragraph("Efficacite du dolutegravir chez les patients naifs", styles['Title']),
    Paragraph("Cette etude randomisee a evalue l'efficacite virologique...", styles['Normal']),
]
doc.build(story)
# → saves ln08-french-source.pdf → uploads it → runs LN-08
```

---

## 3. Error Handling & Debugging

### 3.1 Common Issues

**Database Corruption** (`sqlite3.DatabaseError: database disk image is malformed`)
- **Symptom:** Streaming errors when initiating generation.
- **Root Cause:** Corrupted `checkpoints1.db` or `db.sqlite3`.
- **Fix:**
  ```bash
  rm -f checkpoints1.db checkpoints1.db-shm checkpoints1.db-wal
  rm -f db.sqlite3
  python manage.py migrate
  ```

**Copilot can automate this:**
```
"I'm getting 'database disk image is malformed'. Fix it."
→ Copilot identifies corrupted files, deletes them, runs migrations
```

### 3.2 Streaming Hangs
**Symptom:** Post-confirmation, status bar loops indefinitely ("Analyzing...", "Thinking...", etc.).
- **Test IDs Affected:** AU-04, CF-03, SG-02, SG-05
- **Workaround:** Refresh page (Copilot can detect and suggest).
- **Expected Fix:** Backend generation logic needs review.

**Ask Copilot:**
```
"Generation hangs after confirmation. Is this a known issue?"
→ Copilot reviews session notes and defect list
```

### 3.3 Network / Connection Failure Simulation

**When a test case involves a network drop, connection abort, or mid-request failure (e.g. ER-01 "Network drop mid-generation"), do NOT skip it.** Playwright provides two reliable in-process approaches — use one of them.

#### Approach A — `page.context().setOffline()` (full network cut)
Simulates a complete network drop at the OS level for the browser context. Best for testing what happens when the server becomes unreachable mid-operation (e.g. polling a long-running task).

```javascript
// 1. Start the operation and wait for it to reach an active in-progress state
//    (e.g. status bar shows "Pre-processing..." or "Waiting for capacity...")
await page.getByRole('textbox', { name: 'Type a message' }).fill('Yes');
await page.getByRole('textbox', { name: 'Type a message' }).press('Enter');

// Wait for the status bar to confirm generation is in progress
let statusText = '';
for (let i = 0; i < 15; i++) {
  await page.waitForTimeout(2000);
  statusText = await page.evaluate(() => document.querySelector('[role="status"]')?.innerText || '');
  if (statusText.includes('Pre-processing') || statusText.includes('Waiting')) break;
}

// 2. Cut the network
await page.context().setOffline(true);

// 3. Observe UI for ~20 seconds
await page.waitForTimeout(20000);
const statusAfter = await page.evaluate(() => document.querySelector('[role="status"]')?.innerText || 'no status bar');
const chatTail   = await page.evaluate(() => document.body.innerText.slice(-400));

// 4. Restore network
await page.context().setOffline(false);

// 5. Evaluate: was there a clear error message? A retry option? Or silent failure?
```

**Expected pass criteria:** A visible error message in the chat and/or a retry/recovery option. No silent disappearance of the status bar.

#### Approach B — `page.route().abort()` (targeted stream/endpoint abort)
Aborts a specific HTTP request pattern at the browser level before it reaches the server. More surgical than Approach A — use it when you want to kill only the generation stream without affecting all network traffic.

**Important:** Arm the intercept **only after** the normal conversation flow is complete and the bot is at the confirmation stage ("Shall I proceed?"). Arming it earlier will kill the conversational stream calls too.

```javascript
// 1. Complete the full conversation flow with NO intercepts active:
//    upload file → bot confirms settings → bot asks "Shall I proceed?"

// 2. Arm the intercept just before sending the final confirmation
await page.route('**/api/agent/**/stream/**',      route => route.abort('connectionaborted'));
await page.route('**/api/orchestrate/**/stream**', route => route.abort('connectionaborted'));
await page.route('**/api/task/**',                 route => route.abort('connectionaborted'));

// 3. Send the confirmation — the stream POST is immediately killed
await page.getByRole('textbox', { name: 'Type a message' }).fill('Yes');
await page.getByRole('textbox', { name: 'Type a message' }).press('Enter');

// 4. Observe UI for ~8 seconds
await page.waitForTimeout(8000);
const statusBar       = await page.evaluate(() => document.querySelector('[role="status"]')?.innerText || 'no status bar');
const textareaEnabled = await page.evaluate(() => !document.querySelector('textarea')?.disabled);
const chatTail        = await page.evaluate(() => document.body.innerText.slice(-600));

// 5. Remove intercepts to restore normal behaviour
await page.unroute('**/api/agent/**/stream/**');
await page.unroute('**/api/orchestrate/**/stream**');
await page.unroute('**/api/task/**');

// 6. Evaluate: was there a clear error message? A retry option? Or silent failure?
```

**Expected pass criteria:** Error message shown in chat, retry option offered, or explicit "something went wrong" feedback. The user's confirmation message should not disappear silently.

**Known result (as of 2026-07-08):** Both approaches produce a **silent failure** on the Nexus UC — the stream aborts, the status bar/spinner disappears, the textarea re-enables, and no error or retry is shown to the user.

---

## 4. Test Execution Checklist

### Before Starting
- [ ] Django server running: `python manage.py runserver`
- [ ] Workers running: `python manage.py slide_worker` and `python manage.py slide_preworker`
- [ ] Database healthy: No corruption errors
- [ ] Logged in to Nexus chatbot
- [ ] Test pack file accessible (confirm filename and location with Copilot)
- [ ] **Tell Copilot:** which test pack file to use, which sheet, and whether to write results back

### During Testing
- [ ] Share browser page with Copilot
- [ ] Copilot executes one test at a time
- [ ] User validates UI behavior matches expected result
- [ ] Copilot records status and error (if any)
- [ ] Repeat for next test case

### After Testing
- [ ] Ask Copilot to update Status + Actual Result columns in the test pack file
- [ ] Export results summary
- [ ] Fix critical bugs (generation hangs, multi-file UI, language fallback)
- [ ] Re-test affected cases

---

## 5. Key Test Categories

Test categories will vary per test pack. Before running, Copilot reads the test pack and groups tests by the **Module** column (or equivalent) to understand scope.

**Common category types to look for:**
- **Input / Upload** — file type acceptance, multi-file, remove/replace
- **Content type / Format** — summary types, output formats, length variants
- **Audience / Persona** — different target audiences, fallback for unsupported inputs
- **Language** — curated languages, detection from prompt, cross-language sources, unsupported language fallback
- **Conversational Flow** — parameter collection, confirmation, mid-flow changes, decline, context retention
- **Generation** — output matches selections, large/complex documents, regenerate
- **Handoff / Recommendations** — post-generation messages, links, dismissal, content preservation
- **Error & Edge Cases** — empty/huge prompts, injection/XSS, rapid requests, session refresh, network drop

Copilot identifies the categories present in the loaded test pack and groups execution accordingly.

---

## 6. Session Memory & Continuity

**Current Defects (Blocking):**
1. **Generation Hang Post-Confirmation** — Status loops indefinitely; blocks all summary outputs
2. **Non-Curated Language Fallback** — Bot refuses instead of generating via free LLM
3. **Multi-File UI** — Can't add second file or replace upload

**Test Status Summary (update per UAT session):**
- ✅ [N] passing
- ❌ [N] failing (see defects above)
- ⏭️ [N] not tested (blocked by known issues or required scenarios)

**Ask Copilot:**
```
"What tests are still failing?"
→ Copilot reads session notes and provides current status
```

---

## 7. Tips & Gotchas

### Do's
- ✅ Always share the browser before asking Copilot to interact with it.
- ✅ Use `read_page` to verify state instead of assuming UI updates.
- ✅ Test one persona/language combination per thread.
- ✅ Clear databases (`db.sqlite3`, `checkpoints1.db`) if you see corruption errors.
- ✅ Reference the test pack file by its sheet name or section header (e.g. "Functional Test Cases").
- ✅ Upload files from anywhere on your drive — Copilot can access any file path with read permissions.

### Don'ts
- ❌ Don't assume UI updates without calling `read_page`.
- ❌ Don't test multiple features in one request; split into steps.
- ❌ Don't manually edit the test pack file; ask Copilot to use the appropriate library (`openpyxl` for Excel, `csv` for CSV, `json` for JSON) for batch updates.
- ❌ Don't forget to share the browser page before asking for interactions.
- ❌ Don't test across threads without noting file upload isolation.

### Environment
- **Python:** 3.12.9 in `.venv/`
- **App:** Django 5.x at `http://127.0.0.1:8000/unified_chatbot/`
- **Database:** SQLite (`db.sqlite3`) + LangGraph checkpoints (`checkpoints1.db`)
- **Workers:** `slide_worker`, `slide_preworker` (must be running)
- **Test pack:** Excel (default), CSV, JSON, or plain text — tell Copilot the format, filename, and column/field layout before starting

---

## 8. Sample Commands

### "Run the File Upload test cases"
```
Action: Copilot asks for file name, sheet, and column layout
        Reads FU-* test rows, executes each in browser:
          - FU-01–04: Creates new thread, uses setInputFiles() to upload each file type, verifies filename+type appears in chat
          - FU-09: Uploads multiple files in a single setInputFiles() call, checks all appear in one message block
          - FU-10: Creates new thread, types request without uploading, checks bot responds correctly
          - FU-11: Attaches file → removes via X button (dispatchEvent) → attaches replacement → verifies swap
        On failure: reports Test ID, expected result, actual result, then asks
        "[Test ID] failed — do you want me to continue with the remaining tests?"
        Waits for developer yes/no before proceeding
Returns: Pass/Fail per test + writes to test pack file if user confirmed
```

### "Go through test cases and report failures"
```
Action: Copilot reads test pack, executes each test in browser, records Pass/Fail
Returns: List of failures with error descriptions
```

### "Update test pack with results"
```
Action: Copilot uses the appropriate library (openpyxl / csv / json) to populate
        Status and Actual Result fields
Returns: Updated test pack file saved to disk
```

### "Fix database corruption"
```
Action: Copilot identifies corrupted DBs, deletes, runs migrations
Returns: Fresh database ready to use
```

### "Execute test AU-04 (Adolescents persona)"
```
Action: Copilot navigates chatbot, selects Adolescents audience, requests summary, reports result
Returns: Pass/Fail status + screenshot of hang if applicable
```

---

## 9. Feedback & Iteration

When issues arise:
1. **Describe observed behavior** — "Generation hangs after confirmation"
2. **Provide test ID** — "Happens in AU-04, SG-02, SG-05"
3. **Ask Copilot to diagnose** — Check logs, browser console, backend trace
4. **Request fix or workaround** — Refresh, clear cache, or code change
5. **Retest affected cases** — Validate fix with follow-up test execution

---

**Status:** update per UAT session  
**Blocker:** update per UAT session
