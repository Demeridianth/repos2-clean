# Copilot Usage Guide — Plain Language Writer (PLW) Testing

## Overview
This guide documents workflows for using Copilot to perform UAT on the **Plain Language Writer** feature of the Nexus application, covering:
- **File upload** (PDF, PPTX, DOCX, JPEG, PNG — server-side MIME filtering)
- **File management** (delete, Clear All)
- **Audience preferences** (persona + language chips)
- **Generation** (trigger, spinner, automatic polling, auto-download)
- **Download** (ZIP containing .docx per source × preference combination)
- **Error handling** (corrupted files, wrong types, download before ready)

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
- **Option 2: CSV / JSON / plain text** — Copilot adapts

Confirm sheet name and column mapping (Test ID, Expected Result, Actual Result, Status, Severity, Comments) by reading the header row.

### 1.3 Write results back?
> *"Should I write Actual Result and Status back to the file as I go, or just report in chat?"*

### 1.4 App URL and environment
> *"Which environment should I test against?"*

| Page | URL path |
|---|---|
| Plain Language Writer | `/persona/` |
| Readiness check | `/persona/is_ready/` |
| Download ZIP | `/persona/download/` |

### 1.5 Source documents for upload tests — provide or generate?
**Only ask if the test pack contains tests that upload source files.**

> *"Some tests need source documents to upload (PDF, PPTX, DOCX, JPEG, PNG). Do you have them, or should I generate synthetic ones?"*

**If the user provides files**, ask for each path individually:
> - *"Full path to your test PDF?"*
> - *"Full path to your PPTX?"*
> - *"Full path to your DOCX?"*
> - *"Full path to your JPEG?"*
> - *"Full path to your PNG?"*

Always use **absolute paths** — never `~`.

**If generate**, Copilot creates minimal synthetic files in `/tmp/`:
```python
# PDF
with open('/tmp/test_plw.pdf', 'wb') as f: f.write(b'%PDF-1.4 minimal pdf')

# PPTX
from pptx import Presentation
prs = Presentation(); prs.slides.add_slide(prs.slide_layouts[0])
prs.slides[0].shapes.title.text = 'Test PLW Slide'
prs.save('/tmp/test_plw.pptx')

# DOCX
from docx import Document
doc = Document(); doc.add_paragraph('Test plain language content.')
doc.save('/tmp/test_plw.docx')

# JPEG / PNG
from PIL import Image
img = Image.new('RGB', (400, 300), color=(50, 100, 150))
img.save('/tmp/test_plw.jpg'); img.save('/tmp/test_plw.png')
```

### 1.6 Wrong-type files (conditional)
**Only ask if the test pack contains tests for rejected file types (.txt, .csv, etc.):**
> *"Some tests upload files that should be rejected (.txt, .csv). Should I create these automatically in /tmp/?"*

If yes, Copilot creates:
```python
with open('/tmp/test_plw.txt', 'w') as f: f.write('Plain text test content.')
with open('/tmp/test_plw.csv', 'w') as f: f.write('id,title\n1,Test')
```

---

## 2. Failure, Skip & Session Handling

### On test FAIL
1. Record the actual result and mark Status = **Fail**.
2. Report clearly: Test ID, expected result, actual result.
3. Ask: *"[Test ID] failed — do you want me to continue with the remaining tests?"*
4. Wait for an explicit yes/no before proceeding.

### On test BLOCKED / N/A
1. Record the reason and mark Status = **Blocked** or **N/A**.
2. Report clearly: Test ID and reason.
3. Ask: *"[Test ID] was blocked — continue or address the blocker first?"*
4. Wait for an explicit response.

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
5. **On resume:** re-run the interrupted test from the beginning, then continue with remaining tests in order.

**Do NOT:** mark the interrupted test as Fail, skip it, or attempt to continue while the login redirect is active.

---

## 3. Page and UI Reference

### 3.1 File upload
- **File input:** `#id_files`, accept=`.pdf,.pptx,.jpg,.jpeg,.png,.doc,.docx`, multiple
- **Auto-submits immediately on `change` event** — `window.spinner.show()` is called, then `form.submit()`. `window.spinner` **IS defined** on this page (`init_persona.js` loads successfully)
- **No fake spinner injection needed** — unlike NSD, PLW's `init_persona.js` loads without error
- **No client-side type validation** — any file type can be selected; MIME filtering happens server-side only

