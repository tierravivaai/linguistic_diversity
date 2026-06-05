library(tidyverse)
library(janitor)

# confined to CBD parties
# there are multipart strings in the description col that throw a warning (safe to ignore)

cbd_languages <- read_csv("data/cbd_party_languages.csv") %>% 
  janitor::clean_names() %>% 
  separate_rows(core_countries, sep = " \\| ") %>% 
  mutate(core_countries = str_trim(core_countries, side = "both"))

# top ranking is the divider '|' where values were NA so filter out

cbd_languages %>% 
  count(core_countries, sort = TRUE) %>% 
  filter(core_countries != "|")

# write to file in long format
# language per country

cbd_languages %>% 
  filter(core_countries != "|") %>% 
  write_csv("data/cbd_parties_country_by_language.csv")
  



  