"""Load the price snapshot and decide which ingredients a user may eat.

No AI in this file. Allergies and diets are safety rules, so they are
enforced by code: forbidden ingredients are removed *before* the model
sees the catalogue, and the model's answer is checked again afterwards.
"""

import csv
from pathlib import Path

from src.shopping import Product, euros_to_cents

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Which product diet tags each user diet is allowed to eat.
DIET_ALLOWS = {
    "omnivore": {"vegan", "vegetarian", "fish", "meat"},
    "pescatarian": {"vegan", "vegetarian", "fish"},
    "vegetarian": {"vegan", "vegetarian"},
    "vegan": {"vegan"},
}

# The allergen tags used in data/staples.csv.
KNOWN_ALLERGENS = {
    "gluten", "egg", "milk", "fish", "soy", "peanuts",
    "sesame", "celery", "mustard", "sulphites",
}


def latest_snapshot_path(data_dir: Path = DATA_DIR) -> Path:
    """Return the newest prices_*.csv file (the date is in the file name)."""
    snapshots = sorted(data_dir.glob("prices_*.csv"))
    if not snapshots:
        raise FileNotFoundError(f"No prices_*.csv file found in {data_dir}")
    return snapshots[-1]


def load_catalogue(path: Path = None) -> dict:
    """Read the price snapshot into {ingredient_id: Product}."""
    path = path or latest_snapshot_path()
    catalogue = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            allergens = frozenset(a.strip() for a in row["allergens"].split(",") if a.strip())
            catalogue[row["ingredient_id"]] = Product(
                ingredient_id=row["ingredient_id"],
                name_en=row["name_en"],
                name_es=row["name_es"],
                package_price_cents=euros_to_cents(float(row["package_price_eur"])),
                package_size=float(row["package_size"]),
                package_unit=row["package_unit"],
                category=row["category"],
                diet=row["diet"],
                allergens=allergens,
            )
    return catalogue


def snapshot_info(path: Path = None) -> dict:
    """Supermarket, zone and capture date, shown to the user next to every price."""
    path = path or latest_snapshot_path()
    with open(path, newline="", encoding="utf-8") as f:
        first = next(csv.DictReader(f))
    return {
        "supermarket": first["supermarket"],
        "zone": first["zone"],
        "captured_at": first["captured_at"],
    }


def allowed_catalogue(
    catalogue: dict,
    diet: str = "omnivore",
    allergies: frozenset = frozenset(),
    disliked: frozenset = frozenset(),
) -> dict:
    """Keep only the products this user can eat.

    `disliked` contains ingredient_ids the user does not want.
    """
    if diet not in DIET_ALLOWS:
        raise ValueError(f"Unknown diet '{diet}'. Allowed: {sorted(DIET_ALLOWS)}")
    unknown = set(allergies) - KNOWN_ALLERGENS
    if unknown:
        raise ValueError(f"Unknown allergens {sorted(unknown)}. Allowed: {sorted(KNOWN_ALLERGENS)}")

    return {
        ingredient_id: product
        for ingredient_id, product in catalogue.items()
        if product.diet in DIET_ALLOWS[diet]
        and not (product.allergens & allergies)
        and ingredient_id not in disliked
    }
