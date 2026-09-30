"""Tests for calories and protein per plate (pure code, no model)."""

from src.catalogue import load_catalogue, supermarkets
from src.nutrition import load_nutrition, meal_nutrition
from src.shopping import IngredientNeed

CATALOGUE = load_catalogue()


def test_every_staple_of_every_shop_has_nutrition_values():
    table = load_nutrition()
    for supermarket in supermarkets():
        missing = set(load_catalogue(supermarket=supermarket)) - set(table)
        assert missing == set(), f"{supermarket}: no nutrition values for {sorted(missing)}"


def test_values_are_sane():
    for ingredient_id, (per, kcal, protein) in load_nutrition().items():
        assert per in ("100", "piece"), ingredient_id
        assert 0 <= kcal <= 900 and 0 <= protein <= 30, ingredient_id
        assert protein * 4 <= kcal + 1, f"{ingredient_id}: more calories from protein than in total"


def test_one_serving_is_the_recipe_total_divided_by_the_servings():
    # 200 g chicken breast (110 kcal, 23 g protein per 100 g) + 160 g rice (355 kcal, 7 g) for 2 people
    needs = [IngredientNeed("chicken_breast", 200, "g"), IngredientNeed("rice_round", 160, "g")]
    assert meal_nutrition(needs, 2, CATALOGUE) == {"kcal": round((220 + 568) / 2), "protein_g": round((46 + 11.2) / 2)}


def test_eggs_are_counted_per_piece_and_produce_per_gram():
    eggs = meal_nutrition([IngredientNeed("eggs_6", 2, "ud")], 1, CATALOGUE)
    assert eggs == {"kcal": 150, "protein_g": 13}
    # 2 tomatoes counted in pieces = 2 x 140 g at 18 kcal per 100 g
    tomatoes = meal_nutrition([IngredientNeed("tomato", 2, "ud")], 1, CATALOGUE)
    assert tomatoes["kcal"] == round(280 * 0.18)


def test_oil_is_counted_per_millilitre():
    assert meal_nutrition([IngredientNeed("olive_oil", 10, "ml")], 1, CATALOGUE)["kcal"] == 82
