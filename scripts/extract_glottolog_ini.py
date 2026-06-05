#!/usr/bin/env python3
"""Clone the glottolog repository from GitHub and extract all md.ini files
from glottolog/languoids/tree into a single CSV."""

import csv
import subprocess
import configparser
import sys
from pathlib import Path

GLOTTOLOG_REPO_URL = "https://github.com/glottolog/glottolog"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
GLOTTOLOG_DIR = PROJECT_ROOT / "glottolog"
TREE_DIR = GLOTTOLOG_DIR / "languoids" / "tree"
OUTPUT_CSV = PROJECT_ROOT / "data-raw" / "glottolog_data.csv"


def ensure_glottolog_repo():
    """Clone or update the glottolog repository."""
    if GLOTTOLOG_DIR.is_dir():
        print(f"Glottolog directory found at {GLOTTOLOG_DIR}, pulling latest changes...")
        try:
            subprocess.run(
                ["git", "-C", str(GLOTTOLOG_DIR), "pull"],
                check=True,
            )
            print("Pull complete.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: git pull failed ({e}). Continuing with existing data.")
    else:
        print(f"Cloning glottolog repository from {GLOTTOLOG_REPO_URL}...")
        try:
            subprocess.run(
                ["git", "clone", GLOTTOLOG_REPO_URL, str(GLOTTOLOG_DIR)],
                check=True,
            )
            print("Clone complete.")
        except FileNotFoundError:
            print("Error: git is not installed or not on PATH.", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error: git clone failed ({e}).", file=sys.stderr)
            sys.exit(1)


def parse_ini_file(filepath):
    """Parse an INI file and return a dict of section.key -> value."""
    config = configparser.ConfigParser(interpolation=None)
    # Allow keys without values and preserve case
    config.optionxform = str
    try:
        config.read(filepath, encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    data = {}
    for section in config.sections():
        for key, value in config.items(section):
            # Normalize multiline values: join with " | "
            normalized = " | ".join(
                line.strip() for line in value.splitlines() if line.strip()
            )
            col_name = f"{section}.{key}"
            data[col_name] = normalized
    return data


def main():
    ensure_glottolog_repo()

    if not TREE_DIR.is_dir():
        print(f"Error: expected directory {TREE_DIR} not found.", file=sys.stderr)
        sys.exit(1)

    # First pass: collect all md.ini files and parse them
    rows = []
    all_keys = set()

    ini_files = sorted(TREE_DIR.rglob("md.ini"))
    print(f"Found {len(ini_files)} md.ini files")

    for ini_path in ini_files:
        # The glottocode is the name of the parent directory
        glottocode = ini_path.parent.name
        # The path relative to tree/ gives the classification hierarchy
        rel_path = ini_path.relative_to(TREE_DIR)
        # Build the parent path (everything between tree/ and the final dir)
        parent_path = str(rel_path.parent)
        if parent_path == ".":
            parent_path = ""

        data = parse_ini_file(str(ini_path))
        if data is None:
            continue

        data["glottocode"] = glottocode
        data["path"] = parent_path

        all_keys.update(data.keys())
        rows.append(data)

    # Sort columns: glottocode and path first, then sorted by section.key
    fixed_cols = ["glottocode", "path"]
    other_cols = sorted(all_keys - set(fixed_cols))
    fieldnames = fixed_cols + other_cols

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            # Fill missing keys with empty string
            for key in fieldnames:
                if key not in row:
                    row[key] = ""
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows with {len(fieldnames)} columns to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
