---
applyTo: "**"
---

# Copilot Orchestrator — Full Nexus Test Suite

Run all six Nexus feature test packs in sequence, converting JSON test cases to Excel, executing each feature's tests, and writing results back.

---

## Overview

This skill orchestrates a complete end-to-end UAT run across every Nexus feature.  
For each feature it:
1. Reads the **JSON test case file** from `copilot_test_cases/`
2. Converts it to a fresh **Excel workbook** (overwriting any previous run)
3. Executes every test case using the rules from that feature's **individual skill file**
4. Writes Actual Result, Status, Severity, and Comments back to the Excel workbook
5. Reports a summary before moving to the next feature

The six features run in this fixed order:

| # | Feature | JSON file | Individual skill |
|---|---|---|---|
| 1 | Congress Data Finder / ABG | `test_cases/CDF_ABG_Testing_Template.json` | `.github/prompts/testing-congress-data-finder.prompt.md` |
| 2 | Summary Slides Maker | `test_cases/SSM_Testing_Template.json` | `.github/prompts/testing-summary-slides-maker.prompt.md` |
| 3 | Narrative Speaker Drafter | `test_cases/NSD_Testing_Template.json` | `.github/prompts/testing-narrative-speaker-drafter.prompt.md` |
| 4 | Plain Language Writer | `test_cases/PLW_Testing_Template.json` | `.github/prompts/testing-plain-language-writer.prompt.md` |
| 5 | Speech Writer | `test_cases/SW_Testing_Template.json` | `.github/prompts/testing-speech-writer.prompt.md` |
| 6 | Unified Chatbot | `test_cases/UC Testing_Template.json` | `.github/prompts/testing-unified-chat-bot.prompt.md` |

> Voice Creator (`VC_Testing_Template.json`) has its own session-expiry risk profile and is intentionally excluded from this orchestrated run. Run it separately using `voice-creator-testing.prompt.md`.

---

## Step 0 — Pre-run setup (ask once, before anything else)

Ask the user all of the following before starting:

### 0.1 App URL
> *"Which environment should I test against? (e.g. `https://corpviivasdevcomedgenai.corp-ease-devtest-rx-us6.appserviceenvironment.net`)"*

Store as `BASE_URL`. All relative paths below are appended to it.

### 0.2 Browser page
> *"Please share the browser page with me using the browser attachment tool, logged in to the app."*

Confirm the session is active before starting (check that the current URL is within `BASE_URL`, not `login.microsoftonline.com`).

### 0.3 Source / upload files
> *"Several tests need source files to upload (PDFs, DOCX, PPTX, images). Should I generate synthetic ones in `/tmp/`, or will you provide them?"*

If generating, create all required files now in a single batch **before starting any tests** — do not create files mid-run. See each feature's individual skill file for the exact files needed.

### 0.4 Fresh run or continue?
If Excel workbooks already exist in `test_cases/` with previous results:
> *"I can see existing results in the Excel files. Do you want to:*
> *(a) **Fresh run** — rebuild all workbooks from JSON (overwrites every Actual Result and Status), or*
> *(b) **Continue** — keep existing results and only re-run tests whose Status is empty, N/A, or Fail?"*

Never overwrite existing results without explicit confirmation. Store the answer as `RUN_MODE` (`fresh` or `continue`) — it controls Step 1.

### 0.5 Confirm feature scope
> *"I'll run features 1–6 in order (CDF/ABG → SSM → NSD → PLW → SW → UC). Do you want to skip any feature, or start from a specific one?"*

---

## Step 1 — Prepare Excel workbooks

**If `RUN_MODE = fresh`:** Rebuild a clean Excel workbook from the JSON source before that feature's tests start. This overwrites all previous Actual Result and Status values.

**If `RUN_MODE = continue`:** Skip the rebuild. Open the existing Excel workbook and read current Status values. Only execute test cases where Status is empty, `N/A`, or `Fail` — skip rows that already have `Pass` or `Blocked`.

Run the appropriate branch once per feature, immediately before that feature's tests start.

