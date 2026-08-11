# Copilot Usage Guide — Voice Creator Testing

## Overview
This guide documents workflows for using Copilot to perform UAT on the **Voice Creator** (VC) feature of the Nexus application, covering:
- **File upload** (`.txt`, `.docx` — character limit 5,250; empty files silently rejected)
- **Language auto-detection** (async pool after upload)
- **Voice Studio** (per-file voice/accent selection — all checked by default)
- **Generation** (synchronous via Azure Speech API — page blocks 10–120 s per file/voice)
- **In-browser playback** (`<audio class="player" controls>` with base64 MP3 data URI)
- **Download All ZIP** (`GET /voice/output/download_all/`)
- **File management** (delete individual file, Clear All)
- **Error handling** (empty files, corrupted `.docx`, over-limit files, no voice selected)

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
| Voice Creator | `/voice/` |
| Individual MP3 download | `/voice/output/<pk>/download/` |
| Delete a Voice file | `/voice/output/<pk>/edit/` (POST with `delete.x`) |
| Download All ZIP | `/voice/output/download_all/` (GET) |

### 1.5 Source script files — provide or generate?
> *"Some tests need script files to upload (.txt, .docx). Do you have them, or should I generate synthetic ones in /tmp/?"*

**If generate**, Copilot creates these files:
```python
# English .txt (short, ~600 chars)
with open('/tmp/test_vc_english.txt', 'w') as f:
    f.write("Pharmacokinetics of Oral Islatravir Plus Lenacapavir Given Once Weekly. " * 8)

# English .docx
from docx import Document
doc = Document(); doc.add_paragraph("Islatravir pharmacokinetics study content. " * 8)
doc.save('/tmp/test_vc_english.docx')

# French .txt
with open('/tmp/test_vc_french.txt', 'w') as f:
    f.write("Données pharmacocinétiques pour l'islatravir et le lénacapavir. " * 8)

# Long .txt (>5,250 chars — for over-limit test)
with open('/tmp/test_vc_long.txt', 'w') as f:
    f.write("A" * 6500)

# Empty .txt (0 bytes — for empty file test)
open('/tmp/test_vc_empty.txt', 'w').close()

# Exact 5,250-char .txt (for boundary test)
with open('/tmp/test_vc_exact5250.txt', 'w') as f:
    f.write("B" * 5250)

# Corrupted .docx (invalid ZIP bytes — for error handling test)
with open('/tmp/test_vc_corrupted.docx', 'wb') as f:
    f.write(b'\x00\x01\x02CORRUPTED_NOT_A_ZIP' * 10)
```

Always use **absolute paths** — never `~`.

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

**⚠️ Session expiry is the highest-risk issue for Voice Creator tests.**
The Azure Speech API synthesis is synchronous: the Django view blocks the HTTP request for 10–120 seconds per file/voice while audio is generated. The Microsoft SSO session token can expire during this wait, causing an invisible logout mid-request.

#### Detection
After every navigation, check for redirect to the Microsoft login page:
```javascript
// Define once at the top of every test run
const checkSession = (testId) => {
  if (page.url().includes('login.microsoftonline.com')) {
    throw new Error(`SESSION_EXPIRED:${testId}`);
  }
};
```

Call `checkSession(currentTestId)` after **every** `waitForNavigation`, `page.goto()`, or form submission:
```javascript
await page.waitForNavigation({ waitUntil: 'load', timeout: 180000 });
checkSession('VC-14');  // throws immediately if redirected to login
```

#### What Copilot MUST do when session expires

The entire test run is wrapped in a try/catch:
```javascript
try {
  // ... run each test in sequence ...
} catch (err) {
  if (err.message.startsWith('SESSION_EXPIRED:')) {
    const interruptedTest = err.message.split(':')[1];  // e.g. 'VC-14'
    // 1. Mark the interrupted test as N/A in the results file
    // 2. Stop — do not run any further tests
    // 3. Notify the user (see message below)
  } else {
    throw err;  // re-throw genuine test errors
  }
}
```

When caught, Copilot **stops immediately** and reports:
> *"⚠️ Session expired — the app redirected to the Microsoft login page.*
> *Testing has stopped. The last fully completed test was **[last-passed Test ID]**.*
> ***[interrupted Test ID]** was in progress and has been marked N/A (session expired mid-execution).*
> *Please log back in to the app, then tell me to continue and I will re-run from **[interrupted Test ID]**."*

Then **wait for explicit confirmation** before doing anything else.

#### On resume
When the user confirms they are logged back in:
1. Re-run the interrupted test **from the beginning** (it was marked N/A, not failed).
2. Continue with all remaining tests in order.
3. Do **not** re-run tests that already have a Pass result.

