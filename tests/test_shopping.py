"""Tests for the shopping list maths. Run with: pytest"""

import pytest

from src.shopping import (
    IngredientNeed,
    Product,
    ShoppingError,
    build_shopping_list,
    check_budget,
    consolidate,
    euros_to_cents,
    format_euros,
    to_base,
    total_cost_cents,
)

# A tiny fake catalogue so the tests do not depend on the real price file.
CATALOGUE = {
    "rice": Product("rice", "Rice", "Arroz", 115, 1.0, "kg"),
    "milk": Product("milk", "Milk", "Leche", 84, 1.0, "l"),
    "eggs": Product("eggs", "Eggs (6)", "Huevos (6)", 180, 6, "ud"),
    "tomato": Product("tomato", "Tomato", "Tomate", 28, 0.14, "kg"),
    "salt": Product("salt", "Salt", "Sal", 40, 1.0, "kg"),
}


def line_for(lines, ingredient_id):
    return next(line for line in lines if line.ingredient_id == ingredient_id)


def test_to_base_converts_kg_and_l():
    assert to_base(1.5, "kg") == (1500, "g")
    assert to_base(0.25, "l") == (250, "ml")
    assert to_base(3, "ud") == (3, "ud")


def test_to_base_rejects_unknown_unit_and_bad_quantity():
    with pytest.raises(ShoppingError):
        to_base(2, "tbsp")
    with pytest.raises(ShoppingError):
        to_base(0, "g")
    with pytest.raises(ShoppingError):
        to_base(-5, "g")


def test_same_ingredient_in_several_recipes_is_added_up():
    needs = [IngredientNeed("rice", 300, "g"), IngredientNeed("rice", 400, "g")]
    assert consolidate(needs, CATALOGUE) == {"rice": 700}


def test_we_buy_whole_packages_not_portions():
    # 700 g of rice still means paying for a full 1 kg bag.
    lines = build_shopping_list([IngredientNeed("rice", 700, "g")], CATALOGUE)
    rice = line_for(lines, "rice")
    assert rice.packages == 1
    assert rice.cost_cents == 115
    assert rice.leftover == 300


def test_exact_package_size_does_not_buy_an_extra_one():
    lines = build_shopping_list([IngredientNeed("rice", 2000, "g")], CATALOGUE)
    assert line_for(lines, "rice").packages == 2


def test_one_gram_over_buys_another_package():
    lines = build_shopping_list([IngredientNeed("rice", 1001, "g")], CATALOGUE)
    assert line_for(lines, "rice").packages == 2


def test_eggs_are_counted_in_units():
    # 7 eggs -> two boxes of 6.
    lines = build_shopping_list([IngredientNeed("eggs", 7, "ud")], CATALOGUE)
    eggs = line_for(lines, "eggs")
    assert eggs.packages == 2
    assert eggs.leftover == 5


def test_loose_vegetables_are_bought_by_the_piece():
    # 500 g of tomatoes at 140 g per tomato -> 4 tomatoes.
    lines = build_shopping_list([IngredientNeed("tomato", 500, "g")], CATALOGUE)
    assert line_for(lines, "tomato").packages == 4
    assert line_for(lines, "tomato").cost_cents == 112


def test_items_already_at_home_cost_nothing_but_stay_listed():
    needs = [IngredientNeed("salt", 10, "g"), IngredientNeed("rice", 500, "g")]
    lines = build_shopping_list(needs, CATALOGUE, already_have=frozenset({"salt"}))
    assert line_for(lines, "salt").already_have is True
    assert line_for(lines, "salt").cost_cents == 0
    assert total_cost_cents(lines) == 115


def test_unknown_ingredient_is_rejected():
    # The model invented an ingredient that is not in our price data.
    with pytest.raises(ShoppingError, match="not in the price catalogue"):
        build_shopping_list([IngredientNeed("dragon_fruit", 100, "g")], CATALOGUE)


def test_wrong_unit_for_product_is_rejected():
    # Milk is sold by the litre; "200 g of milk" cannot be priced safely.
    with pytest.raises(ShoppingError, match="sold in l"):
        build_shopping_list([IngredientNeed("milk", 200, "g")], CATALOGUE)


def test_budget_check_within_and_over():
    lines = build_shopping_list(
        [IngredientNeed("rice", 700, "g"), IngredientNeed("milk", 1500, "ml")], CATALOGUE
    )
    # 1 rice (1.15) + 2 milk (1.68) = 2.83
    assert total_cost_cents(lines) == 283

    ok = check_budget(lines, euros_to_cents(5))
    assert ok.within_budget is True
    assert ok.difference_cents == 217

    over = check_budget(lines, euros_to_cents(2.50))
    assert over.within_budget is False
    assert over.difference_cents == -33


def test_budget_equal_to_total_is_within_budget():
    lines = build_shopping_list([IngredientNeed("rice", 100, "g")], CATALOGUE)
    assert check_budget(lines, 115).within_budget is True


def test_budget_must_be_positive():
    with pytest.raises(ShoppingError):
        check_budget([], 0)


def test_format_euros():
    assert format_euros(283) == "2.83 €"
    assert format_euros(5) == "0.05 €"
    assert format_euros(-33) == "-0.33 €"
