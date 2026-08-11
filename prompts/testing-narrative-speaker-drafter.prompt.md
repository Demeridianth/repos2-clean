# Copilot Usage Guide — Narrative Speaker Drafter (NSD) Testing

## Overview
This guide documents workflows for using Copilot to perform UAT on the **Narrative Speaker Drafter** feature of the Nexus application, covering:
- **File upload** (PPTX only — client-side and server-side validation)
- **File management** (delete, Clear All)
- **Core Narrative** (predefined congress/year narratives and custom)
- **Generation** (happy path, no-file error, loading state)
- **Notes result page** (slide navigation, speaker notes display, slide visual)
- **Use It & note editing** (marking versions, editing text)
- **Download** (PPTX with speaker notes)
- **Error handling** (corrupted, empty, text-heavy PPTX)

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
| NSD upload & form | `/note/` |
| Generation loading | `/note/{pk}/page/0/` |
| Slide result page | `/note/{pk}/page/{page_id}/` |

### 1.5 Test PPTX file — provide or generate?
**Only ask if the test pack contains tests that require uploading a PPTX source file.**

> *"Some tests need a PPTX narrative deck to upload (e.g. a slide presentation from a congress). Do you have one ready, or should I generate a synthetic one?"*

**If the user provides a file:**
> *"What is the full path to your test PPTX file?"*

Always use an **absolute path** — never `~` (Playwright does not expand shell shortcuts).

**If the user chooses generate**, Copilot creates a minimal valid PPTX:
```python
from pptx import Presentation
from pptx.util import Pt
prs = Presentation()
for i in range(3):
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = f'Slide {i+1}'
    slide.placeholders[1].text = f'Slide {i+1} content about clinical outcomes.'
prs.save('/tmp/test_nsd_upload.pptx')
```

### 1.6 Special edge-case files (conditional)
**Only ask if the test pack includes error-handling tests** (e.g. corrupted file, empty file, text-heavy file, wrong file type):

> *"Some tests need special files — a corrupted .pptx, an empty .pptx, a text-heavy .pptx, and a legacy .ppt. Should I generate these automatically, or will you provide them?"*

**If generate**, Copilot creates:
```python
# Legacy .ppt (isValidPPTX JS check rejects non-.pptx)
prs.save('/tmp/test_nsd_legacy.ppt')

# Empty PPTX (0 slides)
Presentation().save('/tmp/test_nsd_empty.pptx')

# Text-heavy PPTX (>5,250 chars/slide)
# ... 3 slides, each with ~6000 chars

# Corrupted PPTX (invalid binary)
with open('/tmp/test_nsd_corrupted.pptx', 'wb') as f:
    f.write(b'This is not a valid PPTX file\x00\x01')
```

Ask this **once upfront** for the whole run — not per test.

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

### 🔴 Session expiry (app logout)
**This is a high-risk event during NSD testing.** The Microsoft SSO session can expire during the test run with no in-app warning. Any test that was in progress when the session expired must be **re-run from scratch** after login — it cannot be marked as Pass or Fail based on incomplete execution.

**Copilot detects session expiry by checking after every navigation:**
```javascript
const isLoggedOut = page.url().includes('login.microsoftonline.com') ||
                    (await page.title()).toLowerCase().includes('sign in');
```

**When detected, Copilot MUST:**
1. **Stop the run immediately** — do not attempt any further test steps.
2. **Mark the interrupted test as N/A** with reason "Session expired mid-execution; re-run required."
3. **Report to the user clearly:**
   > *"⚠️ Session expired — the app has redirected to the Microsoft login page.*
   > *Testing has stopped. The last fully completed test was [last-passed Test ID].*
   > *[interrupted Test ID] was in progress and could not be completed — it will be re-run.*
   > *Please log back in, then tell me to continue and I will restart from [interrupted Test ID]."*
4. **Wait for explicit confirmation** from the user before doing anything else.
5. **On resume:** re-run the interrupted test from the beginning (not from where it stopped), then continue with the remaining tests in order.

**Do NOT:**
- Mark the interrupted test as Fail (it did not fail — the session ended).
- Skip the interrupted test and move to the next one.
- Attempt to continue testing while the login redirect is active.

