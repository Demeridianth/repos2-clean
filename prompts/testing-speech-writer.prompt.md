# Copilot Usage Guide — Speech Writer Testing

## Overview
This guide documents workflows for using Copilot to perform UAT on the **Speech Writer** feature of the Nexus application, covering:
- **File upload** (PDF, PPTX, DOCX, JPEG, PNG — server-side MIME filtering, unique_only de-duplication)
- **File management** (delete, Clear All)
- **Audience preferences** (persona + language chips)
- **Generation** (trigger, spinner, automatic polling, auto-download via `window.location.assign`)
- **Direct download** (GET `/poster/download/` when scripts already ready)
- **Error handling** (corrupted files, wrong types, re-generation)

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
| Speech Writer | `/poster/` |
| Readiness check | `/poster/is_ready/` |
| Download ZIP | `/poster/download/` |

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
with open('/tmp/test_sw.pdf', 'wb') as f: f.write(b'%PDF-1.4 minimal pdf')

# PPTX
from pptx import Presentation
prs = Presentation(); prs.slides.add_slide(prs.slide_layouts[0])
prs.slides[0].shapes.title.text = 'Test Speech Writer Slide'
prs.save('/tmp/test_sw.pptx')

# DOCX
from docx import Document
doc = Document(); doc.add_paragraph('Test speech writer content.')
doc.save('/tmp/test_sw.docx')

# JPEG / PNG
from PIL import Image
img = Image.new('RGB', (400, 300), color=(80, 120, 160))
img.save('/tmp/test_sw.jpg'); img.save('/tmp/test_sw.png')
```

### 1.6 Wrong-type files (conditional)
**Only ask if the test pack contains tests for rejected file types (.txt, .csv, etc.):**
> *"Some tests upload files that should be rejected (.txt, .csv). Should I create these in /tmp/ automatically?"*

```python
with open('/tmp/test_sw.txt', 'w') as f: f.write('Plain text test content.')
with open('/tmp/test_sw.csv', 'w') as f: f.write('id,title\n1,Test')
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

### 3.1 Upload mechanism
- **File input:** `#id_files`, accept=`.pdf,.pptx,.jpg,.jpeg,.png,.doc,.docx`, multiple
- **Auto-submits immediately on `change` event** — `id_files.form.submit()` (no delay, no spinner call before submit)
- **`window.spinner` IS defined** (`init_script.js` loads successfully — no fake spinner injection needed)
- **No client-side type validation** — any file type can be sent; server filters by MIME type
- **unique_only = True** — `ScriptUploadForm` de-duplicates by MD5 hash. If the same file content was previously uploaded, the server returns the existing DB record. The filename shown in the queue may differ from what you uploaded.

```javascript
// Upload — setInputFiles triggers change → immediate form submit
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/absolute/path/to/file.pdf')
]);
// Check session after every navigation
if (page.url().includes('login.microsoftonline.com')) throw new Error('SESSION_EXPIRED');
```

**Server-side accepted MIME types:** `application/pdf`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/msword`, `image/png`, `image/jpeg`. Everything else is **silently dropped** (no error, no alert).

**Multi-file upload:**
```javascript
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', ['/path/file1.pdf', '/path/file2.pptx'])
]);
```

### 3.2 File and preference management — DOM click required

**The modal backdrop from uploads blocks Playwright's pointer events.** Use DOM click (`page.evaluate(() => el.click())`) for all buttons:

```javascript
// ✅ DOM click — bypasses modal backdrop overlay
await page.evaluate(() => document.querySelector('button[name="reset"]')?.click());
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});

