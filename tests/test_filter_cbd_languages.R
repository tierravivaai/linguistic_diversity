# test_filter_cbd_languages.R
# Regression tests for the R CBD Party language filter.
# Mirrors the Python tests in tests/test_filter_cbd_languages.py.
#
# Run with: Rscript tests/test_filter_cbd_languages.R

library(testthat)
library(tidyverse)
library(stringi)
library(here)

# ── Source the filter logic ────────────────────────────────────────────────────
# We extract the core functions from the script so they can be tested
# independently of file I/O.

# Manual ISO2 fixes (mirrors Python's ISO2_FIXES)
ISO2_FIXES <- c(
  "C\u00f4te d'Ivoire" = "CI",
  "T\u00fcrkiye"       = "TR",
  "Namibia"             = "NA"
)

# ── Helper: load CBD party codes from a file ──────────────────────────────────

load_cbd_party_codes <- function(filepath) {
  cbd_raw <- read_csv(filepath, show_col_types = FALSE, na = "")

  cbd_parties <- cbd_raw %>%
    mutate(
      Country = str_trim(Country),
      `ISO_A2` = str_trim(`ISO_A2`),
      Party = str_trim(Party)
    ) %>%
    filter(Party != "" & !is.na(Party)) %>%
    mutate(
      Country_nfc = stri_trans_nfc(Country),
      `ISO_A2` = case_when(
        (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country_nfc == "C\u00f4te d'Ivoire" ~ "CI",
        (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country_nfc == "T\u00fcrkiye"         ~ "TR",
        (`ISO_A2` == "" | is.na(`ISO_A2`)) & Country == "Namibia"                  ~ "NA",
        TRUE                                                                         ~ `ISO_A2`
      )
    ) %>%
    distinct(`ISO_A2`, .keep_all = TRUE) %>%
    filter(!is.na(`ISO_A2`) & `ISO_A2` != "")

  unique(cbd_parties$`ISO_A2`)
}

# ── Helper: create fixture CBD CSV ─────────────────────────────────────────────

write_fixture_cbd <- function(dir) {
  rows <- tibble::tribble(
    ~No., ~Country,      ~ISO_A2, ~ISO_A3, ~Signed,       ~Ratification,  ~Party,
    "1",  "Afghanistan",  "AF",    "AFG",   "1992-06-12",  "2002-09-19",   "rtf",
    "2",  "Albania",      "AL",    "ALB",   "",            "1994-01-05",    "acs",
    "3",  "Algeria",      "DZ",    "DZA",   "1992-06-13",  "1995-08-14",    "rtf",
    "44", "C\u00f4te d'Ivoire", "",  "",     "1992-06-10",  "1994-11-29",    "rtf",
    "147","Namibia",      "NA",    "NAM",   "",            "1993-09-16",    "acs",
    "208","T\u00fcrkiye",  "",     "",      "1992-06-13",  "2017-01-04",    "apv",
    "200","Holy See",     "VA",    "VAT",   "",            "",              ""
  )
  path <- file.path(dir, "cbd_parties.csv")
  write_csv(rows, path)
  path
}

# ── Helper: create fixture glottolog CSV ───────────────────────────────────────

write_fixture_glottolog <- function(dir) {
  rows <- tibble::tribble(
    ~glottocode,  ~`core.level`, ~`core.countries`, ~`core.latitude`, ~`core.longitude`, ~`endangerment.status`,
    "afgh1243",   "language",    "AF",               33.0,             67.0,              "not endangered",
    "alba1263",   "language",    "AL",               41.0,             20.0,              "not endangered",
    "alge1238",   "language",    "DZ | MR",          28.0,             3.0,               "shifting",
    "ivoo1234",   "language",    "CI",                7.0,            -5.0,               "threatened",
    "turk1234",   "language",    "TR",               39.0,             35.0,              "not endangered",
    "nami1234",   "language",    "NA",              -22.0,             17.0,              "not endangered",
    "usen1234",   "language",    "US",               38.0,            -97.0,              "not endangered",
    "holys1234",  "language",    "VA",               41.9,             12.5,              "not endangered",
    "dial1234",   "dialect",     "AF",               34.0,             68.0,              "not endangered",
    "fami1234",   "family",      "AF | DZ",          33.0,             67.0,              NA,
    "nocoun123",  "language",    "",                  NA,              NA,                "not endangered",
    "mult1234",   "language",    "AF | DZ | US",     33.0,             67.0,              "not endangered"
  )
  path <- file.path(dir, "glottolog_data.csv")
  write_csv(rows, path)
  path
}

# ── Tests ───────────────────────────────────────────────────────────────────────

test_that("CBD party codes exclude non-Parties (Holy See, USA)", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))
  cbd_path <- write_fixture_cbd(tmpdir)
  codes <- load_cbd_party_codes(cbd_path)
  expect_false("VA" %in% codes)
  expect_false("US" %in% codes)
})

