#!/usr/bin/env Rscript
# cbd_party_language_count.R
# Count languages per CBD Party country.
#
# Reads cbd_party_languages.csv and cbd_parties.csv, counts unique
# language-level glottocodes per country, and writes the result to
# data/cbd_party_language_count.csv.
#
# Output columns: country_name, iso_a2, iso_a3, language_count
#
# This produces the same output as the Python version
# (scripts/cbd_party_language_count.py).

library(tidyverse)
library(stringi)

# ── Paths ──────────────────────────────────────────────────────────────────────

project_root <- here::here()

cbd_languages_file <- file.path(project_root, "data", "cbd_party_languages.csv")
cbd_parties_file   <- file.path(project_root, "data", "cbd_parties.csv")
output_file        <- file.path(project_root, "data", "cbd_party_language_count.csv")

# ── Load party lookup (name + ISO_A3 from cbd_parties.csv) ─────────────────────

ISO2_FIXES <- c(
  "C\u00f4te d'Ivoire" = "CI",
  "T\u00fcrkiye"       = "TR",
  "Namibia"             = "NA"
)

cbd_raw <- read_csv(cbd_parties_file, show_col_types = FALSE, na = "")

party_lookup <- cbd_raw %>%
  mutate(
    Country = str_trim(Country),
    `ISO_A2` = str_trim(`ISO_A2`),
    `ISO_A3` = str_trim(`ISO_A3`),
    Party = str_trim(Party),
    Country_nfc = stri_trans_nfc(Country),
    `ISO_A2` = case_when(
      (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country_nfc == "C\u00f4te d'Ivoire" ~ "CI",
      (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country_nfc == "T\u00fcrkiye"         ~ "TR",
      (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country == "Namibia"                  ~ "NA",
      TRUE                                                                         ~ `ISO_A2`
    )
  ) %>%
  filter(Party != "" & !is.na(Party)) %>%
  filter(!is.na(`ISO_A2`) & `ISO_A2` != "") %>%
  distinct(`ISO_A2`, .keep_all = TRUE) %>%
  select(country_name = Country, iso_a2 = `ISO_A2`, iso_a3 = `ISO_A3`)

cat(sprintf("Loaded %d CBD Party countries\n", nrow(party_lookup)))

# ── Count languages per country ────────────────────────────────────────────────

cbd_languages <- read_csv(cbd_languages_file, show_col_types = FALSE, na = "") %>%
  filter(`core.level` == "language") %>%
  select(glottocode, `core.countries`) %>%
  # Explode pipe-separated country codes
  mutate(country_codes = str_split(str_trim(`core.countries`), "\\s*\\|\\s*")) %>%
  unnest(country_codes) %>%
  filter(country_codes != "") %>%
  # Count unique glottocodes per country
  group_by(iso_a2 = country_codes) %>%
  summarise(language_count = n_distinct(glottocode), .groups = "drop")

# ── Join with party lookup and sort ─────────────────────────────────────────────

result <- party_lookup %>%
  inner_join(cbd_languages, by = "iso_a2") %>%
  arrange(desc(language_count), iso_a2)

cat(sprintf("Wrote %d countries\n", nrow(result)))

# ── Write output ───────────────────────────────────────────────────────────────

write_csv(result, output_file)
cat(sprintf("Output written to %s\n", output_file))
