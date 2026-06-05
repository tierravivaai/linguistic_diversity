#!/usr/bin/env Rscript
# filter_cbd_languages.R
# Filter glottolog_data.csv to keep only languages spoken in the 196 CBD Party countries.
#
# The cbd_parties.csv file contains 224 rows: 196 sovereign Parties (including the EU
# as one Party covering 27 member states), plus non-Parties (Holy See, USA). The EU
# member states appear twice — once under their own entry and once under the EU — so
# we deduplicate by ISO_A2 code. Two rows (Côte d'Ivoire and Türkiye) have blank
# ISO_A2 codes; we manually assign them (CI, TR).
#
# This script produces the same cbd_party_languages.csv as the Python version but
# correctly resolves to the full 196 Parties.

library(tidyverse)
library(janitor)

# ── Paths ──────────────────────────────────────────────────────────────────────

project_root <- here::here()

cbd_file      <- file.path(project_root, "data", "cbd_parties.csv")
glottolog_file <- file.path(project_root, "data-raw", "glottolog_data.csv")
output_file   <- file.path(project_root, "data", "cbd_party_languages.csv")

# ── Manual fixes for rows with missing ISO codes ───────────────────────────────

iso2_fixes <- c(
  "Côte d'Ivoire" = "CI",
  "Türkiye"       = "TR"
)

# ── Load and clean CBD parties ─────────────────────────────────────────────────

cbd_raw <- read_csv(cbd_file, show_col_types = FALSE) %>%
  janitor::clean_names()

cbd_parties <- cbd_raw %>%
  # Only keep rows where Party date is present (i.e. ratified/acceded)
  filter(!is.na(party) & str_trim(party) != "") %>%
  # Fix missing ISO_A2 codes
  mutate(
    iso_a2 = str_trim(iso_a2),
    iso_a2 = if_else(
      iso_a2 == "" | is.na(iso_a2),
      recode(country, !!!iso2_fixes),
      iso_a2
    )
  ) %>%
  # De-duplicate: EU member states appear both individually and under the EU entry
  distinct(iso_a2, .keep_all = TRUE) %>%
  filter(!is.na(iso_a2) & iso_a2 != "") %>%
  select(country, iso_a2, iso_a3, party)

cat(sprintf("Loaded %d CBD Party ISO_A2 codes\n", nrow(cbd_parties)))

# ── Load and filter Glottolog data ─────────────────────────────────────────────

cbd_codes <- unique(cbd_parties$iso_a2)

glottolog <- read_csv(glottolog_file, show_col_types = FALSE) %>%
  # Only language-level entries
  filter(core.level == "language")

cat(sprintf("Found %d language-level entries in Glottolog\n", nrow(glottolog)))

# Explode country codes and keep rows where at least one country is a CBD Party
cbd_languages <- glottolog %>%
  # Split pipe-separated country codes into individual rows
  mutate(
    core_countries_raw = core_countries,
    core_countries_list = str_split(core_countries, "\\s*\\|\\s*")
  ) %>%
  unnest(core_countries_list) %>%
  mutate(iso_a2 = str_trim(core_countries_list)) %>%
  filter(iso_a2 != "") %>%
  # Keep only rows where the country is a CBD Party
  filter(iso_a2 %in% cbd_codes) %>%
  # Rebuild the pipe-separated country string with only CBD Party codes
  group_by(across(-core_countries_list)) %>%
  summarise(
    core_countries = str_c(sort(unique(iso_a2)), collapse = " | "),
    .groups = "drop"
  ) %>%
  ungroup() %>%
  # Remove the temporary columns we added
  select(-core_countries_raw, -iso_a2)

cat(sprintf(
  "Kept %d languages, skipped %d (not in any CBD Party country)\n",
  nrow(cbd_languages),
  nrow(glottolog) - nrow(cbd_languages)
))

# ── Write output ───────────────────────────────────────────────────────────────

write_csv(cbd_languages, output_file)
cat(sprintf("Output written to %s\n", output_file))
