# Copilot Usage Guide — Summary Slides Maker (SSM) Testing

## Overview
This guide documents workflows for using Copilot to perform UAT on the **Summary Slides Maker (Classic Slide Maker)** feature of the Nexus application, covering:
- **File type upload compatibility** (PDF, DOCX, PPTX, JPEG, PNG)
- **Summary type generation** (Single page, Multi page, Table, Plain language)
- **Audience preference settings** (personas and languages)
- **Persona + translation combinations**
- **Lift & Shift (Slide Converter)**
- **Group uploads (5+ files)**
- **Summary re-generation**
- **Image generation in slides**

> **Note:** This guide is intentionally generic. Test pack filenames, sheet names, and column layouts vary per project — Copilot will always confirm these details before starting.

---

## 1. Pre-Run Questions

**Before running any tests, Copilot MUST ask ALL of the following — never assume:**

### 1.1 Fresh run or continue?
If previous Actual Result / Status values already exist in the test pack:
> *"I can see existing results in the file. Do you want to start a fresh run (overwrite everything) or continue from where you left off (only re-run tests that are empty or failed)?"*

Never overwrite existing results without explicit confirmation.

### 1.2 Test pack format and file location
> *"What format is your test pack, and which file should I use?"*
- **Option 1 (default): Excel** — uses `openpyxl`
- **Option 2: CSV** — uses Python's `csv` module
- **Option 3: JSON** — uses `json` module
- **Option 4: Plain text / other** — Copilot adapts accordingly

Then confirm:
> *"Which sheet contains the test cases? Which columns map to Test ID, Expected Result, Actual Result, Status, Severity, and Comments?"*

Copilot reads the header row and confirms column mapping before writing anything.

### 1.3 Write results back?
> *"Should I write Actual Result and Status back to the file as I go, or just report in chat?"*

### 1.4 App URL and environment
> *"Which environment should I test against?"*

| Page | URL path |
|---|---|
| SSM landing (tile index) | `/slide_index/` |
| Classic Slide Maker | `/slide/` |
| Slides ready / download | `/slide/ready/` |

### 1.5 Source documents — provide or generate?

**Only ask if the test pack contains tests that require uploading source documents** (any test with a source file like PDF, DOCX, PPTX, JPEG, PNG).

Copilot scans the test pack for file-type tests upfront and asks **once**:
> *"Some tests require source documents to upload. These file types are needed: [list from test pack]. Do you want to:*
> *(a) Provide your own files — tell me the paths and I'll use them, or*
> *(b) Have me generate synthetic test files automatically?"*

**If the user provides files**, ask for each path individually:
> - *"What is the full path to your test PDF file?"*
> - *"Full path to your DOCX file?"*
> - *"Full path to your PPTX file?"*
> - *"Full path to your JPEG file?"*
> - *"Full path to your PNG file?"*

**Always use absolute paths** — never `~` (not expanded by Playwright).

**If the user chooses generate**, Copilot creates minimal synthetic files in `/tmp/`:
```python
# PDF — minimal valid PDF
with open('/tmp/test_upload.pdf', 'wb') as f:
    f.write(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n%%EOF')

# DOCX — use python-docx
from docx import Document
doc = Document(); doc.add_paragraph('Test medical abstract content.')
doc.save('/tmp/test_upload.docx')

# PPTX — use python-pptx
from pptx import Presentation
prs = Presentation(); slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = 'Test Slide'
prs.save('/tmp/test_upload.pptx')

# JPEG / PNG — use Pillow
from PIL import Image
img = Image.new('RGB', (800, 600), color=(73, 109, 137))
img.save('/tmp/test_upload.jpg')
img.save('/tmp/test_upload.png')
```

> **Important:** Synthetic files will be de-duplicated by the server (`unique_only = True`). If a file with the same MD5 hash was previously uploaded, the server reuses the existing DB record. This means "brand new file" tests (preworker path) cannot be validated with previously-uploaded content. Note this in the Actual Result column.

---

## 2. Failure, Skip & Session Handling

### On test FAIL
1. Record the actual result and mark Status = **Fail**.
2. Report clearly: Test ID, expected result, actual result.
3. Ask: *"[Test ID] failed — do you want me to continue with the remaining tests?"*
4. Wait for an explicit yes/no. Only continue if confirmed.

