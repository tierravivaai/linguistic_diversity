#!/usr/bin/env python3
"""
Create a polished global map of language locations over terrestrial ecoregions,
with language dots colored by endangerment status.

This version:
- reduces left/right whitespace around the map
- adds more space between subtitle and map
- increases marker size by 20%
- increases marker border thickness by 50%
- merges both legends into a single structured panel
- right-aligns the combined legend block
- keeps biome legend in two columns
- aligns legend titles horizontally with each other
- preserves console progress indicators
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

BIOME_COLORS = {
    "Tropical & Subtropical Moist Broadleaf Forests": "#1B5E20",
    "Tropical & Subtropical Dry Broadleaf Forests": "#558B2F",
    "Tropical & Subtropical Coniferous Forests": "#2E7D32",
    "Temperate Broadleaf & Mixed Forests": "#66A61E",
    "Temperate Conifer Forests": "#1F6F50",
    "Boreal Forests/Taiga": "#2C7A7B",
    "Tropical & Subtropical Grasslands, Savannas & Shrublands": "#D4A017",
    "Temperate Grasslands, Savannas & Shrublands": "#B8860B",
    "Flooded Grasslands & Savannas": "#4DB6AC",
    "Montane Grasslands & Shrublands": "#7A7A7A",
    "Tundra": "#B0BEC5",
    "Mediterranean Forests, Woodlands & Scrub": "#8DAA2A",
    "Deserts & Xeric Shrublands": "#E6D3A3",
    "Mangroves": "#00796B",
    "Inland Water": "#4FC3F7",
    "N/A": "#C7CDD4",
}

ROBINSON_CRS = "+proj=robin +lon_0=0 +datum=WGS84 +units=m +no_defs"

BIOME_ORDER = [
    "Tropical & Subtropical Moist Broadleaf Forests",
    "Tropical & Subtropical Dry Broadleaf Forests",
    "Tropical & Subtropical Coniferous Forests",
    "Temperate Broadleaf & Mixed Forests",
    "Temperate Conifer Forests",
    "Boreal Forests/Taiga",
    "Tropical & Subtropical Grasslands, Savannas & Shrublands",
    "Temperate Grasslands, Savannas & Shrublands",
    "Flooded Grasslands & Savannas",
    "Montane Grasslands & Shrublands",
    "Mediterranean Forests, Woodlands & Scrub",
    "Deserts & Xeric Shrublands",
    "Mangroves",
    "Inland Water",
    "Tundra",
    "N/A",
]

ENDANGERMENT_COLORS = {
    "not endangered": "#2ECC40",
    "shifting": "#FFDC00",
    "threatened": "#FF851B",
    "moribund": "#FF4136",
    "nearly extinct": "#B10DC9",
    "extinct": "#2C2C2C",
    "no data": "#AAAAAA",
}

ENDANGERMENT_ORDER = [
    "not endangered",
    "shifting",
    "threatened",
    "moribund",
    "nearly extinct",
    "extinct",
    "no data",
]

ENDANGERMENT_LABELS = {
    "not endangered": "Not endangered",
    "shifting": "Shifting",
    "threatened": "Threatened",
    "moribund": "Moribund",
    "nearly extinct": "Nearly extinct",
    "extinct": "Extinct",
    "no data": "Unknown",
}


def style_panel(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#D1D5DB")
        spine.set_linewidth(0.8)


def main():
    base_dir = Path(__file__).parent
    shapefile_path = base_dir / "Ecoregions2017" / "Ecoregions2017.shp"
    csv_path = base_dir / "glottolog_data.csv"
    output_png = base_dir / "languages_ecoregions_map.png"
    output_pdf = base_dir / "languages_ecoregions_map.pdf"

    print("Loading ecoregions shapefile...")
    ecoregions = gpd.read_file(shapefile_path)
    print(f"Loaded {len(ecoregions):,} ecoregions")

    print("Loading language data...")
    languages = pd.read_csv(csv_path, low_memory=False)

    languages = languages[languages["core.level"] == "language"].copy()
    print(f"Found {len(languages):,} language-level entries")

    languages = languages.dropna(subset=["core.latitude", "core.longitude"]).copy()
    print(f"Found {len(languages):,} languages with valid coordinates")

    languages["endangerment"] = languages["endangerment.status"].fillna("no data")

    languages_gdf = gpd.GeoDataFrame(
        languages,
        geometry=gpd.points_from_xy(
            languages["core.longitude"],
            languages["core.latitude"],
        ),
        crs="EPSG:4326",
    )

    if ecoregions.crs is None:
        raise ValueError("Ecoregions shapefile has no CRS defined.")
    if ecoregions.crs != "EPSG:4326":
        ecoregions = ecoregions.to_crs("EPSG:4326")

    print("Preparing biome colors...")
    ecoregions["plot_color"] = ecoregions["BIOME_NAME"].map(BIOME_COLORS).fillna("#C7CDD4")

    print("Reprojecting layers to Robinson...")
    ecoregions_proj = ecoregions.to_crs(ROBINSON_CRS)
    languages_proj = languages_gdf.to_crs(ROBINSON_CRS)

    print("Building coastline outline...")
    land_outline = ecoregions_proj[["geometry"]].dissolve()

    print("Creating figure...")
    fig = plt.figure(figsize=(20, 12), facecolor="white")

    ax = fig.add_axes([0.005, 0.28, 0.99, 0.63])
    ax.set_facecolor("#F7F8FA")

    print("Plotting ecoregions...")
    ecoregions_proj.plot(
        ax=ax,
        color=ecoregions_proj["plot_color"],
        linewidth=0.0,
        edgecolor="none",
        alpha=0.96,
        zorder=1,
    )

    print("Plotting coastline outline...")
    land_outline.boundary.plot(
        ax=ax,
        color="#7A7A7A",
        linewidth=0.25,
        alpha=0.35,
        zorder=2,
    )

    print("Plotting language markers...")
    for status in ENDANGERMENT_ORDER:
        subset = languages_proj[languages_proj["endangerment"] == status]
        if len(subset) == 0:
            continue

        if status == "no data":
            marker_size = 3.6
            marker_alpha = 0.35
            marker_edgecolor = "none"
            marker_linewidth = 0
        else:
            marker_size = 7.2
            marker_alpha = 0.75
            marker_edgecolor = "white"
            marker_linewidth = 0.225

        subset.plot(
            ax=ax,
            color=ENDANGERMENT_COLORS[status],
            markersize=marker_size,
            alpha=marker_alpha,
            edgecolor=marker_edgecolor,
            linewidth=marker_linewidth,
            zorder=3,
        )

    print("Setting tight projected bounds...")
    xmin, ymin, xmax, ymax = ecoregions_proj.total_bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_axis_off()

    # Title and subtitle
    fig.text(
        0.5,
        0.975,
        "Global Distribution of Languages Overlaid on Terrestrial Ecoregions",
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
        color="#1F2937",
    )

    fig.text(
        0.5,
        0.948,
        f"{len(languages):,} languages coloured by endangerment status across "
        f"{ecoregions['BIOME_NAME'].nunique()} biome classes",
        ha="center",
        va="top",
        fontsize=10,
        color="#4B5563",
    )

    # --------------------------
    # Combined structured legend panel
    # --------------------------
    print("Building combined legend panel...")

    panel_y = 0.060
    panel_h = 0.155
    panel_w = 0.50
    panel_x = (1.0 - panel_w) / 2  # centered

    panel_ax = fig.add_axes([panel_x, panel_y, panel_w, panel_h])
    style_panel(panel_ax)

    # Internal layout within the single legend panel
    left_pad = 0.005
    right_pad = 0.005
    top_title_y = 0.95  # shared title baseline
    legends_top_anchor = 0.82  # shared content baseline under titles (more gap below title)

    biome_x = left_pad
    end_x = 0.75  # push endangerment column further right to clear biome col 2

    # Section titles aligned horizontally
    panel_ax.text(
        biome_x,
        top_title_y,
        "Biome type",
        transform=panel_ax.transAxes,
        ha="left",
        va="top",
        fontsize=13,
        color="#111827",
    )
    panel_ax.text(
        end_x,
        top_title_y,
        "Endangerment status",
        transform=panel_ax.transAxes,
        ha="left",
        va="top",
        fontsize=13,
        color="#111827",
    )

    print("Building biome legend...")
    biome_handles = []
    present_biomes = set(ecoregions["BIOME_NAME"].dropna().unique())
    for biome in BIOME_ORDER:
        if biome in present_biomes:
            biome_handles.append(
                mpatches.Patch(
                    facecolor=BIOME_COLORS.get(biome, "#C7CDD4"),
                    edgecolor="none",
                    label=biome,
                )
            )

    biome_legend = panel_ax.legend(
        handles=biome_handles,
        loc="upper left",
        bbox_to_anchor=(biome_x, legends_top_anchor),
        bbox_transform=panel_ax.transAxes,
        frameon=False,
        ncol=2,
        fontsize=9.4,
        borderaxespad=0.0,
        borderpad=0.2,
        labelspacing=0.30,
        columnspacing=1.5,
        handlelength=1.2,
        handletextpad=0.4,
    )
    biome_legend._legend_box.align = "left"
    panel_ax.add_artist(biome_legend)

    print("Building endangerment legend...")
    end_handles = []
    status_counts = languages["endangerment"].value_counts()
    for status in ENDANGERMENT_ORDER:
        label = ENDANGERMENT_LABELS[status]
        count = status_counts.get(status, 0)
        end_handles.append(
            mpatches.Patch(
                facecolor=ENDANGERMENT_COLORS[status],
                edgecolor="none",
                label=f"{label} ({count:,})",
            )
        )

    end_legend = panel_ax.legend(
        handles=end_handles,
        loc="upper left",
        bbox_to_anchor=(end_x, legends_top_anchor),
        bbox_transform=panel_ax.transAxes,
        frameon=False,
        ncol=1,
        fontsize=9.4,
        borderaxespad=0.0,
        borderpad=0.2,
        labelspacing=0.30,
        handlelength=1.2,
        handletextpad=0.4,
    )
    end_legend._legend_box.align = "left"

    fig.text(
        0.5,
        0.012,
        "Sources: Olson et al. (2001) ecoregions; Glottolog languoid tree data.",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#6B7280",
    )

    print(f"Saving PNG to {output_png} ...")
    fig.savefig(
        output_png,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    print(f"Saving PDF to {output_pdf} ...")
    fig.savefig(
        output_pdf,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)
    print("Done.")


if __name__ == "__main__":
    main()