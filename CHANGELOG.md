# Changelog

All notable changes to this project are documented here.

## [2025-06-05b] — Language count per CBD Party

### Added

- **`scripts/cbd_party_language_count.py`** — Python script that counts unique language-level glottocodes per CBD Party country and writes `data/cbd_party_language_count.csv` with columns: `country_name`, `iso_a2`, `iso_a3`, `language_count`.
- **`scripts/cbd_party_language_count.R`** — R equivalent producing identical output.
- **Both scripts** read `cbd_party_languages.csv` and `cbd_parties.csv`, handle missing ISO codes (CI, TR, NA) and EU deduplication consistently with the filter scripts.
- **tests/test_cbd_party_language_count.py** — 6 pytest tests: output exists, 195 countries, correct columns, sorted descending, known countries present, counts consistent with source data.
- **tests/test_cbd_party_language_count.R** — 6 testthat tests mirroring the Python suite.

## [2025-06-05] — Repo reorganisation and filter fixes

### Changed

- **Repo reorganised into standard structure:**
  - Python scripts moved to `scripts/`
  - R scripts moved to `R/`
  - Processed data (`cbd_parties.csv`, `cbd_party_languages.csv`) moved to `data/`
  - Raw data (`glottolog_data.csv`) moved to `data-raw/`
  - Reference PDF moved to `data-raw/`
  - All outputs moved to `outputs/` with an `endangerment/` subfolder for endangerment-specific outputs
  - `Outputs/` renamed to `outputs/` (lowercase)
  - `R/data/cbd_countries.R` moved up to `R/cbd_countries.R`

- **All Python script paths updated** to use `Path(__file__).resolve().parent.parent` as the project root, referencing `data-raw/`, `data/`, and `outputs/` relative to that root.

- **R script (`cbd_countries.R`) paths updated** to reference `data/cbd_party_languages.csv`.

- **`create_language_map_endangerment.py`** now produces two maps:
  1. A language endangerment map (dots coloured by endangerment status) → `outputs/endangerment/languages_ecoregions_map.{png,pdf}`
  2. A simpler linguistic diversity map (red dots over ecoregions) → `outputs/languages_ecoregions_map.{png,pdf}`
  - Both share a single data-loading pass to avoid duplicate I/O.

- **Output directory creation** added to all Python scripts — `mkdir(parents=True, exist_ok=True)` ensures `outputs/endangerment/` is created if missing.

### Fixed

- **CBD Party filter (`filter_cbd_languages.py` and `.R`):**
  - **Missing ISO_A2 codes:** Côte d'Ivoire (CI), Türkiye (TR), and Namibia (NA) had blank or missing ISO_A2 codes in `cbd_parties.csv`. Both scripts now manually assign these codes.
  - **Unicode combining characters:** Türkiye's name in the CSV uses a combining diaeresis (U+0308). The Python script normalises to NFC for matching; the R script uses `stri_trans_nfc()` from the `stringi` package.
  - **R treating "NA" as missing:** R's `readr::read_csv()` converts the string "NA" (Namibia's ISO_A2 code) to R's `NA` missing value. Fixed by using `na = ""` so only empty strings are treated as missing.
  - **EU member state deduplication:** EU member states appear twice in `cbd_parties.csv` (once individually, once under the EU entry). Both scripts now deduplicate by ISO_A2 code.
  - **Language-level filter only:** Both scripts now output only `core.level == "language"` rows, excluding dialects and families. This was already the behaviour of downstream scripts; the filter now enforces it at source.
  - **Result:** Both Python and R scripts now produce identical output — 195 unique ISO_A2 codes and 8,209 language-level glottocodes.

### Added

- **`scripts/filter_cbd_languages.R`** — R equivalent of the Python filter, ensuring both pipelines produce the same `cbd_party_languages.csv`.
- **Pytest test suite** (`tests/test_filter_cbd_languages.py`) — regression tests for the Python filter.
- **testthat test suite** (`tests/testthat/test-filter-cbd-languages.R`) — matching regression tests for the R filter.

### Removed

- No files were deleted; all original files were moved to their new locations.