---

## 3. Page and UI Reference

### 3.1 Upload mechanism
- **File input:** `#id_files` — accept=`.pptx,.ppt`, multiple (but only 1 file allowed per user)
- **Auto-submits 500ms after file change** (JS `setTimeout(() => form.submit(), 500)`)
- **Critical:** `init_note.js` calls `window.spinner.show()` before submitting. Since `init.js` returns HTTP 500 on this server, `window.spinner` is undefined and **the call throws before the setTimeout runs**, silently preventing the upload.

**Fix — inject a fake spinner before every `setInputFiles` call:**
```javascript
await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; });
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/absolute/path/to/file.pptx')
]);
await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; }).catch(() => {});
```

**Wrong file types (.ppt, .pdf, .docx, .jpg):** The `isValidPPTX()` JS function only accepts `.pptx` extension. Any other type triggers `alert('Please upload a .pptx file')` and resets the input — the form is NEVER submitted.
```javascript
// Set up dialog handler BEFORE setInputFiles for non-.pptx files
let dialogMsg = 'none';
page.once('dialog', async d => { dialogMsg = d.message(); await d.accept(); });
await page.setInputFiles('#id_files', '/tmp/test.pdf');
await page.waitForTimeout(1200);
// dialogMsg = 'Please upload a .pptx file'
```

**Server-side "only one file" error:** If a file is already in the queue and you upload a second `.pptx`, the server returns the warning 'You can upload only one file'.

### 3.2 File management buttons
**Both Clear All and Delete buttons are frequently blocked by a spinner backdrop** after uploads. Use DOM click to bypass:

```javascript
// Clear All
await page.evaluate(() => document.querySelector('button[name="reset"]')?.click());
await page.waitForTimeout(3000);
await page.reload({ waitUntil: 'load' }).catch(() => {});
await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; }).catch(() => {});

// Delete individual file (replace {id} with actual file ID from form action)
const csrfToken = await page.$eval('input[name="csrfmiddlewaretoken"]', el => el.value);
const fileId = await page.$eval('input[name="delete"]', el => el.closest('form')?.action?.match(/\/note\/(\d+)\/edit\//)?.[1]);
await page.evaluate(async (data) => {
  await fetch(`/note/${data.id}/edit/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': data.csrf },
    body: `csrfmiddlewaretoken=${data.csrf}&delete.x=10&delete.y=10`
  });
}, { id: fileId, csrf: csrfToken });
await page.reload({ waitUntil: 'load' }).catch(() => {});
```

### 3.3 Core Narrative
| Element | Selector |
|---|---|
| Congress dropdown | `select[name="congress"]` — CROI, AIDS, ID Week, HIV Glasgow, IAS, EACS, Custom |
| Year dropdown | `select[name="year"]` — 2024, 2025, 2026 |
| Narrative textarea | `textarea[name="narrative_core"]`, max 8024 chars, required |

**Predefined narrative AJAX:** Selecting congress + year fires a POST to `/note/get_narrative_core/` which returns JSON with `{ result: "..." }`. The JS auto-fills the textarea. Simulate and verify:
```javascript
await page.selectOption('select[name="congress"]', 'CROI');
await page.selectOption('select[name="year"]', '2024');
await page.waitForTimeout(1500); // wait for AJAX
const narrativeText = await page.$eval('textarea[name="narrative_core"]', el => el.value);
// narrativeText.length > 0 → predefined narrative loaded ✓
```

### 3.4 Generation
**Generate button:** `input[type="image"][name="generate"]` — triggers when clicked with form POST

Use DOM click (avoids backdrop issues):
```javascript
await page.fill('textarea[name="narrative_core"]', narrativeText);
await page.evaluate(() => document.querySelector('input[name="generate"]')?.click());
await page.waitForTimeout(3000);
```

**Post-generation redirect:** `/note/{pk}/page/0/` — loading state  
**Once worker finishes:** `/note/{pk}/page/{page_id}/` — first slide shown

**Generate without file error:** Alert 'Please upload a PPT presentation!'; page stays on `/note/`

### 3.5 Notes result page (`/note/{pk}/page/{page_id}/`)
Key elements:
| Element | Description |
|---|---|
| `h1` "Slide N of M" | Slide number in the deck |
| `img[alt="Page"]` | Slide visual extracted from PPTX |
| `a[href*="/note/{pk}/page/"]` | Next/Previous slide navigation |
| `#id_speaker_note` (textarea) | Current speaker note (AI-generated or saved) |
| `input[name="download"]` | Download the final PPTX with speaker notes |
| `button[name="save_and_generate"]` | Trigger speaker note generation (creates `OutputPageNote` records) |

