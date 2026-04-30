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
-   **glottolog_data.csv** — The extracted language data in a tabular format. This table contains the full information found in the INI files for each languoid. This includes information about the language, countries where this language is spoken, a single co-ordinate for the language, endangerment status and any available links or sources. To navigate the data structure, it may be helpful to view a sample INI file, which can be found at the bottom of this page.
-   **cbd_parties.csv** - Contains a list of CBD Parties and relevant country codes sourced from https://www.cbd.int/information/parties.shtml This has been expanded to include country codes for all 27 EU member states as of April 2026. This dataset was used to filter `glottolog_data.csv` to produce `cbd_party_languages.csv`.
-   **filter_cbd_languages.py** - The script used to filter `glottolog_data.csv`, removing all languages not spoken in CBD Party countries and all references to non-CBD Parties. The script outputs `cbd_party_languages.csv`.
-   **cbd_party_languages.csv** - Contains only languages found in CBD Party countries. Excludes all other country codes from country data. To navigate the data structure, it may be helpful to view a sample INI file, which can be found at the bottom of this page.
-   **create_language_map_endangerment.py** — Creates a map of language endangerment by terrestrial ecoregion. Outputs `languages_ecoregions_map.png` and `languages_ecoregions_map.pdf`.
-   **create_endangerment_heatmap.py** — Creates a heatmap of language endangerment by UN sub-region. Outputs `endangerment_heatmap.png` and `endangerment_heatmap.pdf`.
-   **create_endangerment_heatmap_country.py** — Creates a heatmap of language endangerment at the country level. Outputs `endangerment_heatmap_country.png` and `endangerment_heatmap_country.pdf`.
-   **generate_endangerment_report.py & generate_endangerment_report_parties_only.py** — Creates a Markdown report on language endangerment. Outputs `endangerment_report.md` or `endangerment_report_parties_only.md`.
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

These coordinates are indicative and should not be treated as precise representations of language distributions. While Glottolog provides a single coordinate (a centroid) for each languoid, it also lists country codes for each country where that language is spoken. More information about the source material for language data can be found on Glottolog.

### Endangerment

