#!/usr/bin/env python3
"""
Count languages per CBD Party country.

Reads cbd_party_languages.csv and cbd_parties.csv, counts unique language-level
glottocodes per country, and writes the result to data/cbd_party_language_count.csv.

Output columns: country_name, iso_a2, iso_a3, language_count

This produces the same output as the R version (scripts/cbd_party_language_count.R).
"""

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CBD_LANGUAGES_FILE = PROJECT_ROOT / "data" / "cbd_party_languages.csv"
CBD_PARTIES_FILE = PROJECT_ROOT / "data" / "cbd_parties.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"


def load_party_lookup(filepath):
    """Load a dict mapping ISO_A2 -> (country_name, ISO_A3) from cbd_parties.csv.

    Handles Unicode combining characters, missing ISO_A2 codes (CI, TR, NA),
    and strips whitespace from all fields. Deduplicates by ISO_A2.
    """
    import unicodedata

    ISO2_FIXES = {
        unicodedata.normalize("NFC", "Côte d'Ivoire"): "CI",
        unicodedata.normalize("NFC", "Türkiye"): "TR",
        "Namibia": "NA",
    }

    lookup = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            party_date = (row.get("Party") or "").strip()
            if not party_date:
                continue

            code = (row.get("ISO_A2") or "").strip()
            country = (row.get("Country") or "").strip()
            iso_a3 = (row.get("ISO_A3") or "").strip()

            if not code:
                country_nfc = unicodedata.normalize("NFC", country)
                if country_nfc in ISO2_FIXES:
                    code = ISO2_FIXES[country_nfc]

            if not code:
                continue

            if code not in lookup:
                lookup[code] = (country, iso_a3)

    return lookup


def count_languages_per_party(cbd_languages_path, party_lookup):
    """Count unique language-level glottocodes per CBD Party ISO_A2 code."""
    counts = {}
    with open(cbd_languages_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("core.level", "") != "language":
                continue
            raw = (row.get("core.countries") or "").strip()
            if not raw:
                continue
            codes = {c.strip() for c in raw.split("|") if c.strip()}
            for code in codes:
                if code in party_lookup:
                    counts[code] = counts.get(code, 0) + 1

    return counts


def main():
    party_lookup = load_party_lookup(CBD_PARTIES_FILE)
    counts = count_languages_per_party(CBD_LANGUAGES_FILE, party_lookup)

    # Build output rows sorted by language count descending
    rows = []
    for code, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        country_name, iso_a3 = party_lookup[code]
        rows.append({
            "country_name": country_name,
            "iso_a2": code,
            "iso_a3": iso_a3,
            "language_count": count,
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["country_name", "iso_a2", "iso_a3", "language_count"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} countries to {OUTPUT_FILE}")
    total_languages = sum(counts.values())
    print(f"Total language-country pairs: {total_languages}")


if __name__ == "__main__":
    main()