**Important:** The initial Generate (`/note/`) only creates `OutputPage` objects (slide structure). Speaker notes (`OutputPageNote` records) are NOT created until the user clicks **"Generate with Selected"** on the notes page. Use It only works after Generate with Selected.

```javascript
// Trigger speaker note generation for current slide
await page.evaluate(() => {
  const btns = document.querySelectorAll('button');
  for (const btn of btns) {
    if (btn.innerText.trim() === 'Generate with Selected' && !btn.id.includes('footer')) {
      btn.click(); return;
    }
  }
});
// Poll for OutputPageNote records
let noteId = null;
for (let i = 0; i < 8; i++) {
  await page.waitForTimeout(3000);
  await page.reload({ waitUntil: 'load' }).catch(() => {});
  await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; }).catch(() => {});
  const opnsRaw = await page.evaluate(() => document.getElementById('root')?.getAttribute('data-full-opns') || '[]');
  const opns = JSON.parse(opnsRaw);
  if (opns.length > 0) { noteId = opns[0].id; break; }
}
```

### 3.6 Use It (mark a note as active)
After `Generate with Selected`, `OutputPageNote` records exist. Use It is triggered by a JSON POST:
```javascript
const csrf = await page.$eval('input[name="csrfmiddlewaretoken"]', el => el.value);
const useItNote = await page.$eval('#id_use_it_note', el => el.value);
const resp = await page.evaluate(async (data) => {
  const res = await fetch(window.location.href, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': data.csrf },
    body: JSON.stringify({ use_it: true, use_it_note: data.note, note_id: data.id })
  });
  return await res.json();
}, { csrf, note: useItNote, id: noteId });
// resp = { status: "success", actual_id: noteId }
```

### 3.7 Download
```javascript
// DOM click triggers file download
await page.evaluate(() => document.querySelector('input[name="download"]')?.click());
await page.waitForTimeout(2000);
// ERR_ABORTED on the download URL = browser handling file download (expected)
```

---

## 4. Known Issues

| Issue | Severity | Description |
|---|---|---|
| `init.js` returns 500 — spinner crash | High | `window.spinner.show()` is called before form submit in `init_note.js`. Since `init.js` returns 500, `window.spinner` is undefined and the call throws, **silently preventing the PPTX upload**. Fix: inject `window.spinner = { show: () => {}, hide: () => {} }` before every `setInputFiles`. |
| Modal backdrop blocks clicks | Medium | After uploads (even with spinner patched), a `<div class="modal-backdrop fade show">` may remain in the DOM, intercepting pointer events. Playwright's `page.click()` times out. Use `page.evaluate(() => el.click())` (DOM click) or `page.click(selector, { force: true })` to bypass. |
| `waitForNavigation('networkidle')` never resolves | Medium | Static resources (init.js, bootstrap.min.js, lottie-player.js) all return 500/abort, so `networkidle` waits indefinitely. Use `waitUntil: 'load'` and follow with `page.waitForTimeout()` + `page.reload()` to verify state. |
| `Generate with Selected` required before `Use It` | Info | The initial Generate only creates slide structure (`OutputPage`). Speaker notes (`OutputPageNote`) are NOT generated until "Generate with Selected" is clicked on the notes page. `Use It` will fail with no `OutputPageNote` records. |
| Only one file per user allowed | Info | Server enforces max 1 InputPpt per user. A second upload returns "You can upload only one file". Clear or delete the existing file before uploading a new one. |
| Session expiry mid-run | High | Microsoft SSO sessions expire without warning. Detect via URL change to `login.microsoftonline.com`. |