Glottolog uses the Agglomerated Endangerment Status (AES) to classify language endangerment. This integrates data from [The Catalogue of Endangered Languages (ELCat)](http://www.endangeredlanguages.com/), [UNESCO Atlas of the World's Languages in Danger](https://www.unesco.org/culture/endangeredlanguages/) and [Ethnologue](https://www.ethnologue.com/).


## Citations

Olson, D. M. et al. (2001). *Terrestrial Ecoregions of the World: A New Map of Life on Earth*. BioScience, 51(11), 933–938. [https://doi.org/10.1641/0006-3568(2001)051[0933:TEOTWA]2.0.CO;2](https://doi.org/10.1641/0006-3568%282001%29051%5B0933:TEOTWA%5D2.0.CO;2)

Dinerstein, E. et al. (2017). *An Ecoregion-Based Approach to Protecting Half the Terrestrial Realm*. BioScience, 67(6), 534–545. <https://doi.org/10.1093/biosci/bix014>

Hammarström, H., Forkel, R., Haspelmath, M., & Bank, S. (2026). *Glottolog 5.3*. Leipzig: Max Planck Institute for Evolutionary Anthropology. <https://doi.org/10.5281/zenodo.18840935>

Harmon, D and Loh, J. 2010. The Index of Linguistic Diversity: A new Quantitative Measure of Trends in the Status of the World’s Languages. Language, Documentation & Conservation, Vol.
4: 97-151 - ILD

## Map Citations

The map component of this repository was inspired by the original ground-breaking collaboration between WWF, Terralingua and UNEP in 2000. We have 
applied the same logic used in that map using the Glottolog data and the Dineretsin 2017 data to create a digital version of the map focusing on
language endangerment by ecoregion. 

Please cite the original map as follows with a link to the original:

WWF International, Terralingua, and UNEP, 2000 Indigenous and Traditional Peoples in the World’s Terrestrial Ecoregions. 
https://terralingua.org/tlshop/maps/indigenous-and-traditional-peoples-in-the-worlds-terrestrial-ecoregions-map/

The map was part of a report by WWF International and TerraLingua that should be cited as follows:

Oviedo, Gonzalo; Maffi, Luisa; Larsen, Peter Bille (2000) Indigenous and traditional peoples of the world and ecoregion conservation: an integrated approach to conserving the world's biological and cultural diversity. WWF International and Terralingua: ISBN 2-88985-247-1

## Convention on Biological Diversity References

The work in this repository is linked to wider work on the Linguistic Diversity Indicator of of the Global Biodiversity Framework

CBD/SBSTTA/26/INF/11 Annex C Linguistic Diversity Indicator Metadata Sheet. Scientific and technical review of the traditional knowledge indicators and their suggested links with the headline, component and complementary indicators of the monitoring framework for the Kunming-Montreal Global Biodiversity Framework* 

Under Decision 16/31 (CBD/COP/DEC/16/31) the Linguistic Diversity Indicator is:

1. A complementary indicator under Goal B - (21.CT.3) Index of Linguistic Diversity
2. A component indicator of Target 21 - (21.CT.1) Index of Linguistic Diversity
3. A component indicator of Target 22 - (22.CT.1) Index of Linguistic Diversity

Previous COP Decisions addressing this indicator are found on page 53 of CBD/SBSTTA/26/INF/11 as follows: decision 7/30, decision 8/15, 
decision 13/28, decision 15/5

## Sample langoid INI Structure

Below is a sample of the INI structure for a single langoid, West Circassian. 

# -*- coding: utf-8 -*-
[core]
name = West Circassian
hid = ady
level = language
iso639-3 = ady
latitude = 44.0
longitude = 39.33
macroareas = 
	Eurasia
countries = 
	IL
	JO
	RU
	SY
	TR
links = 
	[Adyghe](https://lexibank.clld.org/languages/johanssonsoundsymbolic-Adyghe)
	[Adyghe](https://lexibank.clld.org/languages/northeuralex-ady)
	[Adyghe (Abzakh)](https://wals.info/languoid/lect/wals_code_ady)
	[Adyghe (Shapsugh)](https://wals.info/languoid/lect/wals_code_ash)
	[Adyghe (Temirgoy)](https://wals.info/languoid/lect/wals_code_adt)
	https://en.wikipedia.org/wiki/Adyghe_language
	https://phoible.org/languages/adyg1241
	https://www.wikidata.org/entity/Q27776

[sources]
glottolog = 
	**asjp2010:1933**
	**cldf:kumaxov:71**
	**cldf:rogava:kerasheva:66**
	**cldf:rogava:zi:66**
	**hh:d:Loewe:Circassian**
	**hh:d:ParisBatouka:Abzakh**
	**hh:d:Shaov:Adygejsko**
	**hh:d:Txarkaxo:Adygejsko**
	**hh:d:Vodozdokova:Adygejskij**
	**hh:g:JakovlevAshkhamaf:Adygejskogo**
	**hh:g:KumaxovVamling:Circassian**
	**hh:g:RogavaKerasheva:Adygejskogo**
	**hh:g:Smeets:West-Circassian**
	**hh:he:Kosven:Kavkaza:I**
	**hh:hld:Dirr:Kaukasischen**
	**hh:hv:Adelungetal:Mithridates:1**
	**hh:hv:Kumaxov:Adygskix**
	**hh:phon:Mufti:Tscherkessischen**
	**hh:s:Kumaxov:Adygejskij**
	**hh:s:Paris:Abkhaz**
	**hh:s:Paris:Abzakh**
	**hh:s:Paris:Abzakh:PhD**
	**hh:t:Paris:Chapsough**
	**hh:typ:Batouka:Abzakh**
	**hh:typ:Hohlig:Tscherkessischen**
	**hh:w:Gippert:Celebi**
	**mpieva:Hohlig1997Kontaktb**
	**mpieva:Jakovlev1941Grammati**
	**mpieva:Kardanov1955Uryskebe**
	**mpieva:Kumachov1971Slovoizm**
	**mpieva:Kumachov2006rgativno**
	**mpieva:Paris19871995Dictionn**
	**mpieva:Rogave1966Adygabze**
	**mpieva:Smeets1976Septhist**
	**sil16:18356**
	**sil16:21275**
	**sil16:38494**
	**sil16:51198**
	**sil16:51199**

[altnames]
wals = 
	Adyghe (Abzakh)
	Adyghe (Shapsugh)
	Adyghe (Temirgoy)
wals other = 
	Abzakh
	Abzax
	Circassian (West)
ruhlen (1987) = 
	Adyghe
moseley & asher (1994) = 
	Adygh
multitree = 
	Abydh
	Adiga
	Adygei
	Adygey
	Adyghe
	Adyguéen
	Cherkes
	Circassian
	Kiakh
	Kjax
	Lower Circassian
	West Circassian
lexvo = 
	Adigea lingvo [eo]
	Adigece [tr]
	Adigeg [br]
	Adigejski jezik [hr]
	Adigué [ca]
	Adygei [en]
	Adygeische Sprache [de]
	Adygeiska [sv]
	Adygejština [cs]
	Adygen kieli [fi]
	Adygeyska [is]
	Adyghe [en]
	Adyghe language [en]
	Adyguéen [fr]
	Adygų kalba [lt]
	An Adyghe [ga]
	Język adygejski [pl]
	Língua adigue [pt]
	Zimanê adigeyî [ku]
	adyghé [fr]
	Адигейська мова [uk]
	Адигејски јазик [mk]
	Адыг хэлэн [bxr]
	Адыгейский язык [ru]
	Адыгъейаг æвзаг [os]
	אדיגית [he]
	لغة أديغية [ar]
	আদিগে ভাষা [bn]
	ภาษาอะดืยเก [th]
	アディゲ語 [ja]
	阿迪格語 [zh]
	아디게어 [ko]
hhbib_lgcode = 
	Abzakh
	Adygejtsy
	Adyghe
	Circassian
	Tscherkassen
	Tscherkessische
	Tscherkessischen
glottolog = 
	Adyghe

[triggers]
lgcode = 
	shapsugh
	adyghe
	tscherkessischen
	adygskix
	rgativnostb
	adygejskogo
	urys
	adygskich
	turkei
	zor
	cherkesskix
	yazykiv
	abzakh
	sapseg

[identifier]
wals = ady;adt;ash
multitree = ady

[classification]
sub = **hh:hv:Hewitt:NWC**
subrefs = 
	**hh:hv:Hewitt:NWC**

[endangerment]
status = threatened
source = UNESCO
date = 2017-08-19T22:02:46
comment = Adyge (1064-ady) = Vulnerable