#### Mitigation strategies
- Use short script files (<1,000 chars) to minimise Azure Speech processing time.
- Select only ONE voice per file to halve generation time.
- Test generation cases (VC-14 to VC-18) first, while the session is freshest.
- Keep total generation calls per session to a minimum.

---

## 3. Page and UI Reference

### 3.1 Upload mechanism
- **File input:** `#id_files`, accept=`.doc,.docx,.txt`, `multiple`
- **Auto-submits immediately** on `change` event via `init_voice.js` (500ms delay + `form.submit()`)
- **`window.spinner` IS defined** on `/voice/` — no fake spinner needed
- **No server-side MIME filtering** — any file type is accepted and submitted; errors appear in Voice Studio
- **`unique_only = True`** — `VoiceUploadForm` de-duplicates by MD5 hash. Same content = same DB record returned.
- **Character limit: 5,250 chars (inclusive)** — over-limit files are accepted but will show an error on language detection or generation
- **Empty files (0 bytes):** silently rejected by `VoiceUploadForm.is_valid()` — no error message displayed, file not added to queue

```javascript
// Upload — setInputFiles triggers change → auto-submit via init_voice.js
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', '/absolute/path/to/script.txt')
]);
// Always check session after every navigation
if (page.url().includes('login.microsoftonline.com')) throw new Error('SESSION_EXPIRED');
```

**Multi-file upload:**
```javascript
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
  page.setInputFiles('#id_files', ['/tmp/test_vc_english.txt', '/tmp/test_vc_french.txt'])
]);
```

**⚠️ init_voice.js 500 error:** If the server returns a 500 for static assets, `init_voice.js` may fail to load. When this happens:
- Voice checkbox changes do NOT auto-submit
- Upload button click does NOT trigger the spinner delay (but file input `change` still submits the form natively)
- Check the browser console for `Failed to load resource: 500` on `init_voice.js`

### 3.2 Voice Studio
After upload, the Voice Studio section appears as an accordion. It shows one card per uploaded file with:
- `<h5>`: `#{voice_pk} / {filename} - {lang}` (e.g., `#326 / test_vc_english.txt - en`)
- `<h6 class="text-danger">`: error text if language detection or content extraction failed
- A nested "Select preferred voice(s)" accordion with voice checkboxes

**Expand the voice selector:**
```javascript
await page.evaluate(() => {
  document.querySelector('button.accordion-button.lang')?.click();
});
await page.waitForTimeout(600);
```

**Voice checkboxes:**
```javascript
// All available voices are checked by default in the template
const cbState = await page.evaluate(() => {
  const cbs = [...document.querySelectorAll('input[type="checkbox"]')];
  return cbs.map(c => ({ name: c.name, value: c.value, checked: c.checked }));
});
// name format: voice_{voice_pk}, value: Azure voice name (e.g. 'en-US-BrianMultilingualNeural')
```

**Uncheck a specific voice (e.g., keep only Brian for faster generation):**
```javascript
await page.evaluate(() => {
  const cbs = [...document.querySelectorAll('input[type="checkbox"]')];
  // Uncheck second checkbox (Emma)
  if (cbs.length > 1 && cbs[1].checked) cbs[1].click();
});
await page.waitForTimeout(300);
```

**⚠️ If `init_voice.js` loaded successfully**, checking/unchecking a voice checkbox triggers an instant auto-submit navigation (`.instant-edit` behaviour). Always wait for navigation after each checkbox change:
```javascript
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {}),
  page.evaluate(() => document.querySelector('input[type="checkbox"]')?.click())
]);
```

### 3.3 Generate button
The generate button is `input[type="image"][name="generate"]` inside the Voice Studio form (`id="collapseOne"`). It is NOT a `<button>` element.

```javascript
// ✅ Correct — use page.click() on the image input
await Promise.all([
  page.waitForNavigation({ waitUntil: 'load', timeout: 180000 }),
  page.click('input[name="generate"]')
]);
// ❌ Wrong — button[type="submit"] targets a different element or the logout button
```

**The navigation timeout should be at least 180 seconds** for the first generation of multi-file/multi-voice requests.

### 3.4 Output section
After successful generation, the page shows a "Your Voice Overs are ready to download" section:

```javascript
// Confirm output section is visible
const hasOutput = !!document.querySelector('.voice-studio header');
const h1s = [...document.querySelectorAll('h1')].map(h => h.innerText.trim());
// h1s will include 'Your Voice Overs are ready to download' if outputs exist

// Count audio players in output section
const playerAudios = document.querySelectorAll('audio.player').length;
// Each generated voice = 1 <audio class="player" controls src="data:audio/mpeg;base64,...">

// Find individual download forms
const outputForms = [...document.querySelectorAll('form')].filter(f =>
  (f.action || '').includes('/voice/output/') && (f.action || '').includes('/download/')
).map(f => f.action);
// Format: https://{host}/voice/output/{pk}/download/
```