---

## 5. Test Execution Patterns

### 5.1 Full happy-path flow
```javascript
const BASE = '/path/to/testing_docs/';
const PPTX = BASE + 'my_presentation.pptx';

// Patch spinner
await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; });

// Upload
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', PPTX)
]);
await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; }).catch(() => {});

// Set congress narrative
await page.selectOption('select[name="congress"]', 'CROI');
await page.selectOption('select[name="year"]', '2024');
await page.waitForTimeout(1500);

// Generate
await page.evaluate(() => document.querySelector('input[name="generate"]')?.click());
await page.waitForTimeout(3000);

// Check redirect to notes page
const notesUrl = page.url(); // should be /note/{pk}/page/0/ or /note/{pk}/page/{id}/

// Wait for slides to be ready
let slideReady = false;
for (let i = 0; i < 12; i++) {
  await page.reload({ waitUntil: 'load' }).catch(() => {});
  await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; }).catch(() => {});
  await page.waitForTimeout(5000);
  const headings = await page.$$eval('h1', hs => hs.map(h => h.innerText.trim())).catch(() => []);
  if (headings.some(h => h.match(/Slide \d+ of \d+/) && !h.includes('of None'))) {
    slideReady = true; break;
  }
}

// Trigger note generation
await page.evaluate(() => {
  const btns = document.querySelectorAll('button');
  for (const btn of btns) {
    if (btn.innerText.trim() === 'Generate with Selected' && !btn.id.includes('footer')) { btn.click(); return; }
  }
});

// Wait for OutputPageNote records
let noteId = null;
for (let i = 0; i < 10; i++) {
  await page.waitForTimeout(3000);
  await page.reload({ waitUntil: 'load' }).catch(() => {});
  await page.evaluate(() => { window.spinner = { show: () => {}, hide: () => {} }; }).catch(() => {});
  const opns = JSON.parse(await page.evaluate(() => document.getElementById('root')?.getAttribute('data-full-opns') || '[]'));
  if (opns.length > 0) { noteId = opns[0].id; break; }
}

// Use It
const csrf = await page.$eval('input[name="csrfmiddlewaretoken"]', el => el.value);
const useItNote = await page.$eval('#id_use_it_note', el => el.value).catch(() => '');
if (noteId) {
  const resp = await page.evaluate(async (data) => {
    const res = await fetch(window.location.href, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': data.csrf },
      body: JSON.stringify({ use_it: true, use_it_note: data.note, note_id: data.id })
    });
    return await res.json().catch(() => null);
  }, { csrf, note: useItNote, id: noteId });
  // resp.status === 'success' → PASS
}

// Download
await page.evaluate(() => document.querySelector('input[name="download"]')?.click());
// ERR_ABORTED = download triggered
```

### 5.2 Wrong file type (client-side rejection)
```javascript
let dialogMsg = 'none';
page.once('dialog', async d => { dialogMsg = d.message(); await d.accept(); });
await page.setInputFiles('#id_files', '/path/to/file.pdf');
await page.waitForTimeout(1200);
// dialogMsg = 'Please upload a .pptx file'
// queue count unchanged
```

### 5.3 Checking session after every navigation
```javascript
const checkSession = async () => {
  const url = page.url();
  const title = await page.title().catch(() => '');
  if (url.includes('login.microsoftonline.com') || title.toLowerCase().includes('sign in')) {
    throw new Error('SESSION_EXPIRED');
  }
};
// Add try/catch around your test loop and report to user on SESSION_EXPIRED
```

---

## 6. Output Verification

