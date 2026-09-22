"""Tests for loading prices and for the allergy / diet filter."""

import pytest

from src.catalogue import allowed_catalogue, load_catalogue, snapshot_info


@pytest.fixture(scope="module")
def catalogue():
    return load_catalogue()


def test_real_snapshot_loads_with_sane_values(catalogue):
    assert len(catalogue) >= 80
    for product in catalogue.values():
        assert product.package_price_cents > 0
        assert product.package_size > 0
        assert product.package_unit in {"kg", "l", "ud"}
        assert product.diet in {"vegan", "vegetarian", "fish", "meat"}


def test_prices_are_stored_in_cents(catalogue):
    assert catalogue["rice_round"].package_price_cents == 115


def test_recipe_unit_follows_package_unit(catalogue):
    assert catalogue["rice_round"].recipe_unit == "g"
    assert catalogue["milk"].recipe_unit == "ml"
    assert catalogue["eggs_6"].recipe_unit == "ud"


def test_snapshot_info_gives_the_price_date():
    info = snapshot_info()
    assert info["supermarket"] == "mercadona"
    assert info["captured_at"] == "2026-09-21"


def test_vegan_diet_removes_all_animal_products(catalogue):
    allowed = allowed_catalogue(catalogue, diet="vegan")
    assert "tofu" in allowed
    for forbidden in ("chicken_breast", "tuna_oil", "eggs_6", "milk", "mayonnaise"):
        assert forbidden not in allowed


def test_vegetarian_keeps_eggs_and_dairy_but_no_meat_or_fish(catalogue):
    allowed = allowed_catalogue(catalogue, diet="vegetarian")
    assert "eggs_6" in allowed and "milk" in allowed
    assert "bacon" not in allowed and "salmon_frozen" not in allowed


def test_pescatarian_keeps_fish(catalogue):
    allowed = allowed_catalogue(catalogue, diet="pescatarian")
    assert "tuna_oil" in allowed and "chicken_breast" not in allowed


def test_gluten_allergy_removes_pasta_bread_and_soy_sauce(catalogue):
    allowed = allowed_catalogue(catalogue, allergies=frozenset({"gluten"}))
    for forbidden in ("spaghetti", "sliced_bread", "soy_sauce", "flour"):
        assert forbidden not in allowed
    assert "rice_round" in allowed


def test_several_allergies_combine(catalogue):
    allowed = allowed_catalogue(catalogue, allergies=frozenset({"milk", "egg"}))
    assert "butter" not in allowed and "eggs_6" not in allowed


def test_disliked_ingredients_are_removed(catalogue):
    allowed = allowed_catalogue(catalogue, disliked=frozenset({"broccoli"}))
    assert "broccoli" not in allowed


def test_unknown_diet_or_allergen_is_an_error(catalogue):
    with pytest.raises(ValueError):
        allowed_catalogue(catalogue, diet="carnivore")
    with pytest.raises(ValueError):
        allowed_catalogue(catalogue, allergies=frozenset({"kryptonite"}))
