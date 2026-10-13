#!/usr/bin/env python3
"""
Create two global maps of language locations over terrestrial ecoregions:

1. Endangerment map: language dots coloured by endangerment status,
   written to outputs/endangerment/languages_ecoregions_map.{png,pdf}

2. Diversity map: all languages as simple red dots over ecoregions,
   written to outputs/languages_ecoregions_map.{png,pdf}

Both share the same biome colour layer and Robinson projection.

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
from matplotlib.lines import Line2D
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
    "no data": "Endangered (level uncertain)",
}

# Glottolog non-genealogical tree prefixes — languages under these are not
# spoken L1 languages and should be excluded to match Glottolog's own
# "spoken L1 language" count (7,674 as of Glottolog 5.3).
NON_SPOKEN_L1_PREFIXES = [
    "sign1238",   # Sign Language
    "uncl1493",   # Unclassifiable
    "pidg1258",   # Pidgin
    "unat1236",   # Unattested
    "arti1236",   # Artificial Language
    "spee1234",   # Speech Register
    "mixe1287",   # Mixed Language
    "book1242",   # Bookkeeping
]


def style_panel(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor("#D1D5DB")
        spine.set_linewidth(0.8)


def main(
    ecoregions_proj,
    ecoregions,
    land_outline,
    languages,
    languages_proj,
    languages_gdf,
    output_png,
    output_pdf,
):
    print("Creating endangerment figure...")
    print("Creating figure...")
    fig = plt.figure(figsize=(20, 12), facecolor="white")

    ax = fig.add_axes([0.005, 0.30, 0.99, 0.60])
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
            marker_size = 18
            marker_alpha = 0.45
            marker_edgecolor = "white"
            marker_linewidth = 0.4
        else:
            marker_size = 36
            marker_alpha = 0.82
            marker_edgecolor = "white"
            marker_linewidth = 0.6

        subset.plot(
            ax=ax,
            color=ENDANGERMENT_COLORS[status],
            markersize=marker_size,
            alpha=marker_alpha,
            edgecolor=marker_edgecolor,
            linewidth=marker_linewidth,
            zorder=3,
        )

    print("Setting tight projected bounds (cropping Antarctica)...")
    xmin, ymin, xmax, ymax = ecoregions_proj.total_bounds
    # Crop the bottom ~12% to remove Antarctica, which has no language data
    y_range = ymax - ymin
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin + y_range * 0.12, ymax)
    ax.set_axis_off()

    # Title and subtitle
    fig.text(
        0.5,
        0.965,
        "Global Distribution of Languages Overlaid on Terrestrial Ecoregions",
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
        color="#1F2937",
    )

    fig.text(
        0.5,
        0.938,
        f"{len(languages):,} spoken L1 languages (non-extinct, land-validated coordinates) "
        f"coloured by endangerment status across {ecoregions['BIOME_NAME'].nunique()} biome classes",
        ha="center",
        va="top",
        fontsize=10,
        color="#4B5563",
    )

    # --------------------------
    # Combined structured legend panel
    # --------------------------
    print("Building combined legend panel...")

    panel_y = 0.025
    panel_h = 0.24
    panel_w = 0.52
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
        count = status_counts.get(status, 0)
        if count == 0:
            continue
        label = ENDANGERMENT_LABELS[status]
        end_handles.append(
            Line2D(
                [0], [0],
                marker="o",
                color="w",
                markerfacecolor=ENDANGERMENT_COLORS[status],
                markeredgecolor="white",
                markersize=11,
                markeredgewidth=0.8,
                linestyle="None",
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
        labelspacing=0.35,
        handlelength=0.5,
        handletextpad=0.6,
    )
    end_legend._legend_box.align = "left"

    fig.text(
        0.5,
        0.004,
        "Sources: Olson et al. (2001) ecoregions; Glottolog 5.3 languoid tree data.",
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


def create_diversity_map(
    ecoregions_proj,
    ecoregions,
    land_outline,
    languages,
    languages_proj,
    languages_gdf,
    output_png,
    output_pdf,
    project_root,
):
    """Create a simple red-dot map of all languages over ecoregions (no endangerment colouring)."""
    from matplotlib.colors import to_rgba

    LANG_DOT_COLOR = "#C0392B"
    LANG_DOT_ALPHA = 0.65
    LANG_DOT_SIZE = 20
    LANG_DOT_EDGE = "white"
    LANG_DOT_LW = 0.4

    print("Creating diversity (red-dot) figure...")
    fig = plt.figure(figsize=(20, 12), facecolor="white")

    ax = fig.add_axes([0.005, 0.12, 0.99, 0.78])
    ax.set_facecolor("#F7F8FA")

    ecoregions_proj.plot(
        ax=ax,
        color=ecoregions_proj["plot_color"],
        linewidth=0.0,
        edgecolor="none",
        alpha=0.96,
        zorder=1,
    )

    land_outline.boundary.plot(
        ax=ax,
        color="#7A7A7A",
        linewidth=0.25,
        alpha=0.35,
        zorder=2,
    )

    languages_proj.plot(
        ax=ax,
        color=LANG_DOT_COLOR,
        markersize=LANG_DOT_SIZE,
        alpha=LANG_DOT_ALPHA,
        edgecolor=LANG_DOT_EDGE,
        linewidth=LANG_DOT_LW,
        zorder=3,
    )

    xmin, ymin, xmax, ymax = ecoregions_proj.total_bounds
    # Crop the bottom ~12% to remove Antarctica, which has no language data
    y_range = ymax - ymin
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin + y_range * 0.12, ymax)
    ax.set_axis_off()

    fig.text(
        0.5,
        0.955,
        "Global Distribution of Languages Overlaid on Terrestrial Ecoregions",
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
        color="#1F2937",
    )

    fig.text(
        0.5,
        0.928,
        f"{len(languages):,} spoken L1 languages (non-extinct, land-validated coordinates) "
        f"across {ecoregions['BIOME_NAME'].nunique()} biome classes",
        ha="center",
        va="top",
        fontsize=10,
        color="#4B5563",
    )

    # Biome legend panel below the map
    print("Building biome legend panel...")
    panel_y = 0.02
    panel_h = 0.075
    panel_w = 0.92
    panel_x = (1.0 - panel_w) / 2

    panel_ax = fig.add_axes([panel_x, panel_y, panel_w, panel_h])
    style_panel(panel_ax)

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

    lang_handle = mpatches.Patch(
        facecolor=LANG_DOT_COLOR,
        edgecolor="none",
        label=f"Languages ({len(languages):,})",
    )
    biome_handles.append(lang_handle)

    panel_ax.legend(
        handles=biome_handles,
        loc="upper left",
        bbox_to_anchor=(0.005, 0.95),
        bbox_transform=panel_ax.transAxes,
        frameon=False,
        ncol=5,
        fontsize=9,
        borderaxespad=0.0,
        borderpad=0.2,
        labelspacing=0.25,
        columnspacing=1.2,
        handlelength=1.0,
        handletextpad=0.4,
    )

    fig.text(
        0.5,
        0.004,
        "Sources: Olson et al. (2001) ecoregions; Glottolog 5.3 languoid tree data.",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#6B7280",
    )

    print(f"Saving diversity PNG to {output_png} ...")
    fig.savefig(
        output_png,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    print(f"Saving diversity PDF to {output_pdf} ...")
    fig.savefig(
        output_pdf,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )

    plt.close(fig)
    print("Diversity map done.")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    shapefile_path = project_root / "data-raw" / "Ecoregions2017" / "Ecoregions2017.shp"
    csv_path = project_root / "data-raw" / "glottolog_data.csv"

    # Load shared data once
    print("Loading ecoregions shapefile...")
    ecoregions = gpd.read_file(shapefile_path)
    print(f"Loaded {len(ecoregions):,} ecoregions")

    print("Loading language data...")
    languages = pd.read_csv(csv_path, low_memory=False)
    languages = languages[languages["core.level"] == "language"].copy()
    print(f"Found {len(languages):,} language-level entries")

    # Filter to spoken L1 languages only, matching Glottolog's own classification
    # (excludes sign languages, pidgins, unattested, artificial, speech registers,
    # mixed languages, unclassifiable, and bookkeeping entries)
    path_str = languages["path"].astype(str)
    is_non_spoken = path_str.apply(lambda p: any(p.startswith(prefix) for prefix in NON_SPOKEN_L1_PREFIXES))
    languages = languages[~is_non_spoken].copy()
    print(f"After filtering to spoken L1 languages: {len(languages):,} languages")

    # Exclude extinct languages to align with Ethnologue's "living languages" count
    languages = languages[languages["endangerment.status"] != "extinct"].copy()
    print(f"After excluding extinct languages: {len(languages):,} languages")

    languages = languages.dropna(subset=["core.latitude", "core.longitude"]).copy()

    # Validate coordinate ranges (filter out any spurious values)
    lat = languages["core.latitude"]
    lon = languages["core.longitude"]
    valid_coords = (lat >= -90) & (lat <= 90) & (lon >= -180) & (lon <= 180) & ~((lat == 0) & (lon == 0))
    removed = len(languages) - valid_coords.sum()
    if removed > 0:
        print(f"Removing {removed} languages with invalid coordinates (out of range or null island)")
        languages = languages[valid_coords].copy()

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

    # Spatial validation: check which language points fall on or near land.
    # Language coordinates are single centroids, so island languages may have
    # a centroid that falls just offshore. Buffer each point by 200km and check
    # if it intersects any ecoregion polygon. The large buffer accommodates
    # languages on small islands not represented in the ecoregions data.
    print("Validating coordinates against land areas (ecoregion polygons + 200km buffer)...")
    point_buffers = languages_proj.geometry.buffer(200000)  # 200km in metres
    buffered_gdf = gpd.GeoDataFrame(geometry=point_buffers, crs=languages_proj.crs)
    land_join = gpd.sjoin(buffered_gdf, ecoregions_proj[["geometry"]], how="left", predicate="intersects")
    on_land = land_join["index_right"].notna()
    # Deduplicate — sjoin may produce multiple matches per point
    on_land = on_land.groupby(on_land.index).any()
    ocean_count = (~on_land).sum()
    if ocean_count > 0:
        ocean_langs = languages_proj[~on_land]
        print(f"Removing {ocean_count} languages with coordinates in the ocean (>200km from land):")
        for _, r in ocean_langs.iterrows():
            print(f"  {r['core.name']:40s} lat={r['core.latitude']:.4f} lon={r['core.longitude']:.4f}")
        languages = languages[on_land.values].copy()
        languages_gdf = languages_gdf[on_land.values].copy()
        languages_proj = languages_proj[on_land.values].copy()
    print(f"After land validation: {len(languages):,} languages with coordinates on or near land")

    print("Building coastline outline...")
    land_outline = ecoregions_proj[["geometry"]].dissolve()

    # Endangerment map -> outputs/endangerment/
    end_dir = project_root / "outputs" / "endangerment"
    end_dir.mkdir(parents=True, exist_ok=True)
    main(
        ecoregions_proj=ecoregions_proj,
        ecoregions=ecoregions,
        land_outline=land_outline,
        languages=languages,
        languages_proj=languages_proj,
        languages_gdf=languages_gdf,
        output_png=end_dir / "languages_ecoregions_map.png",
        output_pdf=end_dir / "languages_ecoregions_map.pdf",
    )

    # Diversity map (red dots on ecoregions) -> outputs/
    # Do not overwrite existing: languages_ecoregions_map_prev.png
    div_dir = project_root / "outputs"
    div_dir.mkdir(parents=True, exist_ok=True)
    create_diversity_map(
        ecoregions_proj=ecoregions_proj,
        ecoregions=ecoregions,
        land_outline=land_outline,
        languages=languages,
        languages_proj=languages_proj,
        languages_gdf=languages_gdf,
        output_png=div_dir / "languages_ecoregions_map.png",
        output_pdf=div_dir / "languages_ecoregions_map.pdf",
        project_root=project_root,
    )