# test_cbd_party_language_count.R
# Integration tests for the CBD Party language count script.
# Mirrors tests/test_cbd_party_language_count.py.
#
# Run with: Rscript tests/test_cbd_party_language_count.R

library(testthat)
library(here)

project_root <- here::here()
count_file <- file.path(project_root, "data", "cbd_party_language_count.csv")
cbd_lang_file <- file.path(project_root, "data", "cbd_party_languages.csv")

test_that("Output file exists", {
  skip_if_not(file.exists(count_file), "cbd_party_language_count.csv not available")
  expect_true(file.exists(count_file))
})

test_that("Output has 195 countries", {
  skip_if_not(file.exists(count_file), "cbd_party_language_count.csv not available")
  result <- read_csv(count_file, show_col_types = FALSE, na = "")
  expect_equal(nrow(result), 195)
})

test_that("Output has correct columns", {
  skip_if_not(file.exists(count_file), "cbd_party_language_count.csv not available")
  result <- read_csv(count_file, show_col_types = FALSE, na = "")
  expect_equal(colnames(result), c("country_name", "iso_a2", "iso_a3", "language_count"))
})

test_that("Rows are sorted by language_count descending", {
  skip_if_not(file.exists(count_file), "cbd_party_language_count.csv not available")
  result <- read_csv(count_file, show_col_types = FALSE, na = "")
  counts <- result$language_count
  expect_equal(counts, sort(counts, decreasing = TRUE))
})

test_that("Known countries are present", {
  skip_if_not(file.exists(count_file), "cbd_party_language_count.csv not available")
  result <- read_csv(count_file, show_col_types = FALSE, na = "")
  by_iso2 <- setNames(result$language_count, result$iso_a2)

  expect_true("PG" %in% names(by_iso2))   # Papua New Guinea
  expect_true("ID" %in% names(by_iso2))   # Indonesia
  expect_true("AU" %in% names(by_iso2))   # Australia
  expect_true("CI" %in% names(by_iso2))   # Côte d'Ivoire
  expect_true("TR" %in% names(by_iso2))   # Türkiye
  expect_true("NA" %in% names(by_iso2))   # Namibia

  # Papua New Guinea should have the most languages
  expect_true(by_iso2["PG"] > 800)
})

test_that("Count matches cbd_party_languages.csv", {
  skip_if_not(file.exists(count_file), "cbd_party_language_count.csv not available")
  skip_if_not(file.exists(cbd_lang_file), "cbd_party_languages.csv not available")

  result <- read_csv(count_file, show_col_types = FALSE, na = "")
  cbd_lang <- read_csv(cbd_lang_file, show_col_types = FALSE, na = "") %>%
    filter(`core.level` == "language")

  # Count unique glottocodes per country from full file
  actual_counts <- cbd_lang %>%
    mutate(countries = str_split(str_trim(`core.countries`), "\\s*\\|\\s*")) %>%
    unnest(countries) %>%
    filter(countries != "") %>%
    group_by(iso_a2 = countries) %>%
    summarise(n = n_distinct(glottocode), .groups = "drop")

  # Compare
  for (i in seq_len(nrow(result))) {
    iso2 <- result$iso_a2[i]
    expected <- result$language_count[i]
    actual_row <- actual_counts %>% filter(iso_a2 == !!iso2)
    if (nrow(actual_row) > 0) {
      expect_equal(actual_row$n, expected,
        info = paste0("Mismatch for ", iso2, " (", result$country_name[i], ")"))
    }
  }
})