### On test BLOCKED / N/A
1. Record the reason and mark Status = **Blocked** or **N/A**.
2. Report clearly: Test ID and reason.
3. Ask: *"[Test ID] was blocked — continue or address the blocker first?"*
4. Wait for an explicit response.

### 🔴 Session expiry (app logout)
**This is a high-risk event during SSM testing.** The session can expire mid-run (especially during long generation waits or multi-step sequences).

**Copilot detects session expiry by checking after every navigation:**
- Page URL changes to `https://login.microsoftonline.com/...` (Microsoft SSO redirect)
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

## 3. Page and UI Reference

### 3.1 Upload mechanism (Step 1)
The main file input:
- Selector: `#id_files`
- Accept: `.pdf,.pptx,.jpg,.jpeg,.png,.doc,.docx`
- Multiple: true
- **Auto-submits on `change` event** — `setInputFiles` triggers navigation automatically. Do NOT click the Upload button after `setInputFiles`.

```javascript
// Correct: setInputFiles + waitForNavigation together
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }),
  page.setInputFiles('#id_files', '/absolute/path/to/file.pdf')
]);

// Wrong: setInputFiles then separate click — causes double-submit
await page.setInputFiles('#id_files', '/path/to/file.pdf');
await page.click('button:has-text("Upload")'); // ❌
```

**Multiple files at once (group upload):**
```javascript
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }),
  page.setInputFiles('#id_files', ['/path/file1.pdf', '/path/file2.docx', '/path/file3.pptx'])
]);
```

**Slide Converter (Lift & Shift) — separate input:**
```javascript
// Uses a different input: #id_files_lift (accept=".pptx" only, single file)
await page.setInputFiles('#id_files_lift', '/path/to/presentation.pptx');
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }),
  page.click('input[type="image"][name="lift"]')
]);
```

### 3.2 Files table (Step 2)
After upload, files appear in a table at Step 2. Each row contains:
| Column | Description |
|---|---|
| Id | Internal DB ID |
| File name | Truncated name (hover for full Azure Blob URL) |
| Summary | Dropdown: `value=1` One page, `value=5` Multi page, `value=10` Plain language, `value=55` Table summary |
| Add to Table | Dropdown: Select / Table 1–15 (for grouping in Table summary) |
| Date | Upload timestamp + uploader email |
| Processed | None / error message |
| Delete | `input[type="image"][name="delete"]` — removes the row |

**Summary type is `instant-edit`** — changing the dropdown auto-POSTs to `/slide/output/{id}/edit/` and reloads the page. Handle with:
```javascript
const sels = await page.$$('table tbody tr select[name="type"]');
// Re-query after EACH navigation — handles stale DOM refs
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 }),
  sels[i].selectOption('5') // '5' = Multi page
]);
```

**Clear all files:**
```javascript
await page.click('button[name="reset"]');
await page.waitForLoadState('networkidle');
```

### 3.3 Audience preferences
The audience preferences form (persona + language) must be submitted **before** generation is possible. The generate button is disabled until at least one virtual slide exists.

**Audience form submit button:** `input[type="image"][name="add"]` (not a `<button>`)

```javascript
await page.selectOption('select[name="persona"]', '1'); // '1' = HIV Specialists
await page.selectOption('select[name="lang"]', '');     // '' = No Translation Required
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 }),
  page.click('input[type="image"][name="add"]')
]);
```

**Persona values:**

| Value | Label |
|---|---|
| 1 | HIV Specialists |
| 2 | Non-HIV Specialists |
| 3 | Educated Adult |
| 4 | Adolescents |
| 5 | General Public |
| 6 | Healthcare Provider (HCP) |
| 7 | Direct to consumer - Patient |
| 8 | Healthcare organization (HCO) |
| 9 | Government or Policy Maker |

**Language values:** `''` No Translation, `'en'` English, `'fr'` French, `'es'` Spanish, `'de'` German, `'it'` Italian, `'ja'` Japanese

**Multiple personas:** Each call to the add button creates a NEW virtual slide. Call it multiple times to add multiple persona/language combinations.

### 3.4 Generate button
After at least one persona is set, the generate button becomes enabled:
```javascript
// Generate button is input[type="image"][name="generate"]
const genBtn = await page.$('input[type="image"][name="generate"]');
if (!genBtn) throw new Error('Generate button not found — audience preferences may not be set');

await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }),
  page.click('input[type="image"][name="generate"]')
]);
```

