#!/usr/bin/env python3
"""Generate a markdown report on language endangerment by country and UN region,
restricted to CBD Party countries only."""

import pandas as pd
from pathlib import Path

# ISO 3166-1 alpha-2 -> (Country Name, UN Region, UN Sub-region)
COUNTRY_REGION_MAP = {
    "AF": ("Afghanistan", "Asia", "Southern Asia"),
    "AL": ("Albania", "Europe", "Southern Europe"),
    "DZ": ("Algeria", "Africa", "Northern Africa"),
    "AD": ("Andorra", "Europe", "Southern Europe"),
    "AO": ("Angola", "Africa", "Sub-Saharan Africa"),
    "AG": ("Antigua and Barbuda", "Americas", "Latin America and the Caribbean"),
    "AR": ("Argentina", "Americas", "Latin America and the Caribbean"),
    "AM": ("Armenia", "Asia", "Western Asia"),
    "AU": ("Australia", "Oceania", "Australia and New Zealand"),
    "AT": ("Austria", "Europe", "Western Europe"),
    "AZ": ("Azerbaijan", "Asia", "Western Asia"),
    "BS": ("Bahamas", "Americas", "Latin America and the Caribbean"),
    "BH": ("Bahrain", "Asia", "Western Asia"),
    "BD": ("Bangladesh", "Asia", "Southern Asia"),
    "BB": ("Barbados", "Americas", "Latin America and the Caribbean"),
    "BY": ("Belarus", "Europe", "Eastern Europe"),
    "BE": ("Belgium", "Europe", "Western Europe"),
    "BZ": ("Belize", "Americas", "Latin America and the Caribbean"),
    "BJ": ("Benin", "Africa", "Sub-Saharan Africa"),
    "BT": ("Bhutan", "Asia", "Southern Asia"),
    "BO": ("Bolivia", "Americas", "Latin America and the Caribbean"),
    "BA": ("Bosnia and Herzegovina", "Europe", "Southern Europe"),
    "BW": ("Botswana", "Africa", "Sub-Saharan Africa"),
    "BR": ("Brazil", "Americas", "Latin America and the Caribbean"),
    "BN": ("Brunei Darussalam", "Asia", "South-eastern Asia"),
    "BG": ("Bulgaria", "Europe", "Eastern Europe"),
    "BF": ("Burkina Faso", "Africa", "Sub-Saharan Africa"),
    "BI": ("Burundi", "Africa", "Sub-Saharan Africa"),
    "CV": ("Cabo Verde", "Africa", "Sub-Saharan Africa"),
    "KH": ("Cambodia", "Asia", "South-eastern Asia"),
    "CM": ("Cameroon", "Africa", "Sub-Saharan Africa"),
    "CA": ("Canada", "Americas", "Northern America"),
    "CF": ("Central African Republic", "Africa", "Sub-Saharan Africa"),
    "TD": ("Chad", "Africa", "Sub-Saharan Africa"),
    "CL": ("Chile", "Americas", "Latin America and the Caribbean"),
    "CN": ("China", "Asia", "Eastern Asia"),
    "CO": ("Colombia", "Americas", "Latin America and the Caribbean"),
    "KM": ("Comoros", "Africa", "Sub-Saharan Africa"),
    "CG": ("Congo", "Africa", "Sub-Saharan Africa"),
    "CD": ("DR Congo", "Africa", "Sub-Saharan Africa"),
    "CR": ("Costa Rica", "Americas", "Latin America and the Caribbean"),
    "CI": ("Cote d'Ivoire", "Africa", "Sub-Saharan Africa"),
    "HR": ("Croatia", "Europe", "Southern Europe"),
    "CU": ("Cuba", "Americas", "Latin America and the Caribbean"),
    "CY": ("Cyprus", "Asia", "Western Asia"),
    "CZ": ("Czechia", "Europe", "Eastern Europe"),
    "DK": ("Denmark", "Europe", "Northern Europe"),
    "DJ": ("Djibouti", "Africa", "Sub-Saharan Africa"),
    "DM": ("Dominica", "Americas", "Latin America and the Caribbean"),
    "DO": ("Dominican Republic", "Americas", "Latin America and the Caribbean"),
    "EC": ("Ecuador", "Americas", "Latin America and the Caribbean"),
    "EG": ("Egypt", "Africa", "Northern Africa"),
    "SV": ("El Salvador", "Americas", "Latin America and the Caribbean"),
    "GQ": ("Equatorial Guinea", "Africa", "Sub-Saharan Africa"),
    "ER": ("Eritrea", "Africa", "Sub-Saharan Africa"),
    "EE": ("Estonia", "Europe", "Northern Europe"),
    "SZ": ("Eswatini", "Africa", "Sub-Saharan Africa"),
    "ET": ("Ethiopia", "Africa", "Sub-Saharan Africa"),
    "FJ": ("Fiji", "Oceania", "Melanesia"),
    "FI": ("Finland", "Europe", "Northern Europe"),
    "FR": ("France", "Europe", "Western Europe"),
    "GA": ("Gabon", "Africa", "Sub-Saharan Africa"),
    "GM": ("Gambia", "Africa", "Sub-Saharan Africa"),
    "GE": ("Georgia", "Asia", "Western Asia"),
    "DE": ("Germany", "Europe", "Western Europe"),
    "GH": ("Ghana", "Africa", "Sub-Saharan Africa"),
    "GR": ("Greece", "Europe", "Southern Europe"),
    "GD": ("Grenada", "Americas", "Latin America and the Caribbean"),
    "GT": ("Guatemala", "Americas", "Latin America and the Caribbean"),
    "GN": ("Guinea", "Africa", "Sub-Saharan Africa"),
    "GW": ("Guinea-Bissau", "Africa", "Sub-Saharan Africa"),
    "GY": ("Guyana", "Americas", "Latin America and the Caribbean"),
    "HT": ("Haiti", "Americas", "Latin America and the Caribbean"),
    "HN": ("Honduras", "Americas", "Latin America and the Caribbean"),
    "HU": ("Hungary", "Europe", "Eastern Europe"),
    "IS": ("Iceland", "Europe", "Northern Europe"),
    "IN": ("India", "Asia", "Southern Asia"),
    "ID": ("Indonesia", "Asia", "South-eastern Asia"),
    "IR": ("Iran", "Asia", "Southern Asia"),
    "IQ": ("Iraq", "Asia", "Western Asia"),
    "IE": ("Ireland", "Europe", "Northern Europe"),
    "IL": ("Israel", "Asia", "Western Asia"),
    "IT": ("Italy", "Europe", "Southern Europe"),
    "JM": ("Jamaica", "Americas", "Latin America and the Caribbean"),
    "JP": ("Japan", "Asia", "Eastern Asia"),
    "JO": ("Jordan", "Asia", "Western Asia"),
    "KZ": ("Kazakhstan", "Asia", "Central Asia"),
    "KE": ("Kenya", "Africa", "Sub-Saharan Africa"),
    "KI": ("Kiribati", "Oceania", "Micronesia"),
    "KP": ("North Korea", "Asia", "Eastern Asia"),
    "KR": ("South Korea", "Asia", "Eastern Asia"),
    "KW": ("Kuwait", "Asia", "Western Asia"),
    "KG": ("Kyrgyzstan", "Asia", "Central Asia"),
    "LA": ("Laos", "Asia", "South-eastern Asia"),
    "LV": ("Latvia", "Europe", "Northern Europe"),
    "LB": ("Lebanon", "Asia", "Western Asia"),
    "LS": ("Lesotho", "Africa", "Sub-Saharan Africa"),
    "LR": ("Liberia", "Africa", "Sub-Saharan Africa"),
    "LY": ("Libya", "Africa", "Northern Africa"),
    "LI": ("Liechtenstein", "Europe", "Western Europe"),
    "LT": ("Lithuania", "Europe", "Northern Europe"),
    "LU": ("Luxembourg", "Europe", "Western Europe"),
    "MG": ("Madagascar", "Africa", "Sub-Saharan Africa"),
    "MW": ("Malawi", "Africa", "Sub-Saharan Africa"),
    "MY": ("Malaysia", "Asia", "South-eastern Asia"),
    "MV": ("Maldives", "Asia", "Southern Asia"),
    "ML": ("Mali", "Africa", "Sub-Saharan Africa"),
    "MT": ("Malta", "Europe", "Southern Europe"),
    "MH": ("Marshall Islands", "Oceania", "Micronesia"),
    "MR": ("Mauritania", "Africa", "Sub-Saharan Africa"),
    "MU": ("Mauritius", "Africa", "Sub-Saharan Africa"),
    "MX": ("Mexico", "Americas", "Latin America and the Caribbean"),
    "FM": ("Micronesia", "Oceania", "Micronesia"),
    "MD": ("Moldova", "Europe", "Eastern Europe"),
    "MC": ("Monaco", "Europe", "Western Europe"),
    "MN": ("Mongolia", "Asia", "Eastern Asia"),
    "ME": ("Montenegro", "Europe", "Southern Europe"),
    "MA": ("Morocco", "Africa", "Northern Africa"),
    "MZ": ("Mozambique", "Africa", "Sub-Saharan Africa"),
    "MM": ("Myanmar", "Asia", "South-eastern Asia"),
    "NA": ("Namibia", "Africa", "Sub-Saharan Africa"),
    "NR": ("Nauru", "Oceania", "Micronesia"),
    "NP": ("Nepal", "Asia", "Southern Asia"),
    "NL": ("Netherlands", "Europe", "Western Europe"),
    "NZ": ("New Zealand", "Oceania", "Australia and New Zealand"),
    "NI": ("Nicaragua", "Americas", "Latin America and the Caribbean"),
    "NE": ("Niger", "Africa", "Sub-Saharan Africa"),
    "NG": ("Nigeria", "Africa", "Sub-Saharan Africa"),
    "MK": ("North Macedonia", "Europe", "Southern Europe"),
    "NO": ("Norway", "Europe", "Northern Europe"),
    "OM": ("Oman", "Asia", "Western Asia"),
    "PK": ("Pakistan", "Asia", "Southern Asia"),
    "PW": ("Palau", "Oceania", "Micronesia"),
    "PA": ("Panama", "Americas", "Latin America and the Caribbean"),
    "PG": ("Papua New Guinea", "Oceania", "Melanesia"),
    "PY": ("Paraguay", "Americas", "Latin America and the Caribbean"),
    "PE": ("Peru", "Americas", "Latin America and the Caribbean"),
    "PH": ("Philippines", "Asia", "South-eastern Asia"),
    "PL": ("Poland", "Europe", "Eastern Europe"),
    "PT": ("Portugal", "Europe", "Southern Europe"),
    "QA": ("Qatar", "Asia", "Western Asia"),
    "RO": ("Romania", "Europe", "Eastern Europe"),
    "RU": ("Russia", "Europe", "Eastern Europe"),
    "RW": ("Rwanda", "Africa", "Sub-Saharan Africa"),
    "KN": ("Saint Kitts and Nevis", "Americas", "Latin America and the Caribbean"),
    "LC": ("Saint Lucia", "Americas", "Latin America and the Caribbean"),
    "VC": ("Saint Vincent and the Grenadines", "Americas", "Latin America and the Caribbean"),
    "WS": ("Samoa", "Oceania", "Polynesia"),
    "SM": ("San Marino", "Europe", "Southern Europe"),
    "ST": ("Sao Tome and Principe", "Africa", "Sub-Saharan Africa"),
    "SA": ("Saudi Arabia", "Asia", "Western Asia"),
    "SN": ("Senegal", "Africa", "Sub-Saharan Africa"),
    "RS": ("Serbia", "Europe", "Southern Europe"),
    "SC": ("Seychelles", "Africa", "Sub-Saharan Africa"),
    "SL": ("Sierra Leone", "Africa", "Sub-Saharan Africa"),
    "SG": ("Singapore", "Asia", "South-eastern Asia"),
    "SK": ("Slovakia", "Europe", "Eastern Europe"),
    "SI": ("Slovenia", "Europe", "Southern Europe"),
    "SB": ("Solomon Islands", "Oceania", "Melanesia"),
    "SO": ("Somalia", "Africa", "Sub-Saharan Africa"),
    "ZA": ("South Africa", "Africa", "Sub-Saharan Africa"),
    "SS": ("South Sudan", "Africa", "Sub-Saharan Africa"),
    "ES": ("Spain", "Europe", "Southern Europe"),
    "LK": ("Sri Lanka", "Asia", "Southern Asia"),
    "SD": ("Sudan", "Africa", "Northern Africa"),
    "SR": ("Suriname", "Americas", "Latin America and the Caribbean"),
    "SE": ("Sweden", "Europe", "Northern Europe"),
    "CH": ("Switzerland", "Europe", "Western Europe"),
    "SY": ("Syria", "Asia", "Western Asia"),
    "TJ": ("Tajikistan", "Asia", "Central Asia"),
    "TZ": ("Tanzania", "Africa", "Sub-Saharan Africa"),
    "TH": ("Thailand", "Asia", "South-eastern Asia"),
    "TL": ("Timor-Leste", "Asia", "South-eastern Asia"),
    "TG": ("Togo", "Africa", "Sub-Saharan Africa"),
    "TO": ("Tonga", "Oceania", "Polynesia"),
    "TT": ("Trinidad and Tobago", "Americas", "Latin America and the Caribbean"),
    "TN": ("Tunisia", "Africa", "Northern Africa"),
    "TR": ("Turkey", "Asia", "Western Asia"),
    "TM": ("Turkmenistan", "Asia", "Central Asia"),
    "TV": ("Tuvalu", "Oceania", "Polynesia"),
    "UG": ("Uganda", "Africa", "Sub-Saharan Africa"),
    "UA": ("Ukraine", "Europe", "Eastern Europe"),
    "AE": ("United Arab Emirates", "Asia", "Western Asia"),
    "GB": ("United Kingdom", "Europe", "Northern Europe"),
    "US": ("United States", "Americas", "Northern America"),
    "UY": ("Uruguay", "Americas", "Latin America and the Caribbean"),
    "UZ": ("Uzbekistan", "Asia", "Central Asia"),
    "VU": ("Vanuatu", "Oceania", "Melanesia"),
    "VE": ("Venezuela", "Americas", "Latin America and the Caribbean"),
    "VN": ("Viet Nam", "Asia", "South-eastern Asia"),
    "YE": ("Yemen", "Asia", "Western Asia"),
    "ZM": ("Zambia", "Africa", "Sub-Saharan Africa"),
    "ZW": ("Zimbabwe", "Africa", "Sub-Saharan Africa"),
    # Territories and special cases
    "AW": ("Aruba", "Americas", "Latin America and the Caribbean"),
    "AX": ("Aland Islands", "Europe", "Northern Europe"),
    "BM": ("Bermuda", "Americas", "Northern America"),
    "BQ": ("Bonaire, Sint Eustatius and Saba", "Americas", "Latin America and the Caribbean"),
    "BV": ("Bouvet Island", "Americas", "Latin America and the Caribbean"),
    "IO": ("British Indian Ocean Territory", "Africa", "Sub-Saharan Africa"),
    "CC": ("Cocos Islands", "Oceania", "Australia and New Zealand"),
    "CK": ("Cook Islands", "Oceania", "Polynesia"),
    "CW": ("Curacao", "Americas", "Latin America and the Caribbean"),
    "CX": ("Christmas Island", "Oceania", "Australia and New Zealand"),
    "EH": ("Western Sahara", "Africa", "Northern Africa"),
    "FK": ("Falkland Islands", "Americas", "Latin America and the Caribbean"),
    "FO": ("Faroe Islands", "Europe", "Northern Europe"),
    "GF": ("French Guiana", "Americas", "Latin America and the Caribbean"),
    "GG": ("Guernsey", "Europe", "Northern Europe"),
    "GI": ("Gibraltar", "Europe", "Southern Europe"),
    "GL": ("Greenland", "Americas", "Northern America"),
    "GP": ("Guadeloupe", "Americas", "Latin America and the Caribbean"),
    "GS": ("South Georgia and the South Sandwich Islands", "Americas", "Latin America and the Caribbean"),
    "GU": ("Guam", "Oceania", "Micronesia"),
    "HK": ("Hong Kong", "Asia", "Eastern Asia"),
    "IM": ("Isle of Man", "Europe", "Northern Europe"),
    "JE": ("Jersey", "Europe", "Northern Europe"),
    "KY": ("Cayman Islands", "Americas", "Northern America"),
    "MF": ("Saint Martin (French)", "Americas", "Latin America and the Caribbean"),
    "MO": ("Macao", "Asia", "Eastern Asia"),
    "MP": ("Northern Mariana Islands", "Oceania", "Micronesia"),
    "MQ": ("Martinique", "Americas", "Latin America and the Caribbean"),
    "MS": ("Montserrat", "Americas", "Latin America and the Caribbean"),
    "NC": ("New Caledonia", "Oceania", "Melanesia"),
    "NF": ("Norfolk Island", "Oceania", "Australia and New Zealand"),
    "NU": ("Niue", "Oceania", "Polynesia"),
    "PF": ("French Polynesia", "Oceania", "Polynesia"),
    "PN": ("Pitcairn", "Oceania", "Polynesia"),
    "PR": ("Puerto Rico", "Americas", "Latin America and the Caribbean"),
    "PS": ("Palestine", "Asia", "Western Asia"),
    "RE": ("Reunion", "Africa", "Sub-Saharan Africa"),
    "SJ": ("Svalbard and Jan Mayen", "Europe", "Northern Europe"),
    "SX": ("Sint Maarten (Dutch)", "Americas", "Latin America and the Caribbean"),
    "TC": ("Turks and Caicos Islands", "Americas", "Northern America"),
    "TF": ("French Southern Territories", "Africa", "Sub-Saharan Africa"),
    "TK": ("Tokelau", "Oceania", "Polynesia"),
    "TW": ("Taiwan", "Asia", "Eastern Asia"),
    "UM": ("United States Minor Outlying Islands", "Oceania", "Micronesia"),
    "VG": ("British Virgin Islands", "Americas", "Latin America and the Caribbean"),
    "VI": ("United States Virgin Islands", "Americas", "Latin America and the Caribbean"),
    "WF": ("Wallis and Futuna", "Oceania", "Polynesia"),
    "YT": ("Mayotte", "Africa", "Sub-Saharan Africa"),
    "SH": ("Saint Helena", "Africa", "Sub-Saharan Africa"),
    "AI": ("Anguilla", "Americas", "Northern America"),
    "BL": ("Saint Barthelemy", "Americas", "Latin America and the Caribbean"),
    "PM": ("Saint Pierre and Miquelon", "Americas", "Northern America"),
    "VA": ("Holy See", "Europe", "Southern Europe"),
}

