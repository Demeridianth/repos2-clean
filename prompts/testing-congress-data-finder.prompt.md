# Copilot Usage Guide — Congress Data Finder & Abstract Grid Generator Testing

## Overview
This guide documents workflows for using Copilot to perform UAT on the **Congress Data Finder / Abstract Grid Generator** feature of the Nexus application, covering:
- **Landing page** navigation
- **Abstract Grid Generator** — search, filter, view, and download
- **Upload Your Abstracts** — template download, file upload, and validation error handling

> **Note:** This guide is intentionally generic. Test pack filenames, sheet names, column layouts, and app URLs vary per environment — Copilot will always confirm these details before starting.

---

## 1. Pre-Run Questions

**Before running any tests, Copilot MUST ask all of the following — never assume:**

### 1.1 Fresh run or continue?
If previous Actual Result / Status values already exist in the test pack:
> *"I can see existing results in the file. Do you want to start a fresh run (overwrite everything) or continue from where you left off (only re-run tests that are empty or failed)?"*

Never overwrite existing results without explicit confirmation.

### 1.2 Test pack format and file location
Copilot must ask which format the test pack uses:
- **Option 1 (default): Excel** — e.g. `CDF_ABG_Testing_Template.xlsx`. Uses `openpyxl`.
- **Option 2: CSV** — Uses Python's `csv` module.
- **Option 3: JSON** — Uses Python's `json` module.
- **Option 4: Plain text / other** — Copilot asks for the structure and adapts.

If not specified, default to Excel and confirm before proceeding.

Then confirm the file path:
> *"Which file should I use as the test pack? Please provide the full path or filename."*

### 1.3 Sheet and column mapping
> *"Which sheet contains the test cases?"* (e.g. `Functional Test Cases`)

Copilot reads the header row and confirms the column mapping before writing anything:
> *"I found these columns: [list]. Which column is Test ID? Expected Result? Actual Result? Status? Severity? Comments?"*

### 1.4 Write results back?
> *"Should I write Actual Result and Status back to the file as I go, or just report results in chat?"*

### 1.5 App URL and environment
> *"Which environment should I test against?"*
- Local: `http://127.0.0.1:8000`
- Dev/UAT: e.g. `https://corpviivasdevcomedgenai.corp-ease-devtest-rx-us6.appserviceenvironment.net`

The key URLs within the app are:
| Page | URL path |
|---|---|
| Landing page (tiles) | `/abstract_grid/` |
| Abstract Grid Generator (search) | `/abstract-grid/abstract_view_download/` |
| Upload Your Abstracts | `/abstract-grid/bulk_upload_abstracts_posters/` |
| Download template | `/abstract-grid/download-template/` |

### 1.6 Upload test files — provide or generate?
Several test cases (UA-04 through UA-12) require specific test files with invalid content. Copilot must ask upfront:
> *"Tests UA-04 to UA-12 need test files — wrong file type (.csv, .pdf), missing columns, extra columns, empty mandatory fields, duplicate IDs, and an empty file. Do you want to:*
> *(a) Provide your own files — tell me the paths and I'll use them, or*
> *(b) Have me generate synthetic test files automatically?"*

Ask this **once upfront** for the whole run, not case-by-case mid-execution.

**If the user chooses (b) generate**, Copilot creates the following files in `/tmp/` using `openpyxl` and Python:

| File | Used for | Content |
|---|---|---|
| `test_abstracts.csv` | UA-04 | CSV version of abstract data |
| `test.pdf` | UA-05 | Minimal fake PDF (`%PDF-1.4 fake pdf`) |
| `missing_col.xlsx` | UA-06 | Valid columns except `abstract` removed |
| `extra_col.xlsx` | UA-07 | All valid columns plus an extra `notes` column |
| `empty_mandatory.xlsx` | UA-08 | Valid structure, but `title` cell blank on first data row |
| `duplicate_id.xlsx` | UA-09 | Two rows with identical `id` values |
| `empty_data.xlsx` | UA-10 | Correct headers, zero data rows |
| `valid_abstracts.xlsx` | UA-12 | Fully valid file (used as the "good" half of mixed upload) |