| Check | Automatable | Method |
|---|---|---|
| File appears in queue after upload | ✅ | `page.$$eval('form[action*="/edit/"]', fs => fs.length)` |
| Wrong-type alert shown | ✅ | `page.once('dialog', ...)` |
| "Only one file" alert | ✅ | `page.$$eval('.alert', ...)` |
| "All files were cleaned up" alert | ✅ | `page.$$eval('.alert', ...)` |
| Core narrative auto-filled | ✅ | `page.$eval('textarea[name="narrative_core"]', el => el.value)` |
| Generation redirects to result page | ✅ | `page.url().match(/\/note\/\d+\/page\/\d+/)` |
| "Slide N of M" heading | ✅ | `page.$eval('h1', el => el.innerText)` |
| Slide image visible | ✅ | `page.$('img[alt="Page"]')` |
| Speaker notes generated | ✅ | `data-full-opns` attribute on `#root` |
| Use It returns success | ✅ | JSON response `{ status: "success" }` |
| Download triggered | ✅ | ERR_ABORTED on download URL |
| Downloaded PPTX content | ❌ Manual | Open downloaded file; verify notes on each slide |

---

## 7. Writing Results Back

When writing to an Excel test pack, Copilot:
1. Reads and confirms column mapping from the header row.
2. For each completed test writes: Actual Result, Status, Severity (Fail only), Comments.
3. Applies colour coding: green (Pass), red (Fail), amber (Blocked/N/A).
4. Asks before overwriting any existing non-empty result.

**Status values:** Pass / Fail / Blocked / N/A / Manual check required

---

## 8. Example Workflow

```
User: "Run NSD tests from test_cases/NSD_Testing_Template.xlsx"

→ Copilot asks:
  1. Fresh run or continue?
  2. Which sheet? Which columns?
  3. Write results back?
  4. Environment URL?
  5. PPTX for upload tests — your file or generate?
     If yours: "What is the full absolute path?"
  6. Edge-case files needed (corrupted, empty, text-heavy, legacy .ppt)?
     If generate: creates them in /tmp/

→ Confirms answers, navigates to /note/

→ NSD-01: Patches spinner, uploads PPTX, verifies queue → Pass
→ NSD-02: Sets dialog handler, uploads .ppt, checks dialog → Pass
→ NSD-03/04: Same for .pdf and .docx → Pass
→ NSD-05: Uploads second .pptx, checks "only one file" alert → Pass
→ NSD-06: Fetches delete POST, verifies queue empty → Pass
→ NSD-07: DOM-clicks Clear All, verifies "cleaned up" alert → Pass
→ NSD-08–12: Sets congress/year dropdowns, checks textarea → Pass
→ NSD-13: Upload + narrative + generate, waits for slide result → Pass
→ NSD-19/21/22: Generate with Selected, polls for notes, Use It → Pass

→ On session expiry: STOPS immediately
  "⚠️ Session expired. Testing stopped.
   Last completed test: NSD-25.
   NSD-26 was in progress and will be re-run.
   Please log back in, then tell me to continue — I will restart from NSD-26."
  → Marks NSD-26 as N/A (session expired), waits for user confirmation
  → On resume: re-runs NSD-26 from scratch, then continues NSD-27+

→ On failure: "NSD-XX failed — [expected vs actual]. Continue?"
→ Writes all results, reports final summary
```

---

## 9. Debugging

### Upload has no effect (file not in queue after `setInputFiles`)
- **Cause:** `window.spinner.show()` threw before `setTimeout(form.submit)` ran
- **Fix:** Always inject `window.spinner = { show: () => {}, hide: () => {} }` before `setInputFiles`

### Click timeouts on Clear All / Delete
- **Cause:** `<div class="modal-backdrop fade show">` intercepting pointer events
- **Fix:** `page.evaluate(() => el.click())` (DOM click) bypasses pointer event interception

### `waitForNavigation('networkidle')` hangs
- **Cause:** init.js, bootstrap.min.js, lottie-player.js all return 500/abort → network never idles
- **Fix:** Use `waitUntil: 'load'` + `page.waitForTimeout()` + `page.reload()` to verify page state

### Speaker notes textarea stays "Nothing to see here yet!"
- **Cause:** "Generate with Selected" hasn't been clicked — initial generation only creates slide structure
- **Fix:** Click "Generate with Selected" button, then poll `data-full-opns` attribute on `#root` for `OutputPageNote` records

### Use It returns 404 or fails
- **Cause:** No `OutputPageNote` records exist (see above)
- **Fix:** Run "Generate with Selected" first, wait for `data-full-opns` to have entries, then Use It