// ❌ Playwright click — times out when backdrop present
await page.click('button[name="reset"]');  // will timeout
```

**Delete a file:**
```javascript
await page.evaluate(() => {
  const forms = [...document.querySelectorAll('form[action*="/poster/script/"][action*="/edit/"]')];
  forms[0]?.querySelector('input[name="delete"]')?.click();
});
await page.waitForTimeout(2000);
await page.reload({ waitUntil: 'load' }).catch(() => {});
```

**Delete a preference chip (by index):**
```javascript
await page.evaluate((index) => {
  const btns = [...document.querySelectorAll('input[name="delete"]')];
  btns[index]?.click();
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

**Count queue items:**
```javascript
// Counts BOTH file entries AND preference chips (all share the same form pattern)
const totalItems = await page.$$eval(
  'form[action*="/poster/script/"][action*="/edit/"]',
  fs => fs.length
).catch(() => 0);
// To count only preference chips: subtract 1 per source file in queue
```

### 3.3 Audience preferences

| Element | Selector |
|---|---|
| Persona dropdown | `select[name="persona"]` — 9 options |
| Language dropdown | `select[name="lang"]` — `''`=No Translation, `'fr'`=French, `'es'`=Spanish, `'de'`=German, `'it'`=Italian, `'ja'`=Japanese |
| Add button | `input[type="image"][name="add"]` |

**Add a preference chip:**
```javascript
await page.selectOption('select[name="persona"]', '1');  // HIV Specialists
await page.selectOption('select[name="lang"]', '');       // No Translation
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.evaluate(() => document.querySelector('input[name="add"]')?.click())
]);
```

**⚠️ Critical SW behaviour:** Adding a preference chip **deletes all previously derived scripts** (`Script.objects.filter(virtual=False, source_id__isnull=False).delete()`). Any generated output is wiped when you add a new preference. Only one virtual (preference) chip can exist at a time per persona+lang combination.

**Duplicate prevention:** `get_or_create` — submitting the same persona+lang twice creates only one chip.

### 3.4 Generation

**Generate button:** `input[type="image"][name="generate"]` (class `.submit`)

The `.submit` class JS handler: `window.spinner.show()` + 500ms + `form.requestSubmit(button)`.

```javascript
await page.evaluate(() => document.querySelector('input[name="generate"]')?.click());
await page.waitForTimeout(3000);
// Page renders with loader="1" → init_script.js starts polling /poster/is_ready/
```

**After clicking generate:** The page stays at `/poster/` with `loader="1"`. `init_script.js` polls `GET /poster/is_ready/` every 3 seconds:
- `{ ready: true, error: false }` → `window.location.assign("/poster/download/")` → **ZIP downloads automatically**
- `{ ready: false, error: true }` → `window.location.assign("/poster/")` → redirects back with error alerts

**No manual navigation needed** — the whole flow is automated once Generate is clicked.

**⚠️ Important:** The visible **"Download" button** (`input[name="download"]`) in the form submits a POST to `/poster/` with `download.x`, which the `scripts` view **ignores**. The Download button does not directly download anything — it has no effect. The actual download only happens via auto-polling or by navigating directly to `/poster/download/` (GET).

### 3.5 Readiness check
```javascript
const state = await page.evaluate(async () => {
  const res = await fetch('/poster/is_ready/');
  return await res.json();
});
// state = { error: false, ready: true, msg: "", progress: false }
// SW returns 4 fields (vs PLW's 3) — includes "progress"
```

### 3.6 Download
**Auto-triggered** by `window.location.assign("/poster/download/")` when polling reports ready:
- `Content-Type: application/x-zip-compressed`
- `Content-Disposition: attachment; filename=scripts_{username}_{datetime}.zip`
- ZIP contains `.docx` files: `{source[:10]}_{lang}_{PersonaDisplay}_{datetime}.docx`

Playwright captures this as `ERR_ABORTED` — this is **expected and confirms the download succeeded**.

**Direct download** (GET when scripts already ready):
```javascript
// Listen for the download ERR_ABORTED before navigating
let downloaded = false;
page.on('requestfailed', req => {
  if (req.url().includes('/poster/download/')) downloaded = true;
});
await page.goto(baseUrl + '/poster/download/', { waitUntil: 'load' }).catch(() => {});
// downloaded === true → PASS
```

---

## 4. Known Issues

| Issue | Severity | Description |
|---|---|---|
| Modal backdrop blocks Playwright clicks | Medium | After uploads, a modal overlay intercepts pointer events. Use DOM click (`page.evaluate(() => el.click())`) for all buttons. |
| Download button has no effect | Info | `input[name="download"]` submits POST to `/poster/` with `download.x` which the `scripts` view ignores. The download is only triggered by auto-polling or direct GET to `/poster/download/`. |
| Adding preference chip deletes derived scripts | Info | Every time a preference chip is added, all previously generated scripts (derived) are deleted. This is by design but may surprise testers. |
| unique_only de-duplication | Info | `ScriptUploadForm` hashes file content. Same file re-uses existing DB record; queue shows the original filename, not the uploaded one. |
| Session expiry | High | Microsoft SSO expires without warning. Detect via URL change to `login.microsoftonline.com`. |
| Download with empty queue causes 500 error | Low | Navigating directly to `/poster/download/` with no Script records causes a server error (`UnboundLocalError: vo`). Not user-reachable: the Download button is ignored, and auto-polling never fires with empty queue. |

---

## 5. Test Execution Patterns

### 5.1 Full happy-path flow
```javascript
// 1. Upload source file
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/absolute/path/to/source.pdf')
]);

// 2. Add preference chip
await page.selectOption('select[name="persona"]', '1');  // HIV Specialists
await page.selectOption('select[name="lang"]', '');       // No Translation
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.evaluate(() => document.querySelector('input[name="add"]')?.click())
]);

// 3. Generate
await page.evaluate(() => document.querySelector('input[name="generate"]')?.click());
await page.waitForTimeout(3000);

// 4. Detect auto-download
let downloaded = false;
page.on('requestfailed', req => {
  if (req.url().includes('/poster/download/')) downloaded = true;
});
for (let i = 0; i < 18; i++) {
  if (downloaded) break;
  await page.waitForTimeout(5000);
}
// downloaded === true → PASS
```

### 5.2 Wrong file type (silently dropped)
```javascript
const queueBefore = await getQueueCount();
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/tmp/test_sw.txt')
]);
const queueAfter = await getQueueCount();
// queueAfter === queueBefore → PASS (no alert, silently dropped)
```

### 5.3 Detecting session expiry
```javascript
const checkSession = async () => {
  const url = page.url();
  const title = await page.title().catch(() => '');
  if (url.includes('login.microsoftonline.com') || title.toLowerCase().includes('sign in')) {
    throw new Error('SESSION_EXPIRED');
  }
};
// Call after every navigation
```

---

## 6. Output Verification

| Check | Automatable | Method |
|---|---|---|
| File appears in queue after upload | ✅ | Count `form[action*="/poster/script/"][action*="/edit/"]` |
| Wrong-type silently dropped | ✅ | Queue count unchanged; no `.alert` |
| "All files were cleaned up" alert | ✅ | `page.$$eval('.alert', ...)` |
| Preference chip created | ✅ | Count increases after `input[name=add]` click |
| Duplicate chip prevented | ✅ | Count stays same after identical add |
| Spinner shown after Generate | ✅ | `document.querySelector('script[loader]')` is non-null |
| Auto-download triggered | ✅ | `requestfailed` on `/poster/download/` with `ERR_ABORTED` |
| Direct download (GET) | ✅ | Navigate to `/poster/download/`; `ERR_ABORTED` confirms ZIP |
| ZIP content / .docx filenames | ❌ Manual | Open ZIP; verify one .docx per source×preference |
| Speech script content quality | ❌ Manual | Open each .docx; verify script is relevant |

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
User: "Run SW tests from test_cases/SW_Testing_Template.xlsx"

→ Copilot asks:
  1. Fresh run or continue?
  2. Which sheet and columns?
  3. Write results back?
  4. Environment URL?
  5. Source files — your paths or generate?
     If yours: asks for PDF, PPTX, DOCX, JPEG, PNG paths individually.
  6. Wrong-type files (.txt, .csv) — generate?

→ Confirms, navigates to /poster/

→ SW-01–05: setInputFiles per type, verify queue +1, no errors → Pass
→ SW-06–07: setInputFiles with .txt/.csv, verify queue unchanged → Pass
→ SW-08: setInputFiles with 2 files, verify queue +2 → Pass
→ SW-09: DOM-click first file's delete, reload, verify queue -1 → Pass
→ SW-10: DOM-click Clear All, reload, verify 'cleaned up' alert + queue=0 → Pass
→ SW-11–15: selectOption + DOM-click add, verify chips, test duplicate
→ SW-16: upload + pref + DOM-click generate → spinner → ERR_ABORTED → Pass
→ SW-23: navigate to /poster/download/ (GET) → ERR_ABORTED → Pass

→ On session expiry: STOPS immediately
  "⚠️ Session expired. Testing stopped.
   Last completed: SW-XX. SW-YY was interrupted — will re-run.
   Please log back in, then tell me to continue."

→ Writes all results, reports summary
```

---

## 9. Debugging

### Upload has no effect (file not in queue)
- `window.spinner` should be defined on SW page. Run `typeof window.spinner` — should be `"object"`.
- If `"undefined"`, inject: `window.spinner = { show: () => {}, hide: () => {} }` before `setInputFiles`.
- Check that `init_script.js` loaded (check browser console for script errors).

### Clicks time out (backdrop blocking)
- After uploads, the spinner backdrop may remain. Always use DOM click.

### Generate shows spinner but never downloads
- **Cause A:** No preference chips (virtual Scripts) → no combinations → no derived scripts → `is_ready` returns `{error:true}` → redirect back.
- **Cause B:** File upload failed silently (wrong MIME type).
- **Verify:** At least 1 preference chip + 1 source file before clicking Generate.

### Download button appears to do nothing
- This is correct. `input[name="download"]` submits POST to `/poster/` with `download.x` which the `scripts` view ignores. The download only happens via auto-polling (`window.location.assign`) or direct GET to `/poster/download/`.

### Adding a preference chip wipes previous output
- By design. The SW view deletes all derived Scripts (`virtual=False, source_id__isnull=False`) whenever a new preference chip is added. Always add ALL preferences before clicking Generate.
