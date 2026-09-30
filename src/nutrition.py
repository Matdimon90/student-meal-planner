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


def nutrition_gaps(plan, request, catalogue: dict) -> list:
    """Lunches and dinners that miss the user's portion or protein target, as
    counted by code, each with what to change. Breakfast is not checked: the
    targets are for main meals."""
    from src.plan import PORTIONS, PROTEIN_TARGETS

    kcal_range, protein_min = PORTIONS[request.portion], PROTEIN_TARGETS[request.protein]
    if not kcal_range and not protein_min:
        return []
    table = load_nutrition()
    gaps = []
    for meal in plan.meals:
        if meal.meal == "breakfast":
            continue
        counted = meal_nutrition(meal.ingredients, meal.servings, catalogue, table)
        misses = []
        if protein_min and counted["protein_g"] < protein_min:
            misses.append(f"{counted['protein_g']} g of protein, needs at least {protein_min} g: add protein")
        if kcal_range and counted["kcal"] < kcal_range[0]:
            misses.append(f"{counted['kcal']} kcal, needs at least {kcal_range[0]}: bigger portion")
        if kcal_range and kcal_range[1] and counted["kcal"] > kcal_range[1]:
            misses.append(f"{counted['kcal']} kcal, needs at most {kcal_range[1]}: smaller portion")
        if misses:
            gaps.append(f"day {meal.day} {meal.meal} ({meal.recipe_name}): " + "; ".join(misses))
    return gaps


def protein_sources(allowed: dict, limit: int = 8) -> list:
    """The richest protein sources this user may eat in this shop, best first."""
    table = load_nutrition()
    rich = [(table[i][2], i) for i in allowed if i in table and table[i][2] >= (6 if table[i][0] == "piece" else 10)]
    return [ingredient_id for _, ingredient_id in sorted(rich, reverse=True)[:limit]]
