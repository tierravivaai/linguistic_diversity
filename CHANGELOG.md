# Changelog

All notable changes to this project are documented here.

## [2026-10-13] — Spoken L1 filtering, extinct exclusion, coordinate validation, map improvements

### Changed

- **`scripts/create_language_map_endangerment.py`** — Major filtering and visual updates:
  - **Spoken L1 filter:** Languages are now filtered to Glottolog's "spoken L1 language" classification, matching the count of 7,674 reported on the [Glottolog 5.3 website](https://glottolog.org/glottolog/glottologinformation). This excludes sign languages (227), unclassifiable (128), pidgins (87), unattested (68), artificial languages (31), speech registers (19), mixed languages (4), and bookkeeping entries (380) — all of which sit under non-genealogical trees in the Glottolog classification.
  - **Extinct language exclusion:** 977 extinct spoken L1 languages are excluded to align with Ethnologue's count of living languages. This reduces the count from 7,674 to 6,697.
  - **Coordinate validation:** Two-stage validation added:
    1. Range check: lat/lon must be within ±90/±180 and not at null island (0, 0).
    2. Spatial land check: each point is buffered by 200km in Robinson projection and checked for intersection with ecoregion polygons. This removes 8 languages on remote Pacific atolls (Nauru, Tokelau, Anuta, Kapingamarangi, Nukuoro, Luangiua, Nukumanu, Takuu) whose centroids are >200km from any land in the ecoregions dataset. The 200km buffer accommodates island languages where the centroid may fall just offshore.
  - **Antarctica cropping:** The bottom 12% of the map is cropped to remove Antarctica, which contains no language data.
  - **Larger markers:** Endangered language markers increased from 7.2 to 36 points² with 0.6pt white borders; "no data" markers from 3.6 to 18 points². Diversity map dots from 3.5 to 20 points² with white borders.
  - **Legend layout fixed:** Legend panel height increased from 0.155 to 0.24 to prevent text overflow. Source attribution moved below the panel. Diversity map legend uses 5 columns.
  - **Subtitles updated:** Both maps now specify "spoken L1 languages (non-extinct, land-validated coordinates)" with the exact count.
  - **Source attribution** updated to reference "Glottolog 5.3" specifically.
  - **Final count on map:** 6,688 spoken L1 languages (non-extinct, on or near land, with valid coordinates).

- **`scripts/generate_endangerment_report.py`** — Matching filtering updates:
  - Spoken L1 filter and extinct exclusion applied.
  - Report note updated to explain the filtering criteria and reference Glottolog's spoken L1 count of 7,674.

### Added

- **`.gitignore`** — Excludes `glottolog/` (external repo clone), `.DS_Store`, `*.key` (presentation files), `languages_and_dialects_geo.csv`, and large generated PDFs.
- **`NON_SPOKEN_L1_PREFIXES`** constant in both scripts — list of Glottolog non-genealogical tree glottocodes used for the spoken L1 filter.

### Data

- **Glottolog version:** 5.3 (released 2026-03-02), accessed 22 April 2026 via `https://github.com/glottolog/glottolog`. Latest commit in cloned repo: `3f7b10be` (2026-04-02).
- **Language count breakdown:**
  | Stage | Count |
  |-------|-------|
  | Total language-level entries | 8,618 |
  | Spoken L1 only | 7,674 |
  | After excluding extinct | 6,697 |
  | With valid coordinates | 6,696 |
  | On or near land (200km buffer) | 6,688 |
  | Of which endangered (shifting/threatened/moribund/nearly extinct) | 4,075 (60.8% of 6,697) |

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