The expected column order for valid abstract `.xlsx` files is:
```
id, title, authors, category, session, Date, Time (GMT), location, sponsor, url,
Assignee(s), Reference Deck, Responsible for Creation, Copyright Requestor,
Conference Week Advisory Boards, Format Needed for Ad Board,
Congress Medical Narrative Deck, abstract, year, page, presentation_type, congress
```

Mandatory columns (must not be blank): `id`, `title`, `authors`, `congress`, `abstract`, `year`, `url`

### 1.7 Valid upload file — happy path test (conditional)
**Only ask this if the test pack contains a test case that uploads a valid, correctly structured abstract file and expects a success response** (e.g. a test whose Expected Result includes "File Uploaded Successfully" or equivalent).

If such a test exists:
> *"One of the tests uploads a valid populated abstract template and expects a success message. Do you have a file ready? If so, what is the full path? If not, I can generate a synthetic one."*

The reference file used during development is `abstract_upload_template_with_url copy.xlsx` in the project root. If unavailable, Copilot generates a valid synthetic `.xlsx` with the correct 22 columns and at least 2 data rows.

If no such test exists in the pack, skip this question entirely.

---

## 2. Failure & Skip Handling

### On test FAIL
1. Record the actual result and mark Status = **Fail**.
2. Report clearly: Test ID, expected result, actual result.
3. Ask: *"[Test ID] failed — do you want me to continue with the remaining tests?"*
4. Wait for explicit yes/no before proceeding.

### On test BLOCKED / N/A
1. Record the reason and mark Status = **Blocked** or **N/A**.
2. Report clearly: Test ID, reason (e.g. "DB has no abstract records; pre-condition not met").
3. Ask: *"[Test ID] was blocked — do you want me to continue, or address the blocker first?"*
4. Wait for an explicit response.

**Do not silently skip tests and carry on.**

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

---

## 3. Browser Interaction Patterns

### 3.1 Sharing the page
Always share the browser page first. Navigate Copilot to the starting URL before running any tests:
```
"Navigate to /abstract_grid/ and share the page"
→ Copilot opens or reuses the browser tab, reads page state, confirms heading
```

### 3.2 Congress Data Finder Landing Page
The landing page (`/abstract_grid/`) shows feature tiles. To verify it loaded correctly:
```javascript
// Check heading and tile
const heading = await page.$eval('h1', el => el.innerText.trim());
const tile = await page.$eval('h2', el => el.innerText.trim());
// Expected: heading = 'CONGRESS DATA FINDER', tile = 'Abstract Grid Generator'
```

### 3.3 Abstract Grid Generator — Search Form
The search form at `/abstract-grid/abstract_view_download/` has:
- `#id_congress` — Congress select dropdown (dynamic, DB-driven)
- `#id_year` — Year select dropdown (dynamic, DB-driven)
- `input[name="title"]` — Title search (comma-separated, OR logic)
- `input[name="author"]` — Author search (comma-separated, OR logic)
- `input[name="view"]` — Search / View button
- `input[name="download"]` — Download Excel button

**Selecting and searching:**
```javascript
await page.selectOption('#id_congress', 'HIV-Glasgow');
await page.selectOption('#id_year', '2024');
await page.fill('input[name="title"]', 'dolutegravir');
await page.click('input[name="view"]');
await page.waitForLoadState('networkidle');
```

**Reading results:**
```javascript
const rowCount = await page.$$eval('#abstracts-table tbody tr', trs => trs.length).catch(() => 0);
const headers  = await page.$$eval('#abstracts-table thead th', ths => ths.map(th => th.innerText.trim()));
```

**Checking empty state (no results):**
```javascript
// When the queryset is empty, {% if abstracts %} = False in the template
// The table does not render at all — check that #abstracts-table is absent
const tablePresent = await page.$('#abstracts-table').catch(() => null);
// tablePresent === null means no results (correct behaviour)
```

**Expanding truncated summary / abstract:**
```javascript
// Summary and abstract cells have .short-text (truncated) and .long-text (full)
// Clicking the cell toggles them
await page.click('#abstracts-table tbody tr:first-child td:nth-child(3)');
await page.waitForTimeout(400);
const expanded = await page.$eval(
  '#abstracts-table tbody tr:first-child td:nth-child(3) .long-text',
  el => !el.classList.contains('d-none')
);
```