```python
import json
import openpyxl
from openpyxl.styles import PatternFill, Font
from pathlib import Path

FILLS = {
    'Pass':    PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
    'Fail':    PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
    'N/A':     PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid'),
    'Blocked': PatternFill(start_color='BDD7EE', end_color='BDD7EE', fill_type='solid'),
}

def json_to_xlsx(json_path: str, xlsx_path: str):
    data = json.loads(Path(json_path).read_text(encoding='utf-8'))
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    RESULT_COLS = {'Actual Result', 'Status', 'Severity', 'Comments'}

    for sheet_name, content in data.items():
        ws = wb.create_sheet(title=sheet_name)
        headers = content['headers']
        ws.append(headers)

        # Bold header row
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for record in content['rows']:
            # Strip result columns so the workbook is a genuine clean slate
            row = [None if h in RESULT_COLS else record.get(h) for h in headers]
            ws.append(row)

    wb.save(xlsx_path)
    print(f"Created {xlsx_path}")

def get_tests_to_run(xlsx_path: str, sheet: str = 'Functional Test Cases') -> set[str]:
    """Return Test IDs that should be re-run (Status is empty, N/A, or Fail)."""
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb[sheet]
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    col = {h: i + 1 for i, h in enumerate(headers) if h}
    rerun = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        tid = row[col.get('Test ID', 1) - 1]
        status = row[col.get('Status', 9) - 1]
        if tid and str(tid).count('-') == 1:  # actual test row (not section header)
            if not status or status in ('N/A', 'Fail'):
                rerun.add(str(tid))
    return rerun

# Usage:
# if RUN_MODE == 'fresh':
#     json_to_xlsx(json_path, xlsx_path)
#     tests_to_run = None  # run all
# else:
#     tests_to_run = get_tests_to_run(xlsx_path)  # skip existing Pass/Blocked
```

---

## Step 2 — Write results back to Excel

After each test case completes, call this helper to update the row in the active workbook:

```python
def write_result(ws, test_id: str, actual: str, status: str, severity: str = None, comments: str = None):
    """Find the row with the given Test ID and write result columns.
    In continue mode, call this only for tests in the tests_to_run set."""
    FILLS = {
        'Pass':    PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
        'Fail':    PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
        'N/A':     PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid'),
        'Blocked': PatternFill(start_color='BDD7EE', end_color='BDD7EE', fill_type='solid'),
    }
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    col = {h: i + 1 for i, h in enumerate(headers) if h}

    for row in ws.iter_rows(min_row=2):
        if str(row[col.get('Test ID', 1) - 1].value) == test_id:
            if 'Actual Result' in col:
                ws.cell(row[0].row, col['Actual Result']).value = actual
            if 'Status' in col:
                cell = ws.cell(row[0].row, col['Status'])
                cell.value = status
                if status in FILLS:
                    cell.fill = FILLS[status]
            if severity and 'Severity' in col:
                ws.cell(row[0].row, col['Severity']).value = severity
            if comments and 'Comments' in col:
                ws.cell(row[0].row, col['Comments']).value = comments
            return
```

Save the workbook after every test case (not just at the end of each feature) so results are never lost to a crash or session expiry.

---

## Step 3 — Session expiry handling (applies to ALL features)

Session expiry can happen at any point. Check after **every** navigation:

```javascript
const checkSession = (testId) => {
  if (page.url().includes('login.microsoftonline.com')) {
    throw new Error(`SESSION_EXPIRED:${testId}`);
  }
};
```

Wrap each feature's entire test loop in a try/catch:

```javascript
try {
  // ... run all tests for this feature ...
} catch (err) {
  if (err.message.startsWith('SESSION_EXPIRED:')) {
    const interrupted = err.message.split(':')[1];
    // 1. Mark the interrupted test as N/A in the Excel file
    // 2. Save the workbook
    // 3. Stop the run
    return {
      sessionExpired: true,
      feature: currentFeature,
      interruptedTest: interrupted,
      message: `⚠️ Session expired during ${interrupted} (${currentFeature}). All results up to this point have been saved. Please log back in, then tell me to resume from ${interrupted}.`
    };
  }
  throw err;
}
```

