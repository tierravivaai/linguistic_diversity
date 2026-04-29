# Extracting Language Data from Glottolog

This repository covers the process for extracting language data from Glottolog, including information about language endangerment, and visualising it by mapping the data onto Ecoregions data from Olson et al. (2001) to create a map of language endangerment by ecoregion and a heatmap of language endangerment by UN sub-region.

## Ecoregions2017

**2017 Ecoregions data** — Global map of terrestrial ecoregions based on ecology (climate, vegetation, biodiversity); provides spatial units to link language data with environmental context. A revised update to Olson et al. (2001) work on ecoregions. This data is not present in this repository due to file size. It can be downloaded from <https://ecoregions.appspot.com>.

## Glottolog

Glottolog is an initiative of the Max Planck Institute for Evolutionary Anthropology, Leipzig. It provides a catalogue of the world's languages, language families, and dialects. It assigns a unique and stable identifier called a Glottocode to units called *languoids*, which cover all families, languages, and dialects. The languoids are organised via a genealogical classification called the Glottolog tree that is based on available historical-comparative research.

More information about Glottolog's development and use of languoids can be found here: <https://glottolog.org/glottolog/glottologinformation>

More information about the references used to compile information about the languoids in Glottolog can be found here: <https://glottolog.org/langdoc/langdocinformation>

Glottolog data is curated in a GitHub repository: <https://github.com/glottolog/glottolog>

## About this repository

Data about Glottolog languoids (languages, dialects, or sub-groups, aka families) is stored in text files (one per languoid) formatted as INI files. The directory tree mirrors the Glottolog classification of languages. This repository provides Python code to extract language data from those INI files into a single CSV file. Further code is provided which maps this data onto Ecoregions.

This repository contains:

-   **extract_glottolog_ini.py** — Pulls the Glottolog GitHub repository if not already present, and extracts languoid data from the INI files into a CSV file called `glottolog_data.csv`.
-   **glottolog_data.csv** — The extracted language data.
-   **create_language_map_endangerment.py** — Creates a map of language endangerment by terrestrial ecoregion. Outputs `languages_ecoregions_map.png` and `languages_ecoregions_map.pdf`.
-   **create_endangerment_heatmap.py** — Creates a heatmap of language endangerment by UN sub-region. Outputs `endangerment_heatmap.png` and `endangerment_heatmap.pdf`.
-   **create_endangerment_heatmap_country.py** — Creates a heatmap of language endangerment at the country level. Outputs `endangerment_heatmap_country.png` and `endangerment_heatmap_country.pdf`.
-   **generate_endangerment_report.py** — Creates a Markdown report on language endangerment. Outputs `endangerment_report.md`.
-   **Outputs/** — Contains all outputs from above scripts


## Notes about Glottolog data

### Coordinates

Glottolog provides a single coordinate for most language-level languoids. These coordinates typically represent an approximate central point, which may correspond to:

-   The geographic centre of speaker populations
-   A historical or documented location
-   A demographic or administrative reference point

Coordinates are compiled from a range of sources, including:

-   WALS (World Atlas of Language Structures)
-   ASJP (Automated Similarity Judgment Program)
-   Ethnologue maps
-   Manual curation and contributions

These coordinates are indicative and should not be treated as precise representations of language distributions. While Glottolog provides a single coordinate for each languoid, it also lists country codes for each country where that language is spoken. More information about the source material for language data can be found on Glottolog.

### Endangerment

Glottolog uses the Agglomerated Endangerment Status (AES) to classify language endangerment. This integrates data from [The Catalogue of Endangered Languages (ELCat)](http://www.endangeredlanguages.com/), [UNESCO Atlas of the World's Languages in Danger](https://www.unesco.org/culture/endangeredlanguages/) and [Ethnologue](https://www.ethnologue.com/).


## Citations

Olson, D. M. et al. (2001). *Terrestrial Ecoregions of the World: A New Map of Life on Earth*. BioScience, 51(11), 933–938. [https://doi.org/10.1641/0006-3568(2001)051[0933:TEOTWA]2.0.CO;2](https://doi.org/10.1641/0006-3568%282001%29051%5B0933:TEOTWA%5D2.0.CO;2)

Dinerstein, E. et al. (2017). *An Ecoregion-Based Approach to Protecting Half the Terrestrial Realm*. BioScience, 67(6), 534–545. <https://doi.org/10.1093/biosci/bix014>

Hammarström, H., Forkel, R., Haspelmath, M., & Bank, S. (2026). *Glottolog 5.3*. Leipzig: Max Planck Institute for Evolutionary Anthropology. <https://doi.org/10.5281/zenodo.18840935>
