# KompaFest Cruise

Marketing site for KompaFest Cruise. Static HTML, served via GitHub Pages at https://kompafestcruise.com.

- `index.html` — home (hero, Free Cabin Raffle, sponsor teaser, itinerary, mailing list)
- `faq.html`, `presale.html`, `sponsor.html`, `ambassador.html`, `music.html` — content pages
- `privacy.html`, `terms.html`, `refund.html`, `raffle-rules.html` — legal
- `images/` — assets (`logo.webp` is the footer mark; the header uses a CSS wordmark)
- `screenshot.py` — local viewport screenshot helper

## Google Sheet: signups + visits

One Google Apps Script web app (URL is `SHEET_ENDPOINT` in `index.html`, and
`EP` in the small tracking `<script>` on every page) writes to two tabs in a
Google Sheet you own:

- **Signups** — `Timestamp | Email | Source | Page` (from the priority
  popup and the "Be first to know" mailing form)
- **Visits** — `Timestamp | Page | Referrer | Returning | Visitor | Screen | Language | User agent`
  (one row the first time each browser session lands on the site)

### Apps Script code

In the Sheet: **Extensions → Apps Script**, replace everything with:

```js
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var p = (e && e.parameter) || {};

    if (p.type === 'visit') {
      var v = ss.getSheetByName('Visits') || ss.insertSheet('Visits');
      if (v.getLastRow() === 0) {
        v.appendRow(['Timestamp', 'Page', 'Referrer', 'Returning', 'Visitor', 'Screen', 'Language', 'User agent']);
      }
      v.appendRow([new Date(), p.page || '', p.ref || '', p.returning || '', p.visitor || '', p.screen || '', p.lang || '', p.ua || '']);
    } else {
      var s = ss.getSheetByName('Signups') || ss.insertSheet('Signups');
      if (s.getLastRow() === 0) {
        s.appendRow(['Timestamp', 'Email', 'Source', 'Page']);
      }
      s.appendRow([new Date(), p.email || '', p.source || '', p.page || '']);
    }

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

Save, then **Deploy → Manage deployments → (pencil / edit) → Version:
*New version* → Deploy**. The web-app URL stays the same.

### First-time deploy (only if starting from scratch)

1. New Google Sheet at https://sheets.new.
2. **Extensions → Apps Script**, paste the code above, Save.
3. **Deploy → New deployment** → gear → **Web app**. Execute as **Me**,
   Who has access **Anyone**. Deploy, approve the permission prompt
   (your account → "Advanced" → "Go to … (unsafe)" → Allow).
4. Copy the **Web app URL** (ends in `/exec`).
5. Put that URL in `index.html` (`SHEET_ENDPOINT`) and in the tracking
   `<script>` (`EP`) at the bottom of every `*.html` file, commit, push.

Open the Sheet any time, or **File → Download → Microsoft Excel (.xlsx)**.

### Notes on visit tracking

- Fires once per browser session (uses `sessionStorage`), so it counts
  visits, not every page view. To log every page view instead, remove the
  `if (sessionStorage.getItem('kf_seen')) return;` guard in the tracking
  script.
- No cookies, no IP address, no third-party analytics — just what the
  browser exposes (page, referrer, screen size, language, user agent) plus
  a random first-party `visitor` id in `localStorage`.
