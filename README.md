# DTAC 2026 – QR Check-In Scanner

A QR-code check-in system for the Toastmasters District Annual Contest (DTAC 2026). Volunteers scan attendee QR codes against a CSV registrations list, with optional real-time logging to Google Sheets.

---

## Running the scanner

The app is a single static HTML page with no build step. Serve it from the repo root:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

> Opening `index.html` via `file://` won't work — browsers block local file fetches, so `registrations.csv` won't load.

---

## Generating QR codes for ID cards

`generate_qr.py` reads a participants CSV and writes one QR PNG per attendee. Each QR encodes a vCard containing the registration ID, so the scanner can identify attendees without network access.

### Requirements

[uv](https://docs.astral.sh/uv/) — the script declares its own dependencies inline (PEP 723), so `uv run` handles everything automatically with no manual install.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Usage

```bash
uv run generate_qr.py <csv_file> [-o <output_dir>]
```

| Argument | Default | Description |
|---|---|---|
| `csv_file` | _(required)_ | Path to the participants CSV |
| `-o / --output-dir` | `./qr_codes` | Directory to write the PNG files into |

### CSV format

The script expects columns: `Registration ID`, `First Name`, `Last Name`, `Phone`, `Email`.

```csv
Registration ID,First Name,Last Name,Phone,Email
REG001,Jane,Smith,+60123456789,jane@example.com
```

### Example

```bash
# Write PNGs to ./qr_codes/ (default)
uv run generate_qr.py participants.csv

# Write PNGs to a custom directory
uv run generate_qr.py participants.csv -o ./qr_codes_paid
```

Output:

```
  REG001.png  —  Jane Smith
  REG002.png  —  John Doe
  ...
Done: 42 QR codes written to 'qr_codes/'
```

---

## Deploying the Google Sheets backend (optional)

1. Open the registrants Google Spreadsheet → **Extensions → Apps Script**.
2. Paste the contents of `google_app_script.js`, save.
3. **Deploy → New deployment → Web app** — Execute as: Me, Who has access: Anyone → Deploy.
4. Copy the `/exec` URL into the scanner's setup screen.

Check-ins work offline without this configured; backend sync is optional and fails gracefully.