```javascript
// Upload — setInputFiles triggers change event → spinner → immediate form submit
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/absolute/path/to/file.pdf')
]);
// Re-check session after every navigation
if (page.url().includes('login.microsoftonline.com')) throw new Error('SESSION_EXPIRED');
```

**Multi-file upload:**
```javascript
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', ['/path/file1.pdf', '/path/file2.pptx'])
]);
```

**Server-side accepted MIME types:** `application/pdf`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/msword`, `image/png`, `image/jpeg`. Everything else is **silently dropped** (no error, no alert).

**Note on de-duplication:** PLW uses the same content-hash de-duplication as SSM. If a file with the same MD5 hash was previously uploaded, the server returns the existing DB record — the filename shown in the queue may differ from the file you uploaded. This is expected behaviour.

### 3.2 File and preference management — ⚠️ DOM click required

**Critical:** The PLW page shows a `<div class="modal-backdrop">` after uploads that **blocks Playwright's pointer events**. `page.click()` and `page.click(selector, { force: true })` both time out. Use **DOM click** (`page.evaluate(() => el.click())`) for ALL button interactions.

```javascript
// ✅ DOM click — bypasses modal backdrop overlay
await page.evaluate(() => document.querySelector('button[name="reset"]')?.click());
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});

// ❌ Playwright click — times out when backdrop is present
await page.click('button[name="reset"]');  // will timeout
```

**Why DOM click works:** It fires the browser's native `click` event directly on the DOM element, skipping Playwright's pointer-interception checks. The Clear All button (and other buttons) respond correctly to this synthetic event.

**Delete a file (source document):**
```javascript
// Finds the first file-delete form and DOM-clicks its delete button
await page.evaluate(() => {
  const forms = [...document.querySelectorAll('form[action*="/persona/"][action*="/edit/"]')];
  const fileForm = forms.find(f => !f.querySelector('select'));
  fileForm?.querySelector('input[name="delete"]')?.click();
});
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});
```

**Delete a preference chip:**
```javascript
// Clicks the delete button on the Nth chip (0-indexed)
await page.evaluate((index) => {
  const deleteBtns = [...document.querySelectorAll('input[name="delete"]')];
  deleteBtns[index]?.click();
}, 0);
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});
```

**Clear All:**
```javascript
await page.evaluate(() => document.querySelector('button[name="reset"]')?.click());
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});
// Expected alert: 'All files were cleaned up.'
```

**Verify queue:**
```javascript
const queueCount = await page.$$eval(
  'form[action*="/persona/"][action*="/edit/"]',
  fs => fs.filter(f => !f.querySelector('select')).length
).catch(() => 0);
```

### 3.3 Audience preferences

| Element | Selector |
|---|---|
| Persona dropdown | `select[name="persona"]` — 9 options (1=HIV Specialists … 9=Government or Policy Maker) |
| Language dropdown | `select[name="lang"]` — `''`=No Translation, `'fr'`=French, `'es'`=Spanish, `'de'`=German, `'it'`=Italian, `'ja'`=Japanese |
| Add button | `input[type="image"][name="add"]` — triggers `add.x` in POST |

**Add a preference chip:**
```javascript
await page.selectOption('select[name="persona"]', '1');  // HIV Specialists
await page.selectOption('select[name="lang"]', 'fr');    // French
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.evaluate(() => document.querySelector('input[name="add"]')?.click())
]);
// Chip appears: flag icon + persona icon + delete button
```

**Duplicate prevention:** `get_or_create` on the server — submitting the same persona+lang combo twice keeps only one chip.

**Count chips:**
```javascript
const chipCount = await page.evaluate(() =>
  document.querySelectorAll('form[action*="/persona/"][action*="/edit/"] input[name="delete"]').length
);
```

### 3.4 Generation
**Generate button:** `input[type="image"][name="generate"]` (class `.submit`)

The JS handler: `window.spinner.show()` + 500ms + `form.requestSubmit(button)`. Since `window.spinner` is defined, DOM click works:

```javascript
await page.evaluate(() => document.querySelector('input[name="generate"]')?.click());
await page.waitForTimeout(3000);
// Page renders with loader="1" → init_persona.js starts polling /persona/is_ready/
```

**After clicking generate** the page stays at `/persona/` but with `loader="1"` in the template. `init_persona.js` runs:
- Polls `GET /persona/is_ready/` every 3 seconds
- When `{ ready: true, error: false }` → calls `window.location.assign("/persona/download/")` → **ZIP downloads automatically**
- When `{ ready: false, error: true }` → calls `window.location.assign("/persona/")` → redirects back with any error alerts

**No manual navigation needed** — the whole flow is automated once Generate is clicked.

**Polling in progress check:**
```javascript
const loaderActive = await page.evaluate(() => !!document.querySelector('script[loader]')).catch(() => false);
// loaderActive = true → spinner is showing, polling is running
```

### 3.5 Readiness check
```javascript
const ready = await page.evaluate(async () => {
  const res = await fetch('/persona/is_ready/');
  return await res.json();
});
// ready = { error: false, ready: true }  → complete
// ready = { error: false, ready: false } → still processing
// ready = { error: true,  ready: false } → all failed
```

### 3.6 Download
The download is triggered **automatically** by `window.location.assign("/persona/download/")` when polling reports ready. The server responds with a ZIP attachment:

- `Content-Type: application/x-zip-compressed`
- `Content-Disposition: attachment; filename=plain_language_summaries_{datetime}.zip`
- ZIP contains one `.docx` per `Translation` (source × preference): `{source[:10]}_{lang}_{PersonaDisplay}_{datetime}.docx`

Playwright captures this as `ERR_ABORTED` on the download URL — this is **expected and means the download succeeded**.

```javascript
// Detect successful download: ERR_ABORTED on /persona/download/
// page.url() stays at /persona/ — the download was a file attachment, not a navigation
```

**⚠️ Empty queue download:** If no Translation objects exist, navigating to `/persona/download/` serves an **empty ZIP silently** (no warning, no redirect). The "not ready" warning only appears when translations exist but haven't finished processing. This is a known UX gap.

---

## 4. Known Issues

| Issue | Severity | Description |
|---|---|---|
| Modal backdrop blocks Playwright clicks | High | After uploads, `<div class="modal-backdrop fade show">` intercepts pointer events. `page.click()` and `page.click(selector, { force: true })` time out. Use DOM click (`page.evaluate(() => el.click())`) for all button interactions. |
| `fetch()` POST to delete endpoint doesn't work | Low | Deleting files/chips via `fetch()` POST to `/persona/{id}/edit/` doesn't process correctly. Use DOM click on `input[name="delete"]` instead (same approach as Clear All). |
| Empty ZIP served when no translations exist | Medium | `GET /persona/download/` with empty queue serves an empty ZIP silently. No "not ready" warning or redirect. Warning only appears when translations exist but are in-progress. |
| Content-hash de-duplication | Info | PLW uses `unique_only` on file uploads. Same file content re-uses the existing DB record; queue shows the original filename, not the uploaded filename. |
| Session expiry | High | Microsoft SSO expires without warning. Detect via URL change to `login.microsoftonline.com`. |

---

## 5. Test Execution Patterns

### 5.1 Full happy-path flow
```javascript
// 1. Upload a source file
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/absolute/path/to/source.pdf')
]);