**Checking URL links:**
```javascript
const urlHref   = await page.$eval('#abstracts-table tbody tr:first-child td:nth-child(6) a', el => el.href).catch(() => null);
const urlTarget = await page.$eval('#abstracts-table tbody tr:first-child td:nth-child(6) a', el => el.target).catch(() => null);
// Expected: urlTarget === '_blank'
```

**Download — verifying without capturing the file:**
The Download button submits a POST that triggers a file download. Playwright records this as `net::ERR_ABORTED` (the browser aborted the navigation to handle the download). This is **normal and expected**. Verify by:
1. Checking no warning alert appeared after the click.
2. Confirming the page did not navigate away or show an error.
```javascript
await page.click('input[name="download"]');
await page.waitForLoadState('networkidle').catch(() => {}); // ERR_ABORTED is expected
const warning = await page.$('.alert').catch(() => null);
// warning === null → download triggered successfully, no error
```

### 3.4 Upload Your Abstracts — File Upload
The upload page (`/abstract-grid/bulk_upload_abstracts_posters/`) has:
- A **hidden** file input: `#id_files` (`accept=".xlsx"`, `multiple`)
- A **hidden type field**: `#id_type` (set to `"abstract"` for abstract uploads)
- The form id: `file_form`

**Critical:** The JavaScript on this page auto-submits the form on the `change` event of `#id_files`. So `page.setInputFiles` triggers form submission automatically — you do **not** need to click the Upload button separately.

**Correct upload pattern:**
```javascript
// 1. Set the hidden type field
await page.evaluate(() => { document.getElementById('id_type').value = 'abstract'; });

// 2. Set the file(s) — this fires the change event → form auto-submits
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle' }),
  page.setInputFiles('#id_files', '/absolute/path/to/file.xlsx')
]);

// 3. Read the result
const alert   = await page.$eval('.alert', el => el.innerText.trim()).catch(() => 'no alert');
const heading = await page.$eval('h1', el => el.innerText.trim()).catch(() => '');
```

**Wrong pattern (do not use):**
```javascript
// ❌ setInputFiles then click Upload — the change event already submitted the form
//    by the time you try to click; the second submit can cause double-post or timeout
await page.setInputFiles('#id_files', '/path/to/file.xlsx');
await page.click('button:has-text("Upload")'); // wrong
```

**Uploading multiple files at once (UA-12):**
```javascript
await page.evaluate(() => { document.getElementById('id_type').value = 'abstract'; });
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle' }),
  page.setInputFiles('#id_files', ['/tmp/valid_abstracts.xlsx', '/tmp/test_abstracts.csv'])
]);
```

**Expected response messages:**
| Scenario | Message shown |
|---|---|
| Valid file uploaded | `"File Uploaded Successfully — Thank you for submission!..."` (green banner) |
| Wrong file type | `"File <name> is wrong type and will be ignored."` (warning) |
| Wrong columns | `"File <name> has the wrong columns and will be ignored. You are missing/have extra columns: ..."` |
| Empty mandatory field | `"File <name> has errors and will be ignored. Missing Value for Row N, Column 'X'"` |
| Duplicate id | `"MAJOR ERROR. There are rows with duplicate Unique Identifiers in 'id' column. ids:..."` |
| Empty file | `"The uploaded file is empty. Please upload a valid Excel file with data."` |

**Note on mixed batch uploads (UA-12):** When a batch contains both valid and invalid files, a warning is shown for the invalid file(s) but **no success banner is shown** even for the valid file — because the server suppresses the success message whenever `error_abstract` is non-empty. The valid file is still ingested. This is a known UX limitation.

### 3.5 Known Issues to Be Aware Of