**No output section:** if `anyoutput` context is empty (no VoiceOutputs with `processed` set and `file` not null), the section is hidden. This happens when:
- No voices were checked before Generate
- Generation failed (VoiceOutput set `unprocessable=True`)
- `generate.x` was not in the POST data (wrong button clicked)

### 3.5 File management
**Delete an individual uploaded file** (removes the Voice + all its VoiceOutputs):
```javascript
await page.evaluate(() => {
  // The delete form action is /voice/output/{voice_pk}/edit/
  const deleteForm = document.querySelector('form[action*="/voice/output/"][action*="/edit/"]');
  deleteForm?.querySelector('input[name="delete"]')?.click();
});
await page.waitForNavigation({ waitUntil: 'load', timeout: 10000 }).catch(() => {});
```

**Clear All** (removes ALL Voices and VoiceOutputs for the user):
```javascript
await page.evaluate(() => {
  document.querySelector('button.clear-all-btn, button[name="reset"]')?.click();
});
await page.waitForNavigation({ waitUntil: 'load', timeout: 15000 }).catch(() => {});
// Expected alert: 'All files were cleaned up.'
```

### 3.6 Download All ZIP
```javascript
// GET /voice/output/download_all/ — returns application/x-zip-compressed
const zipResult = await page.evaluate(async () => {
  const resp = await fetch('/voice/output/download_all/', { method: 'GET' });
  return {
    status: resp.status,
    contentType: resp.headers.get('Content-Type'),
    filename: resp.headers.get('Filename')
  };
});
// Expected: status=200, contentType contains 'zip', filename starts with 'voice_over_'
```

### 3.7 Individual MP3 download
The individual download button (`input.download-btn`) does **not** POST to the server. `init_voice.js` intercepts the click with `e.preventDefault()` and performs a **pure client-side download** using the base64 audio data already embedded in the page:

```javascript
// init_voice.js handler (runs in real browser when JS loads successfully)
const check_readness = (e) => {
  e.stopPropagation();
  e.preventDefault();  // ← server endpoint is never called
  const link = document.createElement("a");
  link.download = e.target.dataset["name"];  // filename from data-name attribute
  link.href = e.target.form.closest("div").children[1].children[0].src;  // base64 audio src
  link.click();
};
document.querySelectorAll(".download-btn").forEach(x => x.addEventListener("click", check_readness));
```

To test this in Playwright (where `init_voice.js` may fail to load due to CSP nonces), inject the handler manually:
```javascript
await page.evaluate(() => {
  const check_readness = (e) => {
    e.stopPropagation();
    e.preventDefault();
    const link = document.createElement("a");
    link.download = e.target.dataset["name"];
    link.href = e.target.form.closest("div").children[1].children[0].src;
    link.click();
  };
  document.querySelectorAll(".download-btn").forEach(x => x.addEventListener("click", check_readness));
});
```

To verify the audio data is valid without triggering a browser download:
```javascript
const audioFiles = await page.evaluate(() =>
  [...document.querySelectorAll('audio.player')].map(a => ({
    hasAudio: a.src.startsWith('data:audio/mpeg;base64,'),
    estimatedBytes: Math.floor(a.src.length * 0.75),
    filename: a.closest('.card-body')?.querySelector('.download-btn')?.dataset?.name
  }))
);
// Each file ~3+ MB, filename: voice_over_{id}_{voice}_{username}_{timestamp}.mp3
```

> **Latent server bug:** `voice/views.py` line 170 calls `vo.download_mp3_audio()` which is absent from `voice/models.py`. A direct GET/POST to `/voice/output/{pk}/download/` returns HTTP 500. This doesn't affect users because the UI JS never calls the server endpoint.

---

## 4. Re-generation Behaviour

The `voice_list` view uses `get_or_create` for VoiceOutput objects:
```python
vo, created = v.voiceoutput_set.get_or_create(
    voice_id=v.id, lang=v.lang, accent=acc,
    defaults={'user_log_id': tracking_id, 'user': request.user}
)
if not created:
    # Already exists — update log reference only, do NOT re-generate
    vo.user_log_id = tracking_id
```

The generation filter is: `VoiceOutput.objects.filter(processed=None, unprocessable=False, ...)`.

**Consequence:** Re-clicking Generate on an already-processed file returns the existing output in < 5 seconds without calling Azure Speech. This is idempotent by design.

---

## 5. Common Issues and Fixes