// 2. Add a preference chip
await page.selectOption('select[name="persona"]', '1');  // HIV Specialists
await page.selectOption('select[name="lang"]', '');       // No Translation
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.evaluate(() => document.querySelector('input[name="add"]')?.click())
]);

// 3. Generate
await page.evaluate(() => document.querySelector('input[name="generate"]')?.click());
await page.waitForTimeout(3000);

// 4. Poll for download (init_persona.js does this automatically, but we can verify)
let downloadTriggered = false;
page.on('requestfailed', req => {
  if (req.url().includes('/persona/download/') && req.failure()?.errorText === 'net::ERR_ABORTED') {
    downloadTriggered = true;
  }
});

// Wait up to 90s for ERR_ABORTED on /persona/download/
for (let i = 0; i < 18; i++) {
  if (downloadTriggered) break;
  await page.waitForTimeout(5000);
}
// downloadTriggered === true → PASS
```

### 5.2 Wrong file type (silently dropped)
```javascript
// No client-side check — file goes to server, server filters by MIME type
const queueBefore = await getQueueCount();
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/tmp/test_plw.txt')
]);
const queueAfter = await getQueueCount();
// queueAfter === queueBefore → PASS (silently dropped, no alert)
```

### 5.3 File delete (DOM click)
```javascript
const queueBefore = await getQueueCount();
// DOM-click the first file's delete button
await page.evaluate(() => {
  const forms = [...document.querySelectorAll('form[action*="/persona/"][action*="/edit/"]')];
  forms.find(f => !f.querySelector('select'))?.querySelector('input[name="delete"]')?.click();
});
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});
const queueAfter = await getQueueCount();
// queueAfter === queueBefore - 1 → PASS
```

### 5.4 Session check after every navigation
```javascript
const checkSession = async () => {
  const url = page.url();
  const title = await page.title().catch(() => '');
  if (url.includes('login.microsoftonline.com') || title.toLowerCase().includes('sign in')) {
    throw new Error('SESSION_EXPIRED');
  }
};
// Call after every await Promise.all / waitForNavigation / page.goto
```

---

## 6. Output Verification

| Check | Automatable | Method |
|---|---|---|
| File appears in queue after upload | ✅ | Count `form[action*="/persona/"][action*="/edit/"]` without `select` |
| Wrong-type file silently dropped | ✅ | Queue count unchanged after upload; no `.alert` shown |
| "All files were cleaned up" alert | ✅ | `page.$$eval('.alert', ...)` |
| Preference chip created | ✅ | Count `input[name="delete"]` inside `/persona/{id}/edit/` forms |
| Duplicate chip prevented | ✅ | Count stays the same after second identical add |
| Spinner shown after Generate | ✅ | `document.querySelector('script[loader]')` is non-null |
| Auto-download triggered | ✅ | `requestfailed` event on `/persona/download/` with `ERR_ABORTED` |
| ZIP content / .docx filenames | ❌ Manual | Open downloaded ZIP; verify one .docx per source×preference |
| .docx content quality | ❌ Manual | Open each .docx; verify plain language summary is relevant |

---

## 7. Writing Results Back

When writing to an Excel test pack, Copilot:
1. Reads and confirms column mapping from the header row.
2. For each completed test writes: Actual Result, Status, Severity (Fail only), Comments.
3. Applies colour coding: green (Pass), red (Fail), amber (Blocked/N/A).
4. Asks before overwriting any existing non-empty result.

**Status values:** Pass / Fail / Blocked / N/A

---

## 8. Example Workflow

```
User: "Run PLW tests from test_cases/PLW_Testing_Template.xlsx"

