#!/usr/bin/env python3
"""
Create a global heat map of language endangerment by UN sub-region.

Uses a white-to-dark-red colour scale keyed to endangerment %,
with labels directly on the map for each sub-region showing name,
percentage, and raw endangered count.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.colorbar import ColorbarBase

ROBINSON_CRS = "+proj=robin +lon_0=0 +datum=WGS84 +units=m +no_defs"

ENDANGERED_STATUSES = {"shifting", "threatened", "moribund", "nearly extinct"}

ISO2_OVERRIDES = {
    "AN": "NL",
}

# Manual label positions (Robinson projected coords) for each UN sub-region.
# Keyed by sub-region name -> (x, y) in metres. Placed at visual centroid.
LABEL_POSITIONS = {
    "Antarctica":               ( 4.5e6, -7.5e6),
    "Australia and New Zealand": (11.5e6, -3.5e6),
    "Caribbean":                (-5.5e6,  2.8e6),
    "Central America":          (-10.0e6,  1.5e6),
    "Central Asia":             ( 5.8e6,  4.5e6),
    "Eastern Africa":            ( 3.4e6, -0.2e6),
    "Eastern Asia":             (10.5e6,  4.0e6),
    "Eastern Europe":            ( 4.5e6,  6.5e6),
    "Melanesia":                 (15.0e6, -1.5e6),
    "Middle Africa":             ( 1.5e6,  0.2e6),
    "Northern Africa":           ( 0.8e6,  2.8e6),
    "Northern America":          (-6.6e6,  5.8e6),
    "Northern Europe":           ( 0.9e6,  6.4e6),

    "South America":             (-5.9e6, -1.7e6),
    "South-Eastern Asia":        (10.3e6,  0.9e6),
    "Southern Africa":           ( 2.3e6, -2.8e6),
    "Southern Asia":             ( 7.0e6,  2.8e6),
    "Southern Europe":          ( 1.2e6,  4.5e6),
    "Western Africa":            (-0.5e6,  1.3e6),
    "Western Asia":              ( 3.8e6,  3.4e6),
    "Western Europe":            (-1.5e6,  5.0e6),
}


def main():
    base_dir = Path(__file__).parent
    csv_path = base_dir / "glottolog_data.csv"
    output_png = base_dir / "endangerment_heatmap.png"
    output_pdf = base_dir / "endangerment_heatmap.pdf"

    # --- Load world boundaries ---
    print("Loading Natural Earth country boundaries...")
    world = gpd.read_file(
        "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
    )
    print(f"Loaded {len(world):,} countries")

    # --- Load and prepare language data ---
    print("Loading language data...")
    df = pd.read_csv(csv_path, low_memory=False)
    langs = df[df["core.level"] == "language"].copy()
    langs["endangerment"] = langs["endangerment.status"].fillna("Unknown")
    langs["endangered"] = langs["endangerment"].isin(ENDANGERED_STATUSES)
    print(f"Found {len(langs):,} languages")

    # Explode country codes
    rows = []
    for _, row in langs.iterrows():
        countries_raw = row.get("core.countries")
        if pd.isna(countries_raw) or str(countries_raw).strip() == "":
            continue
        codes = [c.strip() for c in str(countries_raw).split(" | ") if c.strip()]
        for code in codes:
            code = ISO2_OVERRIDES.get(code, code)
            rows.append({
                "glottocode": row["glottocode"],
                "iso_a2": code,
                "endangerment": row["endangerment"],
                "endangered": row["endangered"],
            })
    ex = pd.DataFrame(rows)
    print(f"Exploded to {len(ex):,} language-country pairs")

    # --- Build region lookup from world shapefile ---
    _lookup_df = world.dropna(subset=["ISO_A2_EH"]).drop_duplicates(subset="ISO_A2_EH")
    region_lookup = {}
    for _, r in _lookup_df.iterrows():
        region_lookup[r["ISO_A2_EH"]] = {
            "REGION_UN": r["REGION_UN"],
            "SUBREGION": r["SUBREGION"],
        }

    # Assign each language-country pair its UN sub-region
    ex["un_region"] = ex["iso_a2"].map(
        lambda c: region_lookup.get(c, {}).get("REGION_UN", "Unknown")
    )
    ex["un_subregion"] = ex["iso_a2"].map(
        lambda c: region_lookup.get(c, {}).get("SUBREGION", "Unknown")
    )

    # --- Aggregate by UN sub-region (deduplicated) ---
    subregion_langs = ex.drop_duplicates(subset=["glottocode", "un_subregion"])
    subregion_stats = (
        subregion_langs.groupby("un_subregion")
        .agg(
            total_languages=("glottocode", "nunique"),
            endangered=("endangered", "sum"),
        )
        .reset_index()
    )
    subregion_stats["endangered"] = subregion_stats["endangered"].astype(int)
    subregion_stats["pct_endangered"] = (
        subregion_stats["endangered"] / subregion_stats["total_languages"] * 100
    ).round(1)

    # Map sub-region stats to each country
    subregion_pct_map = subregion_stats.set_index("un_subregion")["pct_endangered"].to_dict()
    subregion_endangered_map = subregion_stats.set_index("un_subregion")["endangered"].to_dict()
    world["subregion_pct"] = world["SUBREGION"].map(subregion_pct_map)

    # --- Reproject ---
    world_proj = world.to_crs(ROBINSON_CRS)

    # --- Colour scale: light cream (low) -> dark red (high) ---
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "cream_to_red", [
            "#FFF5EB",  # very light cream
            "#FDD2A4",  # light peach
            "#FFA12C",  # orange
            "#F06030",  # red-orange
            "#C4212A",  # dark red
        ]
    )
    norm = mcolors.Normalize(vmin=20, vmax=70)

    # --- Create figure ---
    print("Creating figure...")
    fig = plt.figure(figsize=(22, 12), facecolor="white")
    ax = fig.add_axes([0.02, 0.08, 0.82, 0.78])
    ax.set_facecolor("#D6DCE4")

    # Plot each country coloured by its sub-region's endangerment %
    world_proj.dropna(subset=["subregion_pct"]).plot(
        ax=ax,
        column="subregion_pct",
        cmap=cmap,
        norm=norm,
        edgecolor="white",
        linewidth=0.35,
        zorder=1,
        missing_kwds={"color": "#C7CDD4", "edgecolor": "white", "linewidth": 0.35},
    )

    # Countries with no sub-region data
    no_data = world_proj[world_proj["subregion_pct"].isna()]
    if len(no_data) > 0:
        no_data.plot(
            ax=ax,
            color="#C7CDD4",
            edgecolor="white",
            linewidth=0.35,
            zorder=0,
        )

    ax.set_axis_off()

    # Tight projected bounds
    xmin, ymin, xmax, ymax = world_proj.total_bounds
    ax.set_xlim(xmin - 3e5, xmax + 3e5)
    ax.set_ylim(ymin - 3e5, ymax + 3e5)

    # --- Place sub-region labels on the map ---
    print("Placing sub-region labels...")
    for sr, (lx, ly) in LABEL_POSITIONS.items():
        if sr not in subregion_pct_map:
            continue
        pct = subregion_pct_map[sr]
        endangered = subregion_endangered_map.get(sr, 0)
        face_color = cmap(norm(pct))
        label_text = f"{sr}\n{pct:.0f}% ({endangered:,} endangered)"
        ax.annotate(
            label_text,
            xy=(lx, ly),
            ha="center",
            va="center",
            fontsize=9.1,
            fontweight="bold",
            color="#1F2937",
            zorder=5,
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor="white",
                edgecolor=face_color,
                linewidth=2.0,
                alpha=0.90,
            ),
        )

    # --- Title ---
    fig.text(
        0.43,
        0.91,
        "Language Endangerment by UN Sub-Region",
        ha="center",
        va="top",
        fontsize=20,
        fontweight="bold",
        color="#1F2937",
    )
    fig.text(
        0.43,
        0.88,
        "Percentage of living languages endangered (shifting, threatened, moribund, or nearly extinct)",
        ha="center",
        va="top",
        fontsize=11,
        color="#4B5563",
    )

    # --- Colour bar on the right ---
    cbar_ax = fig.add_axes([0.86, 0.15, 0.015, 0.60])
    cb = ColorbarBase(
        cbar_ax,
        cmap=cmap,
        norm=norm,
        orientation="vertical",
        label="% languages endangered",
    )
    cb.set_ticks([20, 30, 40, 50, 60, 70])
    cb.ax.tick_params(labelsize=8)

    # --- Legend table below ---
    # Build a small sorted table of all sub-regions
    region_order = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
    subregion_stats_sorted = subregion_stats.copy()
    # Add region column for sorting
    sr_to_region = {}
    for _, r in world.dropna(subset=["SUBREGION"]).drop_duplicates("SUBREGION").iterrows():
        sr_to_region[r["SUBREGION"]] = r["REGION_UN"]
    subregion_stats_sorted["region"] = subregion_stats_sorted["un_subregion"].map(sr_to_region)
    subregion_stats_sorted = subregion_stats_sorted.sort_values(
        ["region", "pct_endangered"], ascending=[True, False]
    )

    legend_lines = []
    for reg in region_order:
        subset = subregion_stats_sorted[subregion_stats_sorted["region"] == reg]
        for _, r in subset.iterrows():
            legend_lines.append(
                f"{r['un_subregion']}: {r['pct_endangered']:.1f}% ({int(r['endangered']):,} of {int(r['total_languages']):,})"
            )

    # Place as text block below the map
    legend_text = "  |  ".join(legend_lines)
    fig.text(
        0.43,
        0.03,
        legend_text,
        ha="center",
        va="bottom",
        fontsize=6.5,
        color="#374151",
        wrap=True,
    )

    print(f"Saving PNG to {output_png} ...")
    fig.savefig(output_png, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())

    print(f"Saving PDF to {output_pdf} ...")
    fig.savefig(output_pdf, bbox_inches="tight", facecolor=fig.get_facecolor())

    plt.close(fig)
    print("Done.")


if __name__ == "__main__":
    main()
