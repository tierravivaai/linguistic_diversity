#!/usr/bin/env python3
"""
Filter glottolog_data.csv to keep only languages spoken in CBD Party countries.
- Reads CBD party ISO_A2 codes from cbd_parties2.csv
- For each language in glottolog_data.csv, checks if any country code in core.countries
  matches a CBD Party ISO_A2 code
- Outputs matching rows to cbd_party_languages.csv
"""

import csv
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CBD_FILE = PROJECT_ROOT / "data" / "cbd_parties.csv"
GLOTTOLOG_FILE = PROJECT_ROOT / "data-raw" / "glottolog_data.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "cbd_party_languages.csv"


def load_cbd_party_codes(filepath):
    """Load the set of ISO_A2 codes for CBD Party countries.

    Only includes countries that have actually ratified/acceded to the CBD
    (i.e. have a Party date). Non-Parties like Holy See and USA are excluded.
    """
    codes = set()
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # The last column is the Party date; if empty, the country is not a Party
            party_date = row.get("Party", "").strip()  # last column = Party date
            code = row["ISO_A2"].strip()
            if code and party_date:
                codes.add(code)
    return codes


def filter_glottolog_by_cbd(cbd_codes, glottolog_path, output_path):
    """Filter glottolog rows where any core.countries code is in the CBD set."""
    with open(glottolog_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8", newline="") as fout:

        # Read header to find column indices
        header_line = fin.readline()
        # Use csv reader for proper parsing since some fields contain commas in quotes
        fin.seek(0)

        reader = csv.DictReader(fin)
        header = reader.fieldnames
        countries_col = "core.countries"

        writer = csv.DictWriter(fout, fieldnames=header)
        writer.writeheader()

        kept = 0
        skipped = 0
        for row in reader:
            raw = row.get(countries_col, "") or ""
            # Parse pipe-separated country codes, strip whitespace
            if raw.strip() == "":
                skipped += 1
                continue
            lang_codes = {c.strip() for c in raw.split("|")}
            # Keep if any language country code is a CBD party
            if lang_codes & cbd_codes:
                # Strip non-CBD country codes from core.countries
                filtered_codes = sorted(c.strip() for c in raw.split("|") if c.strip() in cbd_codes)
                row[countries_col] = " | ".join(filtered_codes)
                writer.writerow(row)
                kept += 1
            else:
                skipped += 1

    return kept, skipped


if __name__ == "__main__":
    cbd_codes = load_cbd_party_codes(CBD_FILE)
    print(f"Loaded {len(cbd_codes)} CBD Party ISO_A2 codes")
    print(f"Codes: {sorted(cbd_codes)}")

    kept, skipped = filter_glottolog_by_cbd(cbd_codes, GLOTTOLOG_FILE, OUTPUT_FILE)
    print(f"Kept {kept} languages, skipped {skipped} (not in any CBD Party country)")
    print(f"Output written to {OUTPUT_FILE}")