| Issue | Cause | Fix |
|---|---|---|
| Session expires during generation | Azure Speech synthesis blocks HTTP request for 10–120 s; SSO token expires | Use shorter test files; select only 1 voice; restart session and re-run generation tests |
| "Clear All" fires instead of Generate | Wrong button selector — `button[type="submit"]` matches logout, Clear All, or other forms first | Always use `input[name="generate"]` not `button[type="submit"]` |
| No "Your Voice Overs" section shown | `anyoutput` context empty — `generate.x` missing from POST, or all outputs already `processed` and filter didn't match | Verify `input[name="generate"]` was clicked (it's an image input, not a button) |
| Individual download button does nothing in Playwright | `init_voice.js` not loaded (CSP nonce) → `e.preventDefault()` handler not registered → native form POST fires → server returns 500 (broken `download_mp3_audio` method) | Inject `check_readness` handler manually before clicking; or verify audio data directly from `audio.player` src |
| Voice checkboxes not auto-submitting | `init_voice.js` failed to load (500 on static asset) | Use `page.click()` on checkboxes without expecting auto-submit; expand selector first |
| Empty file silently not uploaded | `VoiceUploadForm.is_valid()` rejects 0-byte files with no user feedback | No fix needed — correct silent rejection. Note: UX gap (no error message) |
| Language detected incorrectly (e.g., English detected as Finnish) | Azure language detection uses statistical models; very short or random-looking text may mis-detect | Use realistic medical content in test files for reliable language detection |

---

## 6. Full Test Run Sequence (Recommended Order)

Run in this order to minimise session expiry risk and maximise re-use of generated outputs:

1. **File upload tests** (VC-01 to VC-06) — upload only, no generation, fast
2. **Language detection tests** (VC-07 to VC-09) — detected after upload
3. **Voice Studio UI tests** (VC-10 to VC-13) — inspect checkboxes/accordion, no generation
4. **File management tests** (VC-24) — Clear All before generation tests
5. **Generation tests** (VC-14 to VC-18) — start when session is freshest
6. **Audio playback tests** (VC-19) — check `<audio class="player">` after generation
7. **Download tests** (VC-21, VC-22) — after generation
8. **Re-generation test** (VC-25) — uses cached outputs, fast
9. **Error/edge-case tests** (VC-26 to VC-28) — upload edge-case files, less session risk

---

## 7. Minimal Working Test Example

```javascript
// Full VC happy-path: upload → generate (Brian) → verify output → download ZIP
const checkSession = (testId) => {
  if (page.url().includes('login.microsoftonline.com')) {
    throw new Error(`SESSION_EXPIRED:${testId}`);
  }
};

try {
  // 1. Upload English .txt
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'load', timeout: 20000 }).catch(() => {}),
    page.setInputFiles('#id_files', '/tmp/test_vc_english.txt')
  ]);
  checkSession('VC-01');

  // 2. Expand voice selector, uncheck Emma (keep Brian only for speed)
  await page.evaluate(() => document.querySelector('button.accordion-button.lang')?.click());
  await page.waitForTimeout(600);
  await page.evaluate(() => {
    const cbs = [...document.querySelectorAll('input[type="checkbox"]')];
    if (cbs.length > 1 && cbs[1].checked) cbs[1].click();
  });
  await page.waitForTimeout(300);

  // 3. Generate (synchronous — may take 10–120s)
  const startTime = Date.now();
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'load', timeout: 180000 }),
    page.click('input[name="generate"]')
  ]);
  checkSession('VC-14');
  const elapsed = Date.now() - startTime;

  // 4. Verify output
  const result = await page.evaluate(() => ({
    hasOutput: !!document.querySelector('.voice-studio header'),
    audioPlayers: document.querySelectorAll('audio.player').length,
    outputForms: [...document.querySelectorAll('form')]
      .filter(f => (f.action || '').includes('/voice/output/') && f.action.includes('/download/'))
      .map(f => f.action)
  }));
  // Expected: hasOutput=true, audioPlayers=1, outputForms has 1 URL

  // 5. Download All ZIP
  const zipResult = await page.evaluate(async () => {
    const resp = await fetch('/voice/output/download_all/', { method: 'GET' });
    return { status: resp.status, contentType: resp.headers.get('Content-Type') };
  });
  // Expected: status=200, contentType includes 'zip'

  return JSON.stringify({ elapsedMs: elapsed, result, zipResult });

} catch (err) {
  if (err.message.startsWith('SESSION_EXPIRED:')) {
    const interrupted = err.message.split(':')[1];
    return JSON.stringify({
      sessionExpired: true,
      interruptedTest: interrupted,
      message: `Session expired during ${interrupted}. Mark as N/A. User must log back in, then resume from ${interrupted}.`
    });
  }
  throw err;
}
```
