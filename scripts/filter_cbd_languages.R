#!/usr/bin/env Rscript
# filter_cbd_languages.R
# Filter glottolog_data.csv to keep only languages spoken in CBD Party countries.
#
# The cbd_parties.csv file contains 224 rows: 196 CBD Parties (including the EU
# as one Party covering 27 member states), plus non-Parties (Holy See, USA).
# The EU member states appear twice — once under their own entry and once under
# the EU — so we deduplicate by ISO_A2 code. Two rows (Cote d'Ivoire and
# Turkiye) have blank ISO_A2 codes; we manually assign them (CI, TR).
#
# This script produces the same cbd_party_languages.csv as the Python version
# (scripts/filter_cbd_languages.py).

library(tidyverse)
library(stringi)

# ── Paths ──────────────────────────────────────────────────────────────────────

project_root <- here::here()

cbd_file       <- file.path(project_root, "data", "cbd_parties.csv")
glottolog_file <- file.path(project_root, "data-raw", "glottolog_data.csv")
output_file    <- file.path(project_root, "data", "cbd_party_languages.csv")

# ── Load CBD parties (no clean_names to preserve original column names) ──────

cbd_raw <- read_csv(cbd_file, show_col_types = FALSE)

# Build the set of CBD Party ISO_A2 codes
cbd_parties <- cbd_raw %>%
  # Trim whitespace from key columns
  mutate(
    Country = str_trim(Country),
    `ISO_A2` = str_trim(`ISO_A2`),
    Party = str_trim(Party)
  ) %>%
  # Only keep rows where Party date is present (i.e. ratified/acceded)
  filter(Party != "" & !is.na(Party)) %>%
  # Fix missing or NA ISO_A2 codes
  # Türkiye has a combining diaeresis (U+0308) making grepl unreliable;
  # we normalise to NFC and do an exact match instead.
  mutate(
    Country_nfc = stri_trans_nfc(Country),
    `ISO_A2` = case_when(
      (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country_nfc == "C\u00f4te d'Ivoire" ~ "CI",
      (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country_nfc == "T\u00fcrkiye"         ~ "TR",
      (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country == "Namibia"                  ~ "NA",
      TRUE                                                                         ~ `ISO_A2`
    )
  ) %>%
  # De-duplicate: EU member states appear both individually and under the EU entry
  distinct(`ISO_A2`, .keep_all = TRUE) %>%
  filter(!is.na(`ISO_A2`) & `ISO_A2` != "")

cbd_codes <- unique(cbd_parties$`ISO_A2`)
cat(sprintf("Loaded %d CBD Party ISO_A2 codes\n", length(cbd_codes)))

# ── Load and filter Glottolog data ─────────────────────────────────────────────

glottolog <- read_csv(glottolog_file, show_col_types = FALSE, na = "") %>%
  filter(`core.level` == "language")

cat(sprintf("Found %d language-level entries in Glottolog\n", nrow(glottolog)))

# For each language, check if any country code in core.countries is a CBD Party.
# Then rebuild core.countries with only CBD Party codes.
cbd_languages <- glottolog %>%
  rowwise() %>%
  mutate(
    .raw_countries = `core.countries`,
    .country_codes = list(str_split(str_trim(.raw_countries), "\\s*\\|\\s*")[[1]]),
    .cbd_codes = list(purrr::keep(.country_codes, ~ .x %in% cbd_codes)),
    .has_cbd = length(.cbd_codes) > 0
  ) %>%
  ungroup() %>%
  filter(.has_cbd) %>%
  mutate(
    `core.countries` = sapply(.cbd_codes, function(codes) {
      str_c(sort(unique(codes)), collapse = " | ")
    })
  ) %>%
  select(-.raw_countries, -.country_codes, -.cbd_codes, -.has_cbd)

skipped <- nrow(glottolog) - nrow(cbd_languages)
cat(sprintf(
  "Kept %d languages, skipped %d (not in any CBD Party country)\n",
  nrow(cbd_languages),
  skipped
))

# ── Write output ───────────────────────────────────────────────────────────────

write_csv(cbd_languages, output_file)
cat(sprintf("Output written to %s\n", output_file))
