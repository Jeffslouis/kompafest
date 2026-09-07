# KompaFest Cruise

Marketing site for KompaFest Cruise. Static HTML, served via GitHub Pages at https://kompafestcruise.com.

- `index.html` — home (hero, Free Cabin Raffle, sponsor teaser, itinerary, etc.)
- `faq.html`, `presale.html`, `sponsor.html`, `ambassador.html`, `music.html` — content pages
- `privacy.html`, `terms.html`, `refund.html`, `raffle-rules.html` — legal
- `images/` — assets (`logo.webp` is the footer mark; the header uses a CSS wordmark)
- `screenshot.py` — local viewport screenshot helper

## Priority-list signups → Google Sheet

The "Join Priority List" popup posts each signup to a Google Apps Script
web app, which appends a row to a Google Sheet you own:
`Timestamp | Email | Source | Page`.

**One-time setup:**

1. Create a new Google Sheet (go to https://sheets.new). Name it, e.g.
   "KompaFest Priority List".
2. In the Sheet: **Extensions → Apps Script**.
3. Delete the sample code and paste:

   ```js
   function doPost(e) {
     var lock = LockService.getScriptLock();
     lock.tryLock(10000);
     try {
       var ss = SpreadsheetApp.getActiveSpreadsheet();
       var sheet = ss.getSheetByName('Signups') || ss.insertSheet('Signups');
       if (sheet.getLastRow() === 0) {
         sheet.appendRow(['Timestamp', 'Email', 'Source', 'Page']);
       }
       var p = (e && e.parameter) || {};
       sheet.appendRow([new Date(), p.email || '', p.source || '', p.page || '']);
       return ContentService.createTextOutput(JSON.stringify({ ok: true }))
         .setMimeType(ContentService.MimeType.JSON);
     } catch (err) {
       return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
         .setMimeType(ContentService.MimeType.JSON);
     } finally {
       lock.releaseLock();
     }
   }
   ```

4. Save (Ctrl/Cmd+S).
5. **Deploy → New deployment**. Click the gear → **Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
6. **Deploy**. Approve the permission prompt (choose your account →
   "Advanced" → "Go to <project> (unsafe)" → Allow — it's your own script).
7. Copy the **Web app URL** (ends in `/exec`).
8. In `index.html`, set `SHEET_ENDPOINT` to that URL (search for
   `REPLACE_WITH_APPS_SCRIPT_URL`), commit, and push.

Open the Sheet any time, or **File → Download → Microsoft Excel (.xlsx)**.

If you ever change the Apps Script, use **Deploy → Manage deployments →
edit → Version: New version** so the same URL keeps working.