ENDANGERED_STATUSES = {"shifting", "threatened", "moribund", "nearly extinct"}


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "cbd_party_languages.csv"
    output_dir = project_root / "outputs" / "endangerment"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "endangerment_report_parties_only.md"

    df = pd.read_csv(csv_path, low_memory=False)
    langs = df[df["core.level"] == "language"].copy()
    langs["endangerment"] = langs["endangerment.status"].fillna("Unknown")

    # Explode country codes so one row per language-country pair
    rows = []
    for _, row in langs.iterrows():
        countries_raw = row.get("core.countries")
        if pd.isna(countries_raw) or str(countries_raw).strip() == "":
            continue
        codes = [c.strip() for c in str(countries_raw).split(" | ") if c.strip()]
        for code in codes:
            info = COUNTRY_REGION_MAP.get(code)
            if info:
                rows.append({
                    "glottocode": row["glottocode"],
                    "country_code": code,
                    "country": info[0],
                    "un_region": info[1],
                    "un_subregion": info[2],
                    "endangerment": row["endangerment"],
                    "endangered": row["endangerment"] in ENDANGERED_STATUSES,
                })
            else:
                rows.append({
                    "glottocode": row["glottocode"],
                    "country_code": code,
                    "country": code,
                    "un_region": "Unknown",
                    "un_subregion": "Unknown",
                    "endangerment": row["endangerment"],
                    "endangered": row["endangerment"] in ENDANGERED_STATUSES,
                })

    ex = pd.DataFrame(rows)

    # --- Country-level stats ---
    country_stats = (
        ex.groupby(["country_code", "country", "un_region", "un_subregion"])
        .agg(
            total_languages=("glottocode", "nunique"),
            endangered=("endangered", "sum"),
        )
        .reset_index()
    )
    country_stats["endangered"] = country_stats["endangered"].astype(int)
    country_stats["pct_endangered"] = (
        (country_stats["endangered"] / country_stats["total_languages"] * 100).round(1)
    )
    country_stats = country_stats.sort_values("total_languages", ascending=False)

    # --- UN Region stats (deduplicated by glottocode) ---
    region_langs = ex.drop_duplicates(subset=["glottocode", "un_region"])
    region_stats = (
        region_langs.groupby("un_region")
        .agg(
            total_languages=("glottocode", "nunique"),
            endangered=("endangered", "sum"),
        )
        .reset_index()
    )
    region_stats["endangered"] = region_stats["endangered"].astype(int)
    region_stats["pct_endangered"] = (
        (region_stats["endangered"] / region_stats["total_languages"] * 100).round(1)
    )
    region_stats = region_stats.sort_values("total_languages", ascending=False)

    # --- UN Sub-region stats (deduplicated by glottocode) ---
    subregion_langs = ex.drop_duplicates(subset=["glottocode", "un_subregion"])
    subregion_stats = (
        subregion_langs.groupby(["un_region", "un_subregion"])
        .agg(
            total_languages=("glottocode", "nunique"),
            endangered=("endangered", "sum"),
        )
        .reset_index()
    )
    subregion_stats["endangered"] = subregion_stats["endangered"].astype(int)
    subregion_stats["pct_endangered"] = (
        (subregion_stats["endangered"] / subregion_stats["total_languages"] * 100).round(1)
    )
    subregion_stats = subregion_stats.sort_values("total_languages", ascending=False)

    # --- Endangerment breakdown by UN region (deduplicated) ---
    end_by_region = (
        region_langs.groupby(["un_region", "endangerment"])["glottocode"]
        .nunique()
        .unstack(fill_value=0)
    )
    # Ensure all columns present
    for col in ["not endangered", "shifting", "threatened", "moribund", "nearly extinct", "extinct", "Unknown"]:
        if col not in end_by_region.columns:
            end_by_region[col] = 0
    col_order = ["not endangered", "shifting", "threatened", "moribund", "nearly extinct", "extinct", "Unknown"]
    end_by_region = end_by_region[col_order]
    end_by_region["Total"] = end_by_region.sum(axis=1)
    end_by_region = end_by_region.sort_values("Total", ascending=False)

    # --- Top 30 countries by endangerment count ---
    top_endangered = country_stats.sort_values("endangered", ascending=False).head(30)

    # --- Build report ---
    lines = []
    lines.append("# Language Endangerment Report — CBD Parties Only")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    total_unique = langs["glottocode"].nunique()
    langs_with_coords = langs.dropna(subset=["core.latitude", "core.longitude"]).shape[0]
    total_endangered = langs[langs["endangerment"].isin(ENDANGERED_STATUSES)].shape[0]
    lines.append(f"- **Total languages in dataset:** {total_unique:,}")
    lines.append(f"- **Languages with coordinates:** {langs_with_coords:,}")
    lines.append(f"- **Languages with country data:** {ex['glottocode'].nunique():,}")
    lines.append(f"- **Endangered languages** (shifting, threatened, moribund, or nearly extinct): {total_endangered:,} ({total_endangered/total_unique*100:.1f}%)")
    lines.append("")
    lines.append("This report covers only languages spoken in CBD Party countries "
                 "(non-Parties such as the Holy See and the United States are excluded).")
    lines.append("")
    lines.append("Note: A language spoken in multiple countries is counted once per country. "
                 "Therefore country-level totals sum to more than the total number of unique languages.")
    lines.append("")

    lines.append("## Endangerment Status by UN Region")
    lines.append("")
    lines.append("| UN Region | Not endangered | Shifting | Threatened | Moribund | Nearly extinct | Extinct | Unknown | Total |")
    lines.append("|-----------|---------------|----------|------------|----------|----------------|---------|---------|-------|")
    for region in end_by_region.index:
        r = end_by_region.loc[region]
        lines.append(
            f"| {region} | {int(r['not endangered']):,} | {int(r['shifting']):,} | "
            f"{int(r['threatened']):,} | {int(r['moribund']):,} | {int(r['nearly extinct']):,} | "
            f"{int(r['extinct']):,} | {int(r['Unknown']):,} | {int(r['Total']):,} |"
        )
    lines.append("")

    lines.append("## UN Region Summary")
    lines.append("")
    lines.append("| UN Region | Total languages | Endangered | % Endangered |")
    lines.append("|-----------|----------------|------------|--------------|")
    for _, r in region_stats.iterrows():
        lines.append(f"| {r['un_region']} | {r['total_languages']:,} | {r['endangered']:,} | {r['pct_endangered']:.1f}% |")
    lines.append("")

    lines.append("## UN Sub-region Summary")
    lines.append("")
    lines.append("| UN Region | UN Sub-region | Total languages | Endangered | % Endangered |")
    lines.append("|-----------|--------------|----------------|------------|--------------|")
    for _, r in subregion_stats.iterrows():
        lines.append(f"| {r['un_region']} | {r['un_subregion']} | {r['total_languages']:,} | {r['endangered']:,} | {r['pct_endangered']:.1f}% |")
    lines.append("")

    lines.append("## Top 30 Countries by Number of Endangered Languages")
    lines.append("")
    lines.append("| # | Country | Total languages | Endangered | % Endangered | UN Region | UN Sub-region |")
    lines.append("|---|---------|----------------|------------|--------------|-----------|--------------|")
    for i, (_, r) in enumerate(top_endangered.iterrows(), 1):
        lines.append(
            f"| {i} | {r['country']} | {r['total_languages']:,} | {r['endangered']:,} | "
            f"{r['pct_endangered']:.1f}% | {r['un_region']} | {r['un_subregion']} |"
        )
    lines.append("")

    lines.append("## All Countries — Languages and Endangerment")
    lines.append("")
    lines.append("| # | Country | Total languages | Endangered | % Endangered | UN Region | UN Sub-region |")
    lines.append("|---|---------|----------------|------------|--------------|-----------|--------------|")
    for i, (_, r) in enumerate(country_stats.iterrows(), 1):
        lines.append(
            f"| {i} | {r['country']} | {r['total_languages']:,} | {r['endangered']:,} | "
            f"{r['pct_endangered']:.1f}% | {r['un_region']} | {r['un_subregion']} |"
        )
    lines.append("")

    report = "\n".join(lines)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
