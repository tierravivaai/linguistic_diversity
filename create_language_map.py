#!/usr/bin/env python3
"""
Overlay language/dialect coordinates on ecoregions map.

This script reads the Ecoregions2017 shapefile and overlays it with
language/dialect coordinates from languages_and_dialects_geo.csv.
Ecoregions are colored by biome type with a legend.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import numpy as np


# Intuitive color palette for biomes - rainforests dark green, deserts sand
BIOME_COLORS = {
    "Tropical & Subtropical Moist Broadleaf Forests": "#064E3B",  # Dark rainforest green
    "Tropical & Subtropical Dry Broadleaf Forests": "#065F46",    # Forest green
    "Tropical & Subtropical Coniferous Forests": "#14532D",       # Evergreen
    "Temperate Broadleaf & Mixed Forests": "#15803D",           # Standard forest green
    "Temperate Conifer Forests": "#166534",                     # Pine green
    "Boreal Forests/Taiga": "#065F46",                          # Dark boreal
    "Tropical & Subtropical Grasslands, Savannas & Shrublands": "#CA8A04",  # Golden savanna
    "Temperate Grasslands, Savannas & Shrublands": "#A16207",     # Prairie gold
    "Flooded Grasslands & Savannas": "#0D9488",                  # Teal wetland
    "Montane Grasslands & Shrublands": "#525252",                # Gray alpine
    "Tundra": "#94A3B8",                                         # Icy blue-gray
    "Mediterranean Forests, Woodlands & Scrub": "#65A30D",       # Olive/maquis
    "Deserts & Xeric Shrublands": "#D4B996",                     # Sand/beige
    "Mangroves": "#0369A1",                                      # Coastal blue
    "Inland Water": "#0891B2",                                   # Water blue
    "N/A": "#9CA3AF"                                             # Gray
}


def shorten_biome_name(name, max_len=30):
    """Shorten biome name for legend display."""
    if len(name) <= max_len:
        return name
    return name[:max_len-3] + "..."


def main():
    # Paths
    base_dir = Path(__file__).parent
    shapefile_path = base_dir / "Ecoregions2017" / "Ecoregions2017.shp"
    csv_path = base_dir / "languages_and_dialects_geo.csv"
    output_path = base_dir / "languages_ecoregions_map.png"

    print("Loading ecoregions shapefile...")
    ecoregions = gpd.read_file(shapefile_path)
    print(f"Loaded {len(ecoregions)} ecoregions")

    print("Loading language coordinates...")
    languages = pd.read_csv(csv_path)
    print(f"Loaded {len(languages)} languages/dialects")

    # Filter to only entries with valid coordinates
    languages_with_coords = languages.dropna(subset=["latitude", "longitude"])
    print(f"Found {len(languages_with_coords)} entries with valid coordinates")

    # Create GeoDataFrame from language coordinates
    languages_gdf = gpd.GeoDataFrame(
        languages_with_coords,
        geometry=gpd.points_from_xy(
            languages_with_coords.longitude,
            languages_with_coords.latitude
        ),
        crs="EPSG:4326"
    )

    # Reproject ecoregions to match language CRS if needed
    if ecoregions.crs != languages_gdf.crs:
        ecoregions = ecoregions.to_crs(languages_gdf.crs)

    print("Processing biome colors...")
    # Assign colors to ecoregions based on biome
    ecoregions["color"] = ecoregions["BIOME_NAME"].map(
        lambda x: BIOME_COLORS.get(x, "#999999")
    )

    print("Creating map...")
    # Create figure with high resolution and sleek styling
    fig, ax = plt.subplots(figsize=(24, 14), facecolor="#f5f5f5")
    ax.set_facecolor("#fafafa")

    # Plot ecoregions by biome with custom colors
    for _, row in ecoregions.iterrows():
        gpd.GeoSeries([row.geometry]).plot(
            ax=ax,
            color=row["color"],
            edgecolor="#333333",
            linewidth=0.15,
            alpha=0.85
        )

    # Plot language points with larger markers
    languages_gdf.plot(
        ax=ax,
        color="#d32f2f",
        markersize=15,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.4
    )

    # Set axis properties for sleek look
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_aspect("equal")
    ax.axis("off")

    # Add title with sleek typography
    title = ax.set_title(
        "Global Distribution of Languages Overlaid on Terrestrial Ecoregions",
        fontsize=18,
        fontweight="bold",
        color="#212121",
        pad=20
    )
    ax.text(
        0.5, 0.98,
        f"Showing {len(languages_with_coords):,} language locations across {ecoregions['BIOME_NAME'].nunique()} major biomes",
        transform=ax.transAxes,
        ha="center",
        fontsize=11,
        color="#555555",
        style="italic"
    )

    # Create biome legend
    legend_elements = []
    for biome, color in sorted(BIOME_COLORS.items()):
        if biome in ecoregions["BIOME_NAME"].values:
            legend_elements.append(
                mpatches.Patch(
                    facecolor=color,
                    edgecolor="#333333",
                    linewidth=0.5,
                    label=shorten_biome_name(biome),
                    alpha=0.85
                )
            )

    # Place legend on the bottom left
    legend = ax.legend(
        handles=legend_elements,
        loc="lower left",
        bbox_to_anchor=(0.01, 0.01),
        frameon=True,
        fancybox=True,
        shadow=True,
        fontsize=11,
        title="Biome Types",
        title_fontsize=13,
        borderpad=1.5,
        markerscale=1.5
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.95)

    # Add scale indicator
    ax.annotate(
        "● Language Location",
        xy=(0.99, 0.02),
        xycoords="axes fraction",
        ha="right",
        fontsize=9,
        color="#d32f2f",
        fontweight="bold"
    )

    # Add source credit at bottom
    fig.text(
        0.99, 0.01,
        "Data: Olson et al. 2001 (Ecoregions), Glottolog (Languages)",
        ha="right",
        fontsize=8,
        color="#777777",
        style="italic"
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="#f5f5f5")
    print(f"Map saved to: {output_path}")


if __name__ == "__main__":
    main()
