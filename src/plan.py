"""The shapes of a request and of a meal plan, and the checks we run on both.

The model's answer is never trusted as it comes. `parse_plan` turns its JSON
into Python objects and `validate_plan` lists everything that is wrong with
it: invented ingredients, forbidden ingredients, wrong units, missing meals.
"""

import json
from dataclasses import dataclass, field

from src.catalogue import DIET_ALLOWS, KNOWN_ALLERGENS, supermarkets
from src.shopping import IngredientNeed

MEAL_TYPES = ("breakfast", "lunch", "dinner")
LANGUAGES = ("en", "es")
MAX_PEOPLE = 8
MAX_DAYS = 14
MAX_BUDGET_EUR = 1000
MAX_NOTES_CHARS = 300
# More than this per person in one recipe is almost certainly a model mistake.
MAX_PER_SERVING = {"g": 1000, "ml": 1000, "ud": 6}


class RequestError(ValueError):
    """The user's input is invalid. The message is safe to show to the user."""


class PlanFormatError(ValueError):
    """The model's answer is not the JSON shape we asked for."""


@dataclass(frozen=True)
class PlanRequest:
    budget_eur: float
    people: int
    days: int
    meals: tuple = ("lunch", "dinner")
    diet: str = "omnivore"
    allergies: frozenset = frozenset()
    disliked: frozenset = frozenset()  # ingredient_ids
    already_have: frozenset = frozenset()  # ingredient_ids
    language: str = "en"
    notes: str = ""  # free text from the user: treated as data, never as instructions
    supermarket: str = ""  # "" means the default supermarket (see src/catalogue.py)

    @property
    def slots(self) -> list:
        """Every (day, meal) the plan must cover, in order."""
        return [(day, meal) for day in range(1, self.days + 1) for meal in MEAL_TYPES if meal in self.meals]


@dataclass(frozen=True)
class Meal:
    day: int
    meal: str
    recipe_name: str
    servings: int
    ingredients: tuple  # of IngredientNeed
    steps: tuple  # of str


@dataclass(frozen=True)
class MealPlan:
    feasible: bool
    reason: str
    meals: tuple  # of Meal
    suggestions: tuple = field(default_factory=tuple)

    @property
    def needs(self) -> list:
        return [need for meal in self.meals for need in meal.ingredients]


def validate_request(request: PlanRequest) -> None:
    """Reject impossible or abusive input before spending money on a model call."""
    if not 0 < request.budget_eur <= MAX_BUDGET_EUR:
        raise RequestError(f"Budget must be between 0 and {MAX_BUDGET_EUR} euros")
    if not 1 <= request.people <= MAX_PEOPLE:
        raise RequestError(f"Number of people must be between 1 and {MAX_PEOPLE}")
    if not 1 <= request.days <= MAX_DAYS:
        raise RequestError(f"Number of days must be between 1 and {MAX_DAYS}")
    if not request.meals or any(meal not in MEAL_TYPES for meal in request.meals):
        raise RequestError(f"Meals must be chosen from {list(MEAL_TYPES)}")
    if request.diet not in DIET_ALLOWS:
        raise RequestError(f"Diet must be one of {sorted(DIET_ALLOWS)}")
    if set(request.allergies) - KNOWN_ALLERGENS:
        raise RequestError(f"Allergies must be chosen from {sorted(KNOWN_ALLERGENS)}")
    if request.language not in LANGUAGES:
        raise RequestError(f"Language must be one of {list(LANGUAGES)}")
    if len(request.notes) > MAX_NOTES_CHARS:
        raise RequestError(f"Notes must be at most {MAX_NOTES_CHARS} characters")
    if request.supermarket and request.supermarket not in supermarkets():
        raise RequestError(f"Supermarket must be one of {supermarkets()}")


def extract_json(text: str) -> dict:
    """Find the JSON object in the model's reply, even if it added text around it."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise PlanFormatError("No JSON object found in the model's reply")
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as error:
        raise PlanFormatError(f"Reply is not valid JSON: {error}") from error
    if not isinstance(data, dict):
        raise PlanFormatError("Reply JSON must be an object")
    return data


def parse_plan(text: str) -> MealPlan:
    """Turn the model's reply into a MealPlan, or raise PlanFormatError."""
    data = extract_json(text)
    try:
        meals = tuple(
            Meal(
                day=int(m["day"]),
                meal=str(m["meal"]),
                recipe_name=str(m["recipe_name"]).strip(),
                servings=int(m["servings"]),
                ingredients=tuple(
                    IngredientNeed(str(i["ingredient_id"]), float(i["quantity"]), str(i["unit"]))
                    for i in m["ingredients"]
                ),
                steps=tuple(str(step).strip() for step in m["steps"]),
            )
            for m in data.get("meals", [])
        )
        return MealPlan(
            feasible=bool(data["feasible"]),
            reason=str(data.get("reason", "")).strip(),
            meals=meals,
            suggestions=tuple(str(s).strip() for s in data.get("suggestions", [])),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise PlanFormatError(f"Reply JSON has the wrong shape: {error!r}") from error


def validate_plan(plan: MealPlan, request: PlanRequest, full_catalogue: dict, allowed: dict) -> list:
    """Return a list of problems. An empty list means the plan can be priced safely.

    Each problem starts with a short code so the evaluation script can count them.
    """
    problems = []

    expected = request.slots
    got = [(meal.day, meal.meal) for meal in plan.meals]
    for slot in expected:
        if got.count(slot) == 0:
            problems.append(f"MISSING_MEAL: day {slot[0]} {slot[1]} is missing")
        elif got.count(slot) > 1:
            problems.append(f"DUPLICATE_MEAL: day {slot[0]} {slot[1]} appears more than once")
    for slot in sorted(set(got) - set(expected)):
        problems.append(f"EXTRA_MEAL: day {slot[0]} {slot[1]} was not requested")

    for meal in plan.meals:
        where = f"day {meal.day} {meal.meal} ({meal.recipe_name or 'no name'})"
        if not meal.recipe_name:
            problems.append(f"NO_NAME: {where} has no recipe name")
        if not meal.steps:
            problems.append(f"NO_STEPS: {where} has no cooking steps")
        if not meal.ingredients:
            problems.append(f"NO_INGREDIENTS: {where} has no ingredients")
        if meal.servings != request.people:
            problems.append(f"WRONG_SERVINGS: {where} serves {meal.servings}, expected {request.people}")

        for need in meal.ingredients:
            if need.ingredient_id not in full_catalogue:
                problems.append(f"UNKNOWN_INGREDIENT: '{need.ingredient_id}' in {where} is not in the catalogue")
                continue
            if need.ingredient_id not in allowed:
                problems.append(f"FORBIDDEN_INGREDIENT: '{need.ingredient_id}' in {where} breaks the user's diet, allergies or dislikes")
                continue
            product = allowed[need.ingredient_id]
            if not product.accepts_unit(need.unit):
                problems.append(f"WRONG_UNIT: '{need.ingredient_id}' in {where} must be in {product.recipe_unit}, got {need.unit}")
                continue
            if need.quantity <= 0:
                problems.append(f"BAD_QUANTITY: '{need.ingredient_id}' in {where} has quantity {need.quantity}")
            elif product.to_recipe_base(need.quantity, need.unit) > MAX_PER_SERVING[product.recipe_unit] * request.people:
                problems.append(f"BAD_QUANTITY: '{need.ingredient_id}' in {where} has an unrealistic quantity {need.quantity} {need.unit}")
    return problems
