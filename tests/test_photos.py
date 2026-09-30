"""Tests for the dish photo chosen by code (no model involved)."""

from pathlib import Path

from src.photos import DEFAULT_PHOTO, candidate_photos, choose_photos, photo_files
from src.plan import Meal
from src.shopping import IngredientNeed

PHOTO_DIR = Path(__file__).resolve().parent.parent / "public" / "img" / "dishes"


def meal(name, *ingredient_ids):
    return Meal(day=1, meal="dinner", recipe_name=name, servings=1,
                ingredients=tuple(IngredientNeed(i, 100, "g") for i in ingredient_ids), steps=("Cook.",))


def test_every_photo_the_code_can_choose_exists_and_is_credited():
    credits = (PHOTO_DIR / "CREDITS.md").read_text(encoding="utf-8")
    for photo in photo_files():
        assert (PHOTO_DIR / f"{photo}.webp").is_file(), photo
        assert f"`{photo}.webp`" in credits, photo
    assert len(list(PHOTO_DIR.glob("*.webp"))) == len(photo_files())  # no unused image in the repo


def test_english_and_spanish_names_find_the_same_photo():
    assert candidate_photos("Meatballs in tomato sauce", [])[0][0] == "meatballs"
    assert candidate_photos("Albóndigas con tomate", [])[0][0] == "meatballs"
    assert candidate_photos("Lentil stew", [])[0][0] == candidate_photos("Guiso de lentejas", [])[0][0] == "lentils"


def test_specific_dishes_win_over_their_main_ingredient():
    assert candidate_photos("Chickpea curry", [])[0][0] == "curry"
    assert candidate_photos("Tortilla de patatas", [])[0][0] == "tortilla"
    assert candidate_photos("Tortilla wraps with chicken", [])[0][0] == "wrap"
    assert candidate_photos("Baked macaroni with cheese", [])[0][0] == "pasta_bake"
    assert candidate_photos("Pasta with creamy mushrooms", [])[0][0] == "pasta_creamy"
    assert candidate_photos("Macarrones con nata y bacon", [])[0][0] == "pasta_creamy"


def test_ingredients_decide_when_the_name_says_nothing():
    assert choose_photos([meal("Grandma's special", "lentils_dry", "carrots")]) == ["lentils"]
    assert choose_photos([meal("Mystery dish", "salt")]) == [DEFAULT_PHOTO]


def test_a_week_of_rice_alternates_between_the_rice_photos():
    week = [meal("Rice with egg", "rice_round"), meal("Rice with peas", "rice_round"), meal("Rice with tuna", "rice_round")]
    assert choose_photos(week) == ["rice_bowl", "rice_bowl_2", "rice_bowl"]


def test_a_photo_is_never_swapped_for_a_worse_one_just_to_be_different():
    # Macaroni with eggs is a pasta dish: it keeps a pasta photo even after spaghetti, never the omelette.
    photos = choose_photos([meal("Spaghetti with tomato", "spaghetti"), meal("Macaroni with peas and eggs", "macaroni", "eggs_6")])
    assert photos == ["pasta_tomato", "pasta_tomato_2"]


def test_pasta_with_pulses_is_still_a_pasta_dish():
    assert choose_photos([meal("Spaghetti with chickpea tomato sauce", "spaghetti", "chickpeas_cooked")]) == ["pasta_tomato"]
    assert choose_photos([meal("Macarrones con lentejas", "macaroni", "lentils_cooked")]) == ["pasta_tomato"]
    assert choose_photos([meal("Sopa de fideos", "macaroni")]) == ["soup"]  # a noodle soup is a soup


def test_a_salad_looks_like_a_salad_even_with_pulses_in_it():
    assert choose_photos([meal("Chickpea salad with cucumber", "chickpeas_cooked")]) == ["salad"]


def test_common_spanish_names_find_the_right_dish():
    cases = {
        "Lasaña de verduras": "pasta_bake",
        "Pollo al yogur con arroz": "rice_bowl",
        "Arroz con almendras tostadas": "rice_bowl",
        "Arroz con pollo al curry": "curry",
        "Pollo al chilindrón": "chicken_plate",
        "Garbanzos con tacos de jamón": "chickpeas",
        "Tacos de pollo": "wrap",
        "Yogur con plátano": "yogurt",
    }
    for name, photo in cases.items():
        assert choose_photos([meal(name)]) == [photo], name
