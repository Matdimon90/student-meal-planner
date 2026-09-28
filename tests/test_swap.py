"""Tests for swapping a single meal, using a fake model (no API key, no network)."""

import json

import pytest

from src.plan import PlanRequest, RequestError
from src.planner import swap_meal

# A tiny plan the web page would send back: two meals on day 1.
PLAN = [
    {"day": 1, "meal": "lunch", "recipe_name": "Rice and lentils", "servings": 1,
     "ingredients": [{"ingredient_id": "rice_round", "quantity": 100, "unit": "g"},
                     {"ingredient_id": "lentils_cooked", "quantity": 200, "unit": "g"}],
     "steps": ["Boil the rice.", "Warm the lentils."]},
    {"day": 1, "meal": "dinner", "recipe_name": "Egg fried rice", "servings": 1,
     "ingredients": [{"ingredient_id": "rice_round", "quantity": 100, "unit": "g"},
                     {"ingredient_id": "eggs_6", "quantity": 2, "unit": "ud"}],
     "steps": ["Fry the rice.", "Add the eggs."]},
]


def one_meal(ingredients, name="Tomato rice", day=1, meal="dinner", servings=1, feasible=True):
    meals = [] if not feasible else [
        {"day": day, "meal": meal, "recipe_name": name, "servings": servings,
         "ingredients": ingredients, "steps": ["Cook."]}
    ]
    return json.dumps({"feasible": feasible, "reason": "reuse", "meals": meals, "suggestions": []})


REUSE = [{"ingredient_id": "rice_round", "quantity": 120, "unit": "g"},
         {"ingredient_id": "lentils_cooked", "quantity": 150, "unit": "g"}]
INVENTED = [{"ingredient_id": "truffle", "quantity": 10, "unit": "g"}]
EXPENSIVE = [{"ingredient_id": "salmon_frozen", "quantity": 500, "unit": "g"}]


class FakeModel:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []

    def __call__(self, system, messages):
        self.calls.append((system, [dict(m) for m in messages]))
        return self.replies.pop(0)


def request(**changes):
    return PlanRequest(**{"budget_eur": 10, "people": 1, "days": 1, "meals": ("lunch", "dinner"), **changes})


def test_swap_replaces_only_the_target_meal_and_reprices_the_whole_plan():
    result = swap_meal(request(), PLAN, 1, "dinner", FakeModel(one_meal(REUSE, name="Tomato lentil rice")))
    assert result["status"] == "ok"
    by_slot = {(m["day"], m["meal"]): m["recipe_name"] for m in result["meals"]}
    assert by_slot[(1, "dinner")] == "Tomato lentil rice"   # replaced
    assert by_slot[(1, "lunch")] == "Rice and lentils"       # untouched
    assert result["budget"]["total_cents"] > 0


def test_swap_keeps_the_new_meal_in_the_forced_slot_even_if_the_model_mislabels_it():
    # The model answers with the wrong day/meal; the code pins it to the slot asked for.
    result = swap_meal(request(), PLAN, 1, "dinner", FakeModel(one_meal(REUSE, day=9, meal="breakfast")))
    slots = {(m["day"], m["meal"]) for m in result["meals"]}
    assert slots == {(1, "lunch"), (1, "dinner")}


def test_invented_ingredient_triggers_one_repair_then_succeeds():
    model = FakeModel(one_meal(INVENTED), one_meal(REUSE))
    result = swap_meal(request(), PLAN, 1, "dinner", model)
    assert result["status"] == "ok"
    assert len(model.calls) == 2
    assert "UNKNOWN_INGREDIENT" in model.calls[1][1][-1]["content"]


def test_a_meal_that_stays_invalid_is_refused():
    result = swap_meal(request(), PLAN, 1, "dinner", FakeModel(one_meal(INVENTED), one_meal(INVENTED)))
    assert result["status"] == "invalid_plan"


def test_a_swap_that_breaks_the_budget_is_reported_as_over_budget():
    result = swap_meal(request(budget_eur=2), PLAN, 1, "dinner", FakeModel(one_meal(EXPENSIVE)))
    assert result["status"] == "over_budget"
    assert result["budget"]["within_budget"] is False


def test_swapping_a_slot_that_is_not_in_the_plan_is_rejected():
    with pytest.raises(RequestError):
        swap_meal(request(), PLAN, 5, "breakfast", FakeModel(one_meal(REUSE)))


def test_the_other_recipes_are_shown_to_the_model_for_reuse():
    model = FakeModel(one_meal(REUSE))
    swap_meal(request(), PLAN, 1, "dinner", model)
    prompt = model.calls[0][1][0]["content"]
    assert "Rice and lentils" in prompt          # the meal that stays
    assert "Egg fried rice" in prompt            # the current recipe being replaced
