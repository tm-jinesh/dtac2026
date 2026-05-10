// Scanner backend — paste into the Apps Script editor of your registrants spreadsheet.
// After saving: Deploy → New deployment → gear icon → Web app
//   Execute as: Me     Who has access: Anyone     → Deploy
// First time it'll ask for permissions — Advanced → Go to (unsafe) → Allow.
// Copy the URL it gives you (ends in /exec) and paste it into the scanner.

const CHECKINS_TAB = 'CheckIns';

function doPost(e) {
  let body;
  try { body = JSON.parse(e.postData.contents); }
  catch (err) { return jsonOut({ ok: false, error: 'Invalid JSON' }); }

  const code = String(body.code || '').trim();
  const name = String(body.name || '').trim();
  const desk = String(body.desk || '').trim();
  if (!code) return jsonOut({ ok: false, error: 'Missing code' });

  const lock = LockService.getDocumentLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(CHECKINS_TAB);
    if (!sheet) {
      sheet = ss.insertSheet(CHECKINS_TAB);
      sheet.appendRow(['Timestamp', 'Code', 'Name', 'Desk']);
      sheet.setFrozenRows(1);
      sheet.getRange('A1:D1').setFontWeight('bold');
    }

    // Already checked in? (case-insensitive)
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      const codes = sheet.getRange(2, 2, lastRow - 1, 1).getValues();
      const upper = code.toUpperCase();
      for (let i = 0; i < codes.length; i++) {
        if (String(codes[i][0]).trim().toUpperCase() === upper) {
          const row = sheet.getRange(i + 2, 1, 1, 4).getValues()[0];
          return jsonOut({
            ok: true, status: 'duplicate',
            firstCheckIn: row[0] instanceof Date ? row[0].toISOString() : String(row[0]),
            firstDesk: String(row[3] || '')
          });
        }
      }
    }

    sheet.appendRow([new Date(), code, name, desk]);
    return jsonOut({ ok: true, status: 'logged' });
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) { return jsonOut({ ok: true, message: 'Scanner backend running' }); }

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
