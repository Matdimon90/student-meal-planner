"""Calories and protein per plate. No AI in this file.

The model aims for the user's portion and protein targets, but it never
reports the numbers: the code adds them up from data/nutrition.csv, the same
way it adds up prices. The values are typical ones for the raw product as
sold (see data/README.md), so the result is an estimate, not a label.
"""

import csv
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def load_nutrition(path: Path = DATA_DIR / "nutrition.csv") -> dict:
    """{ingredient_id: (per, kcal, protein_g)}. `per` is "100" (per 100 g or ml) or "piece"."""
    with open(path, newline="", encoding="utf-8") as f:
        return {
            row["ingredient_id"]: (row["per"], float(row["kcal"]), float(row["protein_g"]))
            for row in csv.DictReader(f)
        }


def need_nutrition(need, product, table: dict) -> tuple:
    """(kcal, protein_g) in one recipe line, for all servings. (0, 0) if unknown."""
    if need.ingredient_id not in table:
        return 0.0, 0.0
    per, kcal, protein = table[need.ingredient_id]
    amount = product.to_recipe_base(need.quantity, need.unit)  # g, ml or pieces
    factor = amount if per == "piece" else amount / 100
    return kcal * factor, protein * factor


def meal_nutrition(ingredients, servings: int, catalogue: dict, table: dict = None) -> dict:
    """Calories and protein for ONE serving of a recipe, rounded to whole numbers."""
    table = table if table is not None else load_nutrition()
    kcal = protein = 0.0
    for need in ingredients:
        product = catalogue.get(need.ingredient_id)
        if product is None:
            continue
        k, p = need_nutrition(need, product, table)
        kcal, protein = kcal + k, protein + p
    servings = max(servings, 1)
    return {"kcal": round(kcal / servings), "protein_g": round(protein / servings)}
