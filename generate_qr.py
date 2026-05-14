#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "qrcode[pure]",
#   "Pillow",
# ]
# ///
"""Generate QR code PNGs from a participants CSV for ID card printing."""

import argparse
import csv
import sys
from pathlib import Path

import qrcode
from qrcode.image.pure import PyPNGImage


def build_vcard(reg_id: str, full_name: str, phone: str, email: str) -> str:
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{full_name}",
        f"TEL:{phone}",
        f"EMAIL:{email}",
        f"X-APP-ID:{reg_id}",
        "END:VCARD",
    ]
    return "\r\n".join(lines)


def generate_qr(vcard: str, out_path: Path) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=4,
    )
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate QR code PNGs for ID card printing from a participants CSV."
    )
    parser.add_argument("csv_file", help="Path to participants CSV file")
    parser.add_argument(
        "-o", "--output-dir",
        default="qr_codes",
        help="Directory to write QR PNGs into (default: ./qr_codes)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        sys.exit(f"Error: CSV file not found: {csv_path}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        sys.exit("Error: CSV file is empty or has no data rows.")

    generated = 0
    skipped = 0

    for row in rows:
        reg_id = row.get("Registration ID", "").strip()
        first = row.get("First Name", "").strip()
        last = row.get("Last Name", "").strip()
        phone = row.get("Phone", "").strip()
        email = row.get("Email", "").strip()

        if not reg_id:
            print(f"  Skipping row with missing Registration ID: {row}")
            skipped += 1
            continue

        full_name = f"{first} {last}".strip()
        vcard = build_vcard(reg_id, full_name, phone, email)
        out_path = out_dir / f"{reg_id}.png"
        generate_qr(vcard, out_path)
        print(f"  {reg_id}.png  —  {full_name}")
        generated += 1

    print(f"\nDone: {generated} QR codes written to '{out_dir}/'", end="")
    if skipped:
        print(f", {skipped} rows skipped (missing ID)", end="")
    print()


if __name__ == "__main__":
    main()