After clicking generate, the page typically returns to `/slide/`. Navigate to `/slide/ready/` to check the result.

### 3.5 Slides ready / download page
```javascript
await page.goto(baseUrl + '/slide/ready/');
await page.waitForLoadState('networkidle');

const heading = await page.$eval('h1', el => el.innerText.trim()).catch(() => '');
const hasDownload = !!(await page.$('input[name="download"]'));

// heading = 'Your slides are ready to download' + hasDownload = true → PASS
// Redirect to /slide/ with warning → slides not ready yet (processing still in progress)
```

**Download:**
```javascript
await page.click('input[name="download"]').catch(() => {});
await page.waitForLoadState('networkidle').catch(() => {});
// ERR_ABORTED on the download URL = expected (browser handles file download)
```

**Restart (regenerate):** `input[name="back"]`

---

## 4. Known Issues

| Issue | Severity | Description |
|---|---|---|
| `init.js` returns 500 on page load | Medium | `/static/js/init.js` returns HTTP 500 on every page load, causing `window.spinner.show is not a function` at `init_slides.js:22`. The upload spinner animation doesn't appear during file upload, but the upload itself succeeds. No user-facing error message. |
| `unique_only = True` de-duplication | Info | `SlideUploadForm` hashes uploaded files (MD5). If a file with the same hash was previously uploaded by ANY user, the server returns the existing DB record. The file appears in the queue under its original filename — which may differ from the uploaded filename. This is intentional design, but means "brand new file" tests cannot be validated if those files already exist in the DB. |
| Session expiry during long runs | High | Microsoft SSO sessions expire during testing. No warning is shown in-app. Copilot detects this via URL change to `login.microsoftonline.com`. See Section 2 for handling. |
| Multiple file upload JS error | Low | When uploading 5+ files simultaneously, `window.spinner.show is not a function` fires. Upload completes correctly. |

---

## 5. Test Execution Patterns

### 5.1 Single file upload + single summary type
```javascript
// 1. Upload file
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }),
  page.setInputFiles('#id_files', '/absolute/path/to/file.pdf')
]);

// 2. Verify no errors, file in queue
const alerts = await page.$$eval('.alert', els => els.map(e => e.innerText.trim())).catch(() => []);
const queueRows = await page.$$eval('table tbody tr', trs =>
  trs.filter(tr => tr.querySelectorAll('td').length > 1).map(tr => {
    const tds = tr.querySelectorAll('td');
    return { id: tds[0]?.innerText.trim(), file: tds[1]?.innerText.trim(), processed: tds[5]?.innerText.trim() };
  })
).catch(() => []);

// 3. Set audience pref
await page.selectOption('select[name="persona"]', '1');
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 }),
  page.click('input[type="image"][name="add"]')
]);

// 4. Generate
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }),
  page.click('input[type="image"][name="generate"]')
]);

// 5. Check ready
await page.goto(baseUrl + '/slide/ready/');
await page.waitForLoadState('networkidle');
const heading = await page.$eval('h1', el => el.innerText.trim()).catch(() => '');
const hasDownload = !!(await page.$('input[name="download"]'));
```

### 5.2 Changing summary type (instant-edit)
```javascript
// MUST re-query selects after EACH navigation — old refs become stale
for (let i = 0; i < rowCount; i++) {
  const sels = await page.$$('table tbody tr select[name="type"]');
  const curVal = await sels[i].evaluate(el => el.value);
  if (curVal !== targetVal) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 }),
      sels[i].selectOption(targetVal)
    ]);
  }
}
```

### 5.3 Multiple personas / languages
```javascript
const personas = [
  { persona: '1', lang: '' },         // HIV Specialists, No translation
  { persona: '2', lang: '' },         // Non-HIV Specialists
  { persona: '1', lang: 'fr' },       // HIV Specialists + French
];
for (const pref of personas) {
  await page.selectOption('select[name="persona"]', pref.persona);
  await page.selectOption('select[name="lang"]', pref.lang);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 }),
    page.click('input[type="image"][name="add"]')
  ]);
}
```

### 5.4 Detecting session expiry
```javascript
// Check after every navigation
const isLoggedOut = page.url().includes('login.microsoftonline.com') ||
                    (await page.title()).toLowerCase().includes('sign in');
if (isLoggedOut) {
  // STOP and inform the user
  throw new Error('SESSION_EXPIRED');
}
```

