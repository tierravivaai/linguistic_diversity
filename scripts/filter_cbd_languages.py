#!/usr/bin/env python3
"""
Filter glottolog_data.csv to keep only languages spoken in CBD Party countries.

The cbd_parties.csv file contains 224 rows: 196 CBD Parties (including the EU
as one Party covering 27 member states), plus non-Parties (Holy See, USA).
The EU member states appear twice — once under their own entry and once under
the EU — so we deduplicate by ISO_A2 code. Two rows (Côte d'Ivoire and
Türkiye) have blank ISO_A2 codes; we manually assign them (CI, TR).

This produces the same cbd_party_languages.csv as the R version
(scripts/filter_cbd_languages.R).
"""

import csv
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CBD_FILE = PROJECT_ROOT / "data" / "cbd_parties.csv"
GLOTTOLOG_FILE = PROJECT_ROOT / "data-raw" / "glottolog_data.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "cbd_party_languages.csv"

# Manual fixes for rows with missing ISO_A2 codes in cbd_parties.csv.
# Keys are NFC-normalised country names (the CSV uses combining characters).
ISO2_FIXES = {
    unicodedata.normalize("NFC", "Côte d'Ivoire"): "CI",
    unicodedata.normalize("NFC", "Türkiye"): "TR",
    "Namibia": "NA",
}


def load_cbd_party_codes(filepath):
    """Load the set of ISO_A2 codes for CBD Party countries.

    Only includes countries that have actually ratified/acceded to the CBD
    (i.e. have a Party date). Non-Parties like Holy See and USA are excluded.
    Deduplicates by ISO_A2 code (EU member states appear both individually
    and under the EU entry). Manually assigns codes for rows with blank ISO_A2.
    """
    codes = set()
    seen = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            party_date = row.get("Party", "").strip()
            if not party_date:
                continue  # Not a Party (e.g. Holy See, USA)

            code = row["ISO_A2"].strip()
            country = row["Country"].strip()

            # Fix missing ISO_A2 codes (normalise combining characters for matching)
            if not code:
                country_nfc = unicodedata.normalize("NFC", country)
                if country_nfc in ISO2_FIXES:
                    code = ISO2_FIXES[country_nfc]

            if not code:
                print(f"Warning: no ISO_A2 code for '{country}', skipping")
                continue

            # Deduplicate: EU member states appear both individually and under the EU
            if code in seen:
                continue
            seen[code] = country
            codes.add(code)
    return codes


def filter_glottolog_by_cbd(cbd_codes, glottolog_path, output_path):
    """Filter glottolog rows where any core.countries code is in the CBD set.

    Only includes rows where core.level == "language" (excludes dialects and families).
    """
    with open(glottolog_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8", newline="") as fout:

        fin.seek(0)
        reader = csv.DictReader(fin)
        header = reader.fieldnames
        countries_col = "core.countries"

        writer = csv.DictWriter(fout, fieldnames=header)
        writer.writeheader()

        kept = 0
        skipped = 0
        for row in reader:
            # Only include language-level entries (not dialects or families)
            if row.get("core.level", "") != "language":
                continue
            raw = row.get(countries_col, "") or ""
            if raw.strip() == "":
                skipped += 1
                continue
            lang_codes = {c.strip() for c in raw.split("|")}
            if lang_codes & cbd_codes:
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

    kept, skipped = filter_glottolog_by_cbd(cbd_codes, GLOTTOLOG_FILE, OUTPUT_FILE)
    print(f"Kept {kept} languages, skipped {skipped} (not in any CBD Party country)")
    print(f"Output written to {OUTPUT_FILE}")
