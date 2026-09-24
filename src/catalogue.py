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


# Snapshot files are named prices_<supermarket>_<zone>_<date>.csv. The first
# supermarket in this list is the default one.
SUPERMARKET_NAMES = {"mercadona": "Mercadona", "dia": "Dia", "ahorramas": "Ahorramás"}
DEFAULT_SUPERMARKET = "mercadona"


def snapshot_paths(data_dir: Path = DATA_DIR) -> dict:
    """{supermarket_id: newest prices_*.csv for it} (the date is in the file name)."""
    paths = {}
    for path in sorted(data_dir.glob("prices_*.csv")):
        supermarket = path.name.split("_")[1]
        paths[supermarket] = path  # sorted by name, so the newest date wins
    if not paths:
        raise FileNotFoundError(f"No prices_*.csv file found in {data_dir}")
    return paths


def supermarkets(data_dir: Path = DATA_DIR) -> list:
    """The supermarkets we have prices for, default first."""
    ids = list(snapshot_paths(data_dir))
    ids.sort(key=lambda s: (s != DEFAULT_SUPERMARKET, s))
    return ids


def latest_snapshot_path(data_dir: Path = DATA_DIR, supermarket: str = None) -> Path:
    """Path of the snapshot for one supermarket (the default one when not given)."""
    paths = snapshot_paths(data_dir)
    supermarket = supermarket or supermarkets(data_dir)[0]
    if supermarket not in paths:
        raise KeyError(f"No price snapshot for supermarket '{supermarket}'. Available: {sorted(paths)}")
    return paths[supermarket]


def load_catalogue(path: Path = None, supermarket: str = None) -> dict:
    """Read one supermarket's price snapshot into {ingredient_id: Product}."""
    path = path or latest_snapshot_path(supermarket=supermarket)
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
                piece_grams=float(row.get("piece_grams") or 0),
                product_name=row.get("product_name", ""),
                supermarket=row.get("supermarket", ""),
            )
    return catalogue


def snapshot_info(path: Path = None, supermarket: str = None) -> dict:
    """Supermarket, zone and capture date, shown to the user next to every price."""
    path = path or latest_snapshot_path(supermarket=supermarket)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    first = rows[0]
    return {
        "supermarket": first["supermarket"],
        "name": SUPERMARKET_NAMES.get(first["supermarket"], first["supermarket"].title()),
        "zone": first["zone"],
        "captured_at": first["captured_at"],
        "products": len(rows),
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
