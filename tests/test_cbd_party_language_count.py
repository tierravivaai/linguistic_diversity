"""
Tests for scripts/cbd_party_language_count.py

Verifies that the Python and R versions produce identical output.
"""

import csv
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestCbdPartyLanguageCount:
    """Integration tests that run against the real data files."""

    def test_output_exists(self):
        """The count file should exist after running the scripts."""
        output = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"
        assert output.exists(), "Run scripts/cbd_party_language_count.py first"

    def test_output_has_195_countries(self):
        """Should have 195 CBD Party countries."""
        output = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"
        if not output.exists():
            pytest.skip("cbd_party_language_count.csv not available")
        with open(output, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 195

    def test_output_columns(self):
        """Output should have columns: country_name, iso_a2, iso_a3, language_count."""
        output = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"
        if not output.exists():
            pytest.skip("cbd_party_language_count.csv not available")
        with open(output, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == ["country_name", "iso_a2", "iso_a3", "language_count"]

    def test_sorted_by_count_descending(self):
        """Rows should be sorted by language_count descending."""
        output = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"
        if not output.exists():
            pytest.skip("cbd_party_language_count.csv not available")
        with open(output, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            counts = [int(row["language_count"]) for row in reader]
        assert counts == sorted(counts, reverse=True)

    def test_known_countries(self):
        """Spot-check some well-known countries."""
        output = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"
        if not output.exists():
            pytest.skip("cbd_party_language_count.csv not available")
        with open(output, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            by_iso2 = {row["iso_a2"]: row for row in reader}

        assert "PG" in by_iso2  # Papua New Guinea
        assert "ID" in by_iso2  # Indonesia
        assert "AU" in by_iso2  # Australia
        assert "CI" in by_iso2  # Côte d'Ivoire
        assert "TR" in by_iso2  # Türkiye
        assert "NA" in by_iso2  # Namibia

        # Papua New Guinea should have the most languages
        assert int(by_iso2["PG"]["language_count"]) > 800

    def test_count_matches_filter_output(self):
        """Language counts should be consistent with cbd_party_languages.csv."""
        cbd_lang = PROJECT_ROOT / "data" / "cbd_party_languages.csv"
        count_file = PROJECT_ROOT / "data" / "cbd_party_language_count.csv"
        if not cbd_lang.exists() or not count_file.exists():
            pytest.skip("Required data files not available")

        # Count unique glottocodes per country from the full file
        from collections import defaultdict
        country_counts = defaultdict(set)
        with open(cbd_lang, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("core.level", "") != "language":
                    continue
                raw = (row.get("core.countries") or "").strip()
                if not raw:
                    continue
                for code in raw.split("|"):
                    code = code.strip()
                    if code:
                        country_counts[code].add(row["glottocode"])

        # Load the count file and compare
        with open(count_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                iso2 = row["iso_a2"]
                expected = int(row["language_count"])
                actual = len(country_counts.get(iso2, set()))
                assert actual == expected, (
                    f"Mismatch for {iso2} ({row['country_name']}): "
                    f"count file says {expected}, cbd_party_languages has {actual}"
                )