| Issue | Description |
|---|---|
| **JS console error on upload page** | `init_congress_data_finder.js:50` — `document.getElementById('closemodal')` returns `null` on the upload page. The `closemodal` modal element does not exist on `abstract_poster_upload.html`. Drag-drop listeners (lines 26–30) are unaffected; they execute before the crash. |
| **No "No results found" message** | When a search returns zero results, the results table is hidden entirely (`{% if abstracts %}` guard). No explicit "no results" message is shown. Consider this when testing ABG-11. |
| **Download via POST captured as ERR_ABORTED** | Playwright's `waitForEvent('download')` does not reliably capture downloads triggered by form POST with `target` page. Use the presence/absence of a warning alert to determine success instead. |
| **Legacy Abstract Grid Generator not routed** | The `abstract_grid_list` view exists in `views.py` but has no `path()` entry in `viiv/urls.py`. The legacy page is inaccessible — mark related tests as Blocked. |
| **Row index in error messages is 0-based** | `df.iterrows()` is 0-indexed, so the first data row is reported as "Row 1" (not "Row 2"). This is expected. |

---

## 4. Test Data Dependencies

### 4.1 Database must contain abstract records for ABG-04 to ABG-17
Tests that search and filter (ABG-04 through ABG-17) require abstract records to exist in the database. If the dropdowns on the search form show only placeholder values ("Please select a congress" / "Please select a year"), the database is empty.

**Resolution:** Run UA-03 first (upload valid abstract data), then return to the ABG tests. Alternatively, ask: *"Should I skip ahead to the upload tests to populate the database first?"*

### 4.2 Congress/year combinations for testing
Suggested values (from reference dataset):
| Congress | Year | Expected rows |
|---|---|---|
| HIV-Glasgow | 2024 | 6 |
| CROI | 2024 | depends on data |

For ABG-17 (no pre-built grid warning), choose a congress/year combination not present in the database (e.g. IDWeek 2016).

---

## 5. Writing Results Back

When writing results back to an Excel test pack, Copilot:
1. Reads the header row to confirm column mapping (never assumes position).
2. For each completed test, writes:
   - **Actual Result** (column H by default): description of what happened
   - **Status** (column I): `Pass`, `Fail`, `Blocked`, or `N/A`
   - **Severity** (column J): `Critical`, `High`, `Medium`, `Low` — only for Fail
   - **Comments** (column K): notes on bugs, deviations, or UX observations
3. Applies colour coding: green (Pass), red (Fail), amber (Blocked), grey (N/A).
4. Asks before overwriting any existing non-empty result.

**Status legend:**
| Status | Meaning |
|---|---|
| Pass | Behaviour matches expected result exactly |
| Fail | Does not meet expected result (record severity) |
| Blocked | Could not test — dependency or environment issue |
| N/A | Pre-condition not met or not applicable to this run |

---

## 6. Example Workflow

```
User: "Run all CDF/ABG test cases from CDF_ABG_Testing_Template.xlsx"

→ Copilot asks:
  1. Fresh run or continue from previous results?
  2. Which file and sheet?
  3. Which columns map to Test ID, Expected, Actual, Status, Severity, Comments?
  4. Write results back to the file?
  5. Which environment (URL)?
  6. For UA-04–UA-12: provide your own test files or should I generate them?
  7. For UA-03: do you have the populated abstract template, or should I generate one?

→ Copilot confirms answers, generates any needed files, navigates to /abstract_grid/
→ Runs CDF-01: checks heading, tile, Begin button → Pass
→ Runs CDF-02: clicks Begin, checks navigation → Pass
→ Runs CDF-04: marks Blocked (cannot test auth without ending session), asks to continue
→ Runs ABG-01 through ABG-17...
→ Runs UA-01 through UA-12...
→ Runs AGG-01 through AGG-03: marks Blocked (no URL route), asks to continue
→ Writes all results to file with colour coding
→ Reports final summary: N Pass, N Fail, N Blocked, N N/A
```

---

## 7. Debugging

### App not responding / 500 errors
If a POST to the upload endpoint returns a 500 error:
- Check Django debug output for the exception type and location
- Common cause: `viiv/helpers.py handle_uploaded_file` — file opened in wrong mode (`'w'` instead of `'wb'`)
- To inspect: `await page.title()` and `await page.innerText('body')` to read the Django debug page

### Empty dropdowns
If Congress/Year dropdowns show only placeholder options:
- Database has no `AbstractNew` records
- Run UA-03 (upload valid abstract file) first, then re-run ABG-02 onwards

### Upload page JS crash (line 50)
`TypeError: Cannot read properties of null (reading 'addEventListener')` on every page load — safe to ignore. Does not affect form submission or drag-drop.
