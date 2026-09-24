"""Tests for request validation and for checking the model's answer."""

import json

import pytest

from src.catalogue import allowed_catalogue, load_catalogue
from src.plan import (
    PlanFormatError,
    PlanRequest,
    RequestError,
    parse_plan,
    validate_plan,
    validate_request,
)

CATALOGUE = load_catalogue()


def make_reply(meals, feasible=True):
    return json.dumps({"feasible": feasible, "reason": "", "meals": meals, "suggestions": []})


def make_meal(day=1, meal="dinner", servings=2, ingredients=None):
    return {
        "day": day,
        "meal": meal,
        "recipe_name": "Rice with tomato",
        "servings": servings,
        "ingredients": ingredients
        or [
            {"ingredient_id": "rice_round", "quantity": 160, "unit": "g"},
            {"ingredient_id": "crushed_tomato", "quantity": 200, "unit": "g"},
        ],
        "steps": ["Boil the rice.", "Add the tomato."],
    }


REQUEST = PlanRequest(budget_eur=20, people=2, days=1, meals=("dinner",))


def problems_for(reply, request=REQUEST):
    allowed = allowed_catalogue(CATALOGUE, request.diet, request.allergies, request.disliked)
    return validate_plan(parse_plan(reply), request, CATALOGUE, allowed)


# --- invalid user input -----------------------------------------------------

@pytest.mark.parametrize(
    "changes",
    [
        {"budget_eur": 0},
        {"budget_eur": -10},
        {"budget_eur": 5000},
        {"people": 0},
        {"people": 50},
        {"days": 0},
        {"days": 60},
        {"meals": ()},
        {"meals": ("brunch",)},
        {"diet": "carnivore"},
        {"allergies": frozenset({"kryptonite"})},
        {"language": "fr"},
        {"notes": "x" * 301},
    ],
)
def test_invalid_requests_are_rejected(changes):
    values = {"budget_eur": 20, "people": 2, "days": 3, **changes}
    with pytest.raises(RequestError):
        validate_request(PlanRequest(**values))


def test_valid_request_passes():
    validate_request(PlanRequest(budget_eur=35.5, people=3, days=7, meals=("breakfast", "lunch", "dinner")))


def test_slots_lists_every_day_and_meal_in_order():
    request = PlanRequest(budget_eur=20, people=1, days=2, meals=("dinner", "lunch"))
    assert request.slots == [(1, "lunch"), (1, "dinner"), (2, "lunch"), (2, "dinner")]


# --- parsing the model's reply ----------------------------------------------

def test_json_wrapped_in_text_or_code_fences_is_still_parsed():
    reply = "Here is your plan:\n```json\n" + make_reply([make_meal()]) + "\n```\nEnjoy!"
    assert len(parse_plan(reply).meals) == 1


def test_reply_without_json_is_a_format_error():
    with pytest.raises(PlanFormatError):
        parse_plan("Sorry, I cannot help with that.")


def test_reply_with_missing_fields_is_a_format_error():
    with pytest.raises(PlanFormatError):
        parse_plan(json.dumps({"feasible": True, "meals": [{"day": 1}]}))


# --- checking the content of the plan ---------------------------------------

def test_good_plan_has_no_problems():
    assert problems_for(make_reply([make_meal()])) == []


def test_invented_ingredient_is_reported():
    meal = make_meal(ingredients=[{"ingredient_id": "saffron", "quantity": 1, "unit": "g"}])
    assert any(p.startswith("UNKNOWN_INGREDIENT") for p in problems_for(make_reply([meal])))


def test_ingredient_that_breaks_an_allergy_is_reported():
    request = PlanRequest(budget_eur=20, people=2, days=1, meals=("dinner",), allergies=frozenset({"gluten"}))
    meal = make_meal(ingredients=[{"ingredient_id": "spaghetti", "quantity": 200, "unit": "g"}])
    assert any(p.startswith("FORBIDDEN_INGREDIENT") for p in problems_for(make_reply([meal]), request))


def test_meat_in_a_vegetarian_plan_is_reported():
    request = PlanRequest(budget_eur=20, people=2, days=1, meals=("dinner",), diet="vegetarian")
    meal = make_meal(ingredients=[{"ingredient_id": "bacon", "quantity": 100, "unit": "g"}])
    assert any(p.startswith("FORBIDDEN_INGREDIENT") for p in problems_for(make_reply([meal]), request))


def test_wrong_unit_is_reported():
    meal = make_meal(ingredients=[{"ingredient_id": "milk", "quantity": 200, "unit": "g"}])
    assert any(p.startswith("WRONG_UNIT") for p in problems_for(make_reply([meal])))


def test_missing_and_extra_meals_are_reported():
    request = PlanRequest(budget_eur=20, people=2, days=2, meals=("dinner",))
    problems = problems_for(make_reply([make_meal(day=1), make_meal(day=1, meal="lunch")]), request)
    assert any(p.startswith("MISSING_MEAL: day 2 dinner") for p in problems)
    assert any(p.startswith("EXTRA_MEAL: day 1 lunch") for p in problems)


def test_wrong_number_of_servings_is_reported():
    assert any(p.startswith("WRONG_SERVINGS") for p in problems_for(make_reply([make_meal(servings=4)])))


def test_unrealistic_quantity_is_reported():
    meal = make_meal(ingredients=[{"ingredient_id": "rice_round", "quantity": 50000, "unit": "g"}])
    assert any(p.startswith("BAD_QUANTITY") for p in problems_for(make_reply([meal])))


def test_produce_may_be_counted_in_pieces_but_pasta_may_not():
    from src.catalogue import load_catalogue, allowed_catalogue
    catalogue = load_catalogue()
    allowed = allowed_catalogue(catalogue)
    req = PlanRequest(budget_eur=20, people=2, days=1, meals=("dinner",))
    plan = parse_plan(json.dumps({"feasible": True, "reason": "", "meals": [{"day": 1, "meal": "dinner", "recipe_name": "Fruit and pasta", "servings": 2,
        "ingredients": [{"ingredient_id": "banana", "quantity": 2, "unit": "ud"}, {"ingredient_id": "spaghetti", "quantity": 2, "unit": "ud"}], "steps": ["Mix."]}], "suggestions": []}))
    problems = validate_plan(plan, req, catalogue, allowed)
    assert len(problems) == 1 and problems[0].startswith("WRONG_UNIT: 'spaghetti'")


def test_supermarket_must_exist():
    with pytest.raises(RequestError, match="Supermarket"):
        validate_request(PlanRequest(budget_eur=20, people=2, days=1, supermarket="lidl"))
    validate_request(PlanRequest(budget_eur=20, people=2, days=1, supermarket="dia"))