Add this check after each `waitForNavigation` call. If `SESSION_EXPIRED` is thrown, Copilot stops the run and reports to the user as described in Section 2.

---

## 6. Output Verification

Many SSM tests require verifying the **content** of generated slides — image presence, captions, translation quality, layout. These cannot be automated and must be performed manually.

**Mark the following as "Manual check required":**
- Image presence in slides (single, multi, PLS summary types)
- Image caption text and relevance
- Translated caption accuracy (French, Spanish, etc.)
- Slide layout correctness
- Summary content quality (factual accuracy)

**Automatable checks:**
- ✅ File uploads without error (no `.alert` with error text)
- ✅ File appears in queue (row count > 0 in table)
- ✅ Summary type dropdown works (instant-edit saves)
- ✅ Audience preference can be set (add button submits)
- ✅ Generate button becomes enabled after preferences set
- ✅ `/slide/ready/` shows "Your slides are ready to download"
- ✅ Download triggered (no error, `ERR_ABORTED` = expected)

---

## 7. Writing Results Back

When writing to an Excel test pack, Copilot:
1. Reads and confirms column mapping from the header row (never assumes position).
2. For each completed test writes:
   - **Actual Result** (col H by default): what actually happened
   - **Status**: `Pass`, `Fail`, `Blocked`, `N/A`, or `Manual check required`
   - **Severity** (col J): `Critical` / `High` / `Medium` / `Low` — only for Fail
   - **Comments** (col K): bugs, de-dup notes, JS console errors, workarounds
3. Applies colour coding: green (Pass), red (Fail), amber (Blocked), grey (N/A/Manual).
4. Asks before overwriting any existing non-empty result.

**Status legend:**
| Status | Meaning |
|---|---|
| Pass | Behaviour matches expected result |
| Fail | Does not meet expected result (record severity) |
| Blocked | Cannot test — dependency or environment issue |
| N/A | Pre-condition not met or not applicable |
| Manual check required | Automated verification not possible; human review needed |

---

## 8. Example Workflow

```
User: "Run SSM test cases from test_cases/SSM_test_cases.xlsx"

→ Copilot asks:
  1. Fresh run or continue?
  2. Which sheet? Which columns map to Test ID, Actual Result, Status?
  3. Write results back to file?
  4. Which environment URL?
  5. Tests need PDF, DOCX, PPTX, JPEG, PNG — provide or generate?
     If provide: ask for each absolute file path individually.

→ Copilot confirms answers, navigates to /slide/

→ Runs file upload tests:
  - setInputFiles with each file type
  - Verifies file appears in queue, no errors
  - Notes if unique_only de-duplication occurs

→ Runs summary type tests:
  - Changes instant-edit dropdown, re-queries after each navigation
  - Sets audience preference, triggers generate
  - Checks /slide/ready/

→ On session expiry: STOPS immediately
  → Reports: "⚠️ Session expired — please log back in. I'll resume from [Test ID]."

→ On failure: reports Test ID + expected vs actual, then asks:
  "Do you want me to continue with the remaining tests?"

→ Marks image generation tests as "Manual check required"

→ Writes all results to file with colour coding

→ Reports final summary: N Pass, N Fail, N Manual check required
```

---

## 9. Debugging

### Slides not appearing in /slide/ready/
- Processing is async (worker). Navigate to `/slide/ready/` — if the worker hasn't finished, it shows a message or redirects to `/slide/`.
- Check `/slide/` queue: `Processed` column may show an error message if the worker failed.

### Generate button still disabled after setting audience
- At least one virtual `PDFObject` (persona/lang combination) must exist. The `add` button creates these.
- If no virtual slides exist: `"Please set at least one language/persona preference before generating."` warning appears.

### `init.js` 500 error / spinner crash
- The `window.spinner.show is not a function` error is a known bug. Upload still succeeds. Do not mark upload tests as Fail due to this error.

### `unique_only` de-duplication
- If the file you upload already exists in the DB (same MD5), the queue shows the ORIGINAL filename (which may differ from yours). This is expected. Note it in the Comments column.
- To test with truly new files, use freshly generated content that has never been uploaded to this server.

### Multiple rapid navigations (stale DOM)
- After each `waitForNavigation`, all previously-queried DOM element references are invalid. Always re-query with `page.$$()` or `page.$()` after navigation.