→ Copilot asks:
  1. Fresh run or continue?
  2. Which sheet and columns?
  3. Write results back?
  4. Environment URL?
  5. Source files for upload tests — your paths or generate?
     If yours: asks for PDF, PPTX, DOCX, JPEG, PNG paths individually.
  6. Wrong-type files (.txt, .csv) needed? Generate?

→ Confirms, navigates to /persona/

→ PLW-01–05: setInputFiles per type, waitForNavigation, verify queue +1, no errors → Pass
→ PLW-06–07: setInputFiles with .txt/.csv, verify queue unchanged (silently dropped) → Pass
→ PLW-08: setInputFiles with multiple files, verify queue +2 → Pass
→ PLW-10: DOM-click first file's delete button, reload, verify queue -1 → Pass
→ PLW-11: DOM-click Clear All, reload, verify 'cleaned up' alert + queue=0 → Pass
→ PLW-12–16: selectOption + DOM-click add, verify chips, test duplicate prevention
→ PLW-17: upload + add pref + DOM-click generate → spinner shown → wait for ERR_ABORTED on /persona/download/ → Pass

→ On session expiry: STOPS immediately
  "⚠️ Session expired. Testing stopped.
   Last completed: PLW-XX. PLW-YY was interrupted — will re-run.
   Please log back in, then tell me to continue."

→ Writes all results, reports final summary
```

---

## 9. Debugging

### Upload has no effect (file not in queue)
- **Cause:** Rare case where spinner crashed before form submit. `init_persona.js` usually loads successfully on PLW.
- **Check:** `typeof window.spinner` — should be `"object"`. If `"undefined"`, inject: `window.spinner = { show: () => {}, hide: () => {} }` before `setInputFiles`.

### Clicks time out (backdrop blocking)
- **Cause:** `<div class="modal-backdrop fade show">` remains in DOM after upload spinner.
- **Fix:** Always use DOM click: `page.evaluate(() => el.click())` — never `page.click()` for PLW buttons.

### Generate shows spinner but never downloads
- **Cause A:** No preference chips set (no virtual Translation records → no combinations created → `is_ready` returns `error: true` immediately → redirect back to /persona/).
- **Cause B:** File upload failed silently (wrong MIME type).
- **Check:** Verify at least 1 chip and 1 source file exist before clicking Generate.

### Download serves empty ZIP without warning
- **Known issue:** When no Translation records exist, `/persona/download/` returns an empty ZIP. No "not ready" message appears. Only occurs when the queue is completely empty; the warning shows correctly when translations are in-progress (status not in {100, -1}).