When session expiry is caught:
1. **Stop immediately** — do not attempt any further tests for this feature or subsequent features.
2. Write N/A + reason `"Session expired mid-execution; re-run required"` for the interrupted test.
3. Save the workbook.
4. Report to the user:
   > *"⚠️ Session expired during **[Test ID]** (feature: **[Feature Name]**).*
   > *All results up to that point have been saved to `test_cases/[filename].xlsx`.*
   > *Please log back in, then tell me to resume and I will restart from **[Test ID]**."*
5. Wait for explicit confirmation before doing anything else.
6. On resume: re-run only the interrupted test from the beginning, then continue with any remaining tests in that feature, then continue to the next feature.

---

## Step 4 — Feature execution rules

For each feature, read and apply **all rules** from its individual skill file before running any tests. The individual skill files define:
- Exact UI selectors, button names, and form interactions
- File upload patterns and accepted/rejected MIME types
- Generation trigger mechanisms and polling behaviour
- Download patterns (auto-download, ZIP, individual file)
- What constitutes Pass / Fail / N/A / Blocked for each test case
- Any known bugs or workarounds

**Do not rely on memory or assumptions — re-read the relevant skill file at the start of each feature.**

### Feature 1: Congress Data Finder / ABG
- Skill: `.github/prompts/testing-congress-data-finder.prompt.md`
- JSON: `test_cases/CDF_ABG_Testing_Template.json`
- Excel output: `test_cases/CDF_ABG_Testing_Template.xlsx`
- Test sheet: `Functional Test Cases`

### Feature 2: Summary Slides Maker
- Skill: `.github/prompts/testing-summary-slides-maker.prompt.md`
- JSON: `test_cases/SSM_Testing_Template.json`
- Excel output: `test_cases/SSM_Testing_Template.xlsx`
- Test sheet: `Functional Test Cases`

### Feature 3: Narrative Speaker Drafter
- Skill: `.github/prompts/testing-narrative-speaker-drafter.prompt.md`
- JSON: `test_cases/NSD_Testing_Template.json`
- Excel output: `test_cases/NSD_Testing_Template.xlsx`
- Test sheet: `Functional Test Cases`

### Feature 4: Plain Language Writer
- Skill: `.github/prompts/testing-plain-language-writer.prompt.md`
- JSON: `test_cases/PLW_Testing_Template.json`
- Excel output: `test_cases/PLW_Testing_Template.xlsx`
- Test sheet: `Functional Test Cases`

### Feature 5: Speech Writer
- Skill: `.github/prompts/testing-speech-writer.prompt.md`
- JSON: `test_cases/SW_Testing_Template.json`
- Excel output: `test_cases/SW_Testing_Template.xlsx`
- Test sheet: `Functional Test Cases`

### Feature 6: Unified Chatbot
- Skill: `.github/prompts/testing-unified-chat-bot.prompt.md`
- JSON: `test_cases/UC Testing_Template.json`
- Excel output: `test_cases/UC Testing_Template.xlsx`
- Test sheet: `Functional Test Cases`

---

## Step 5 — Between-feature summary

After completing each feature (or stopping due to session expiry), print a summary before moving on:

```
✅ Feature [N] complete: [Feature Name]
   Pass: X  |  Fail: Y  |  N/A: Z  |  Blocked: W
   Excel saved: test_cases/[filename].xlsx
```

If any Fail results were recorded, list the failing Test IDs and ask:
> *"Feature [N] had [Y] failures: [list of IDs]. Do you want to investigate before continuing to Feature [N+1], or shall I proceed?"*

Wait for explicit confirmation before starting the next feature.

---

## Step 6 — Final summary

After all features complete, print an overall table:

```
══════════════════════════════════════════════════════
 NEXUS FULL TEST RUN — SUMMARY
══════════════════════════════════════════════════════
 Feature                  Pass  Fail  N/A  Blocked
 ─────────────────────────────────────────────────
 1. CDF/ABG               XX    X     X    X
 2. Summary Slides Maker  XX    X     X    X
 3. Narrative Speaker      XX    X     X    X
 4. Plain Language Writer  XX    X     X    X
 5. Speech Writer          XX    X     X    X
 6. Unified Chatbot        XX    X     X    X
 ─────────────────────────────────────────────────
 TOTAL                    XX    X     X    X
══════════════════════════════════════════════════════
```

List all Fail and Blocked results with their Test IDs and a one-line description of the actual result.