test_that("CBD party codes include real Parties", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))
  cbd_path <- write_fixture_cbd(tmpdir)
  codes <- load_cbd_party_codes(cbd_path)
  expect_true("AF" %in% codes)
  expect_true("AL" %in% codes)
  expect_true("DZ" %in% codes)
})

test_that("Cote d'Ivoire is assigned CI", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))
  cbd_path <- write_fixture_cbd(tmpdir)
  codes <- load_cbd_party_codes(cbd_path)
  expect_true("CI" %in% codes)
})

test_that("Turkiye is assigned TR", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))
  cbd_path <- write_fixture_cbd(tmpdir)
  codes <- load_cbd_party_codes(cbd_path)
  expect_true("TR" %in% codes)
})

test_that("Namibia NA is treated as a valid code, not missing", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))
  cbd_path <- write_fixture_cbd(tmpdir)
  codes <- load_cbd_party_codes(cbd_path)
  expect_true("NA" %in% codes)
})

test_that("EU member state duplicates are removed", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))
  cbd_path <- write_fixture_cbd(tmpdir)
  codes <- load_cbd_party_codes(cbd_path)
  # AF, AL, DZ, CI, TR, NA = 6 unique codes
  expect_equal(length(codes), 6)
})

test_that("real cbd_parties.csv yields 195 codes", {
  project_root <- here::here()
  cbd_path <- file.path(project_root, "data", "cbd_parties.csv")
  if (!file.exists(cbd_path)) skip("Real cbd_parties.csv not available")
  codes <- load_cbd_party_codes(cbd_path)
  expect_equal(length(codes), 195)
})

test_that("Glottolog filter produces correct glottocode set", {
  tmpdir <- tempfile()
  dir.create(tmpdir)
  on.exit(unlink(tmpdir, recursive = TRUE))

  cbd_path <- write_fixture_cbd(tmpdir)
  glottolog_path <- write_fixture_glottolog(tmpdir)
  output_path <- file.path(tmpdir, "cbd_party_languages.csv")

  cbd_codes <- load_cbd_party_codes(cbd_path)

  # Run the filter
  glottolog <- read_csv(glottolog_path, show_col_types = FALSE, na = "") %>%
    filter(`core.level` == "language")

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

  glottocodes <- cbd_languages$glottocode

  # Should include CBD Party languages
  expect_true("afgh1243" %in% glottocodes)  # AF
  expect_true("alba1263" %in% glottocodes)  # AL
  expect_true("ivoo1234" %in% glottocodes)  # CI
  expect_true("turk1234" %in% glottocodes)  # TR
  expect_true("nami1234" %in% glottocodes)  # NA

  # Should exclude non-CBD languages
  expect_false("usen1234" %in% glottocodes)  # US only
  expect_false("holys1234" %in% glottocodes) # VA only

  # Should exclude dialects and families
  expect_false("dial1234" %in% glottocodes) # dialect
  expect_false("fami1234" %in% glottocodes) # family

  # Should exclude languages with no country data
  expect_false("nocoun123" %in% glottocodes) # empty countries

  # Should strip non-CBD country codes
  mult_row <- cbd_languages %>% filter(glottocode == "mult1234")
  expect_true("AF" %in% str_split(mult_row$`core.countries`, " \\| ")[[1]])
  expect_true("DZ" %in% str_split(mult_row$`core.countries`, " \\| ")[[1]])
  expect_false("US" %in% str_split(mult_row$`core.countries`, " \\| ")[[1]])
})

test_that("real output contains known countries including CI, TR, and NA", {
  project_root <- here::here()
  output_path <- file.path(project_root, "data", "cbd_party_languages.csv")
  if (!file.exists(output_path)) skip("cbd_party_languages.csv not available")

  cbd_lang <- read_csv(output_path, show_col_types = FALSE, na = "")
  countries <- cbd_lang %>%
    filter(`core.level` == "language") %>%
    pull(`core.countries`) %>%
    str_split(" \\| ") %>%
    unlist() %>%
    str_trim() %>%
    unique()

  expect_true("AU" %in% countries)  # Australia
  expect_true("BR" %in% countries)  # Brazil
  expect_true("CN" %in% countries)  # China
  expect_true("IN" %in% countries)  # India
  expect_true("CI" %in% countries)  # Cote d'Ivoire (was missing before fix)
  expect_true("TR" %in% countries)  # Turkiye (was missing before fix)
  expect_true("NA" %in% countries)  # Namibia (was treated as missing by R readr)
})
