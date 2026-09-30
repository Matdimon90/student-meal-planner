"""The whole pipeline, from a user's request to a priced meal plan.

    request -> code checks the input
            -> code removes forbidden ingredients
            -> MODEL proposes meals (JSON)
            -> code checks the answer, asks the model to repair it if needed
            -> code builds the shopping list and the real total
            -> if over budget, MODEL gets one chance to make it cheaper
            -> if meals miss the portion or protein target (counted by code),
               MODEL gets one chance to adjust them; the better plan is kept
            -> code reports the final result honestly

The model is creative; the code is the judge. The model never calculates
the total and never decides whether the budget is respected.
"""

import time
from dataclasses import asdict

from src.catalogue import allowed_catalogue, load_catalogue, snapshot_info, supermarkets
from src.nutrition import meal_nutrition, nutrition_gaps, protein_sources
from src.photos import choose_photos
from src.plan import (Meal, MealPlan, PlanFormatError, PlanRequest, RequestError, clean_minutes, clean_tags, parse_plan, validate_plan,
                      validate_request)
from src.prompting import render_prompt, render_swap_prompt
from src.shopping import IngredientNeed, build_shopping_list, check_budget, format_euros, used_cost_cents

DEFAULT_PROMPT_VERSION = "v7"
SWAP_PROMPT_VERSION = "swap2"
MAX_REPAIRS = 1
MAX_CHEAPER_RETRIES = 1
MAX_NUTRITION_RETRIES = 1
PROTEIN_TAG_GRAMS = 30  # a meal is labelled "protein" from this many grams per serving


def _repair_message(problems: list) -> str:
    listed = "\n".join(f"- {problem}" for problem in problems[:15])
    return (
        "Your answer cannot be used because of these problems:\n"
        f"{listed}\n"
        "Return the full corrected JSON object, following the same rules and format."
    )


def _cheaper_message(check, lines: list, catalogue: dict) -> str:
    expensive = sorted(lines, key=lambda line: line.cost_cents, reverse=True)[:5]
    listed = "\n".join(
        f"- {line.ingredient_id}: {line.packages} package(s), {format_euros(line.cost_cents)}" for line in expensive
    )
    return (
        f"I priced your plan with whole packages. It costs {format_euros(check.total_cents)} "
        f"but the budget is {format_euros(check.budget_cents)}.\n"
        f"The most expensive lines were:\n{listed}\n"
        "Return a cheaper full plan in the same JSON format. If it cannot be done, "
        'set "feasible" to false and explain honestly.'
    )


def _nutrition_message(gaps: list, allowed: dict) -> str:
    listed = "\n".join(f"- {gap}" for gap in gaps[:15])
    sources = ", ".join(protein_sources(allowed))
    return (
        "I counted the calories and protein of one serving of each meal with our nutrition table. "
        "These meals miss the user's targets:\n"
        f"{listed}\n"
        "Return the full plan in the same JSON format with these meals adjusted as listed. "
        + (f"Protein-rich ingredients this user can eat: {sources}. " if sources else "")
        + "Stay within budget_eur, keep the other meals as they are."
    )


def _code_suggestions(request: PlanRequest, check, lines: list) -> list:
    """Adjustments computed from the real numbers, not written by the model."""
    suggestions = [f"budget_needed:{format_euros(check.total_cents)}"]
    affordable_days = int(request.days * check.budget_cents / check.total_cents)
    if 1 <= affordable_days < request.days:
        suggestions.append(f"days_affordable:{affordable_days}")
    pantry = [line.ingredient_id for line in lines if not line.already_have and line.needed / line.bought < 0.15]
    if pantry:
        suggestions.append("barely_used:" + ",".join(pantry[:5]))
    return suggestions


def generate_plan(request: PlanRequest, call_model, prompt_version: str = DEFAULT_PROMPT_VERSION, catalogue: dict = None) -> dict:
    """Run the pipeline. `call_model(system, messages) -> str` is passed in so
    tests can use a fake model and never need an API key."""
    validate_request(request)
    catalogue = catalogue or load_catalogue(supermarket=request.supermarket or None)
    allowed = allowed_catalogue(catalogue, request.diet, request.allergies, request.disliked)

    system, user_message = render_prompt(prompt_version, request, allowed)
    messages = [{"role": "user", "content": user_message}]
    trace = []  # what happened at each model call, kept for transparency and for evaluation
    repairs_left, cheaper_left, nutrition_left = MAX_REPAIRS, MAX_CHEAPER_RETRIES, MAX_NUTRITION_RETRIES
    plan = lines = check = None
    kept = None  # (plan, lines, check, gaps): a good plan kept while the model tries to meet the nutrition targets

    while True:
        started = time.perf_counter()
        reply = call_model(system, messages)
        seconds = round(time.perf_counter() - started, 1)
        messages.append({"role": "assistant", "content": reply})

        try:
            plan = parse_plan(reply)
            problems = [] if not plan.feasible else validate_plan(plan, request, catalogue, allowed)
        except PlanFormatError as error:
            plan, problems = None, [f"BAD_FORMAT: {error}"]

        if problems:
            trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "invalid", "problems": problems})
            if kept:  # the nutrition retry broke the plan: the plan we already had stays
                return _result("ok", request, prompt_version, trace, catalogue, *kept[:3])
            if repairs_left == 0:
                return _result("invalid_plan", request, prompt_version, trace, catalogue)
            repairs_left -= 1
            messages.append({"role": "user", "content": _repair_message(problems)})
            continue

        if not plan.feasible:
            trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "model_says_infeasible"})
            if kept:
                return _result("ok", request, prompt_version, trace, catalogue, *kept[:3])
            return _result("infeasible", request, prompt_version, trace, catalogue, plan=plan, lines=lines, check=check)

        lines = build_shopping_list(plan.needs, allowed, request.already_have)
        check = check_budget(lines, round(request.budget_eur * 100))
        gaps = nutrition_gaps(plan, request, catalogue)
        trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "priced", "total_cents": check.total_cents, "nutrition_gaps": len(gaps)})

        if kept:  # this reply answers the nutrition retry: keep whichever plan misses fewer targets, within budget
            if check.within_budget and len(gaps) < len(kept[3]):
                return _result("ok", request, prompt_version, trace, catalogue, plan, lines, check)
            trace[-1]["kept"] = False  # priced but not shown: the first plan stays
            return _result("ok", request, prompt_version, trace, catalogue, *kept[:3])
        if check.within_budget:
            if gaps and nutrition_left:
                nutrition_left -= 1
                kept = (plan, lines, check, gaps)
                messages.append({"role": "user", "content": _nutrition_message(gaps, allowed)})
                continue
            return _result("ok", request, prompt_version, trace, catalogue, plan, lines, check)
        if cheaper_left == 0:
            return _result("over_budget", request, prompt_version, trace, catalogue, plan, lines, check)
        cheaper_left -= 1
        messages.append({"role": "user", "content": _cheaper_message(check, lines, catalogue)})


def _meal_from_dict(data: dict) -> Meal:
    """Rebuild a Meal from the JSON the web page sends back (it came from us)."""
    return Meal(
        day=int(data["day"]),
        meal=str(data["meal"]),
        recipe_name=str(data["recipe_name"]),
        servings=int(data["servings"]),
        ingredients=tuple(
            IngredientNeed(str(i["ingredient_id"]), float(i["quantity"]), str(i["unit"]))
            for i in data["ingredients"]
        ),
        steps=tuple(str(step) for step in data["steps"]),
        minutes=clean_minutes(data.get("minutes")),
        tags=clean_tags(data.get("tags")),  # the page sends them back: filter them again
    )


def swap_meal(request: PlanRequest, current_meals: list, day: int, meal: str, call_model,
              prompt_version: str = SWAP_PROMPT_VERSION, catalogue: dict = None) -> dict:
    """Replace one meal in an existing plan and re-price the whole plan.

    The model proposes a single new recipe for the (day, meal) slot; the code
    validates it, keeps the other meals untouched, and prices everything again.
    Same result shape as generate_plan, so the web page renders it the same way.
    """
    validate_request(request)
    catalogue = catalogue or load_catalogue(supermarket=request.supermarket or None)
    allowed = allowed_catalogue(catalogue, request.diet, request.allergies, request.disliked)

    try:
        meals = [_meal_from_dict(m) for m in current_meals]
    except (KeyError, TypeError, ValueError) as error:
        raise RequestError(f"The current plan could not be read: {error}")
    if (day, meal) not in request.slots:
        raise RequestError(f"This plan has no {meal} on day {day}")
    target = next((m for m in meals if m.day == day and m.meal == meal), None)
    others = [m for m in meals if not (m.day == day and m.meal == meal)]

    system, user_message = render_swap_prompt(request, allowed, day, meal, target.recipe_name if target else "", others, prompt_version)
    messages = [{"role": "user", "content": user_message}]
    trace = []
    repairs_left = MAX_REPAIRS
    candidate = None

    while True:
        started = time.perf_counter()
        reply = call_model(system, messages)
        seconds = round(time.perf_counter() - started, 1)
        messages.append({"role": "assistant", "content": reply})

        try:
            parsed = parse_plan(reply)
            proposed = parsed.meals[0] if parsed.meals else None
            if proposed is None:
                problems = ["NO_MEAL: the reply contained no meal"]
            else:
                # Trust the model for the recipe, not for the slot: force day, meal and servings.
                new_meal = Meal(day=day, meal=meal, recipe_name=proposed.recipe_name,
                                servings=request.people, ingredients=proposed.ingredients, steps=proposed.steps,
                                minutes=proposed.minutes, tags=proposed.tags)
                candidate = MealPlan(feasible=True, reason=parsed.reason, meals=tuple(others + [new_meal]))
                problems = validate_plan(candidate, request, catalogue, allowed)
        except PlanFormatError as error:
            problems = [f"BAD_FORMAT: {error}"]

        if problems:
            trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "invalid", "problems": problems})
            if repairs_left == 0:
                return _result("invalid_plan", request, prompt_version, trace, catalogue)
            repairs_left -= 1
            messages.append({"role": "user", "content": _repair_message(problems)})
            continue

        lines = build_shopping_list(candidate.needs, allowed, request.already_have)
        check = check_budget(lines, round(request.budget_eur * 100))
        trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "priced", "total_cents": check.total_cents})
        status = "ok" if check.within_budget else "over_budget"
        return _result(status, request, prompt_version, trace, catalogue, candidate, lines, check)


def _summary(request: PlanRequest, plan, shopping_list: list, check) -> dict:
    """A few numbers that tell the user (and our evaluation) how good the plan is."""
    servings = request.people * len(plan.meals)
    uses = {}
    for need in plan.needs:
        uses[need.ingredient_id] = uses.get(need.ingredient_id, 0) + 1
    return {
        "servings": servings,
        "cost_per_serving_cents": round(check.total_cents / servings) if servings else 0,
        "leftover_value_cents": sum(line["leftover_cents"] for line in shopping_list),
        "distinct_ingredients": len(uses),
        # Average number of recipes each ingredient appears in. Higher means less waste.
        "reuse_ratio": round(sum(uses.values()) / len(uses), 2) if uses else 0.0,
        "distinct_recipes": len({meal.recipe_name.lower() for meal in plan.meals}),
    }


def compare_supermarkets(plan, request: PlanRequest, current: str) -> list:
    """Price the same meals in every other supermarket we have a snapshot for.

    Pure code, no model call: the recipes do not change, only the packages and
    their prices. An ingredient a shop does not sell is listed in `missing`
    and the total for that shop is then only indicative.
    """
    rows = []
    for supermarket in supermarkets():
        if supermarket == current:
            continue
        catalogue = load_catalogue(supermarket=supermarket)
        needed = {need.ingredient_id for need in plan.needs}
        missing = sorted(needed - set(catalogue))
        needs = [need for need in plan.needs if need.ingredient_id in catalogue]
        lines = build_shopping_list(needs, catalogue, request.already_have)
        check = check_budget(lines, round(request.budget_eur * 100))
        rows.append({
            **snapshot_info(supermarket=supermarket),
            "total_cents": check.total_cents,
            "within_budget": check.within_budget,
            "missing": missing,
            "packages": sum(line.packages for line in lines),
        })
    return rows


def _result(status, request, prompt_version, trace, catalogue, plan=None, lines=None, check=None) -> dict:
    language = request.language
    supermarket = _supermarket_of(catalogue)

    def name(ingredient_id):
        product = catalogue[ingredient_id]
        return product.name_es if language == "es" else product.name_en

    result = {
        "status": status,  # ok | over_budget | infeasible | invalid_plan
        "prompt_version": prompt_version,
        "prices": snapshot_info(supermarket=supermarket),
        "comparison": [],
        "trace": trace,
        "reason": plan.reason if plan else "",
        "model_suggestions": list(plan.suggestions) if plan else [],
        "code_suggestions": [],
        "meals": [],
        "shopping_list": [],
        "budget": None,
        "summary": None,
    }
    if plan and plan.feasible:
        ordered = sorted(plan.meals, key=lambda m: (m.day, ("breakfast", "lunch", "dinner").index(m.meal)))
        photos = choose_photos(ordered)
        result["meals"] = [_meal_view(meal, photo, catalogue, request, name) for meal, photo in zip(ordered, photos)]
    if lines and check and plan and plan.feasible:
        result["shopping_list"] = [
            {
                **asdict(line),
                "name": name(line.ingredient_id),
                "package_size": catalogue[line.ingredient_id].package_size,
                "package_unit": catalogue[line.ingredient_id].package_unit,
                "package_price_cents": catalogue[line.ingredient_id].package_price_cents,
                "category": catalogue[line.ingredient_id].category,
                "product_name": catalogue[line.ingredient_id].product_name,
                # What the unused part of the packages is worth: money spent on food not in the plan.
                "leftover_cents": round(line.cost_cents * line.leftover / line.bought) if line.bought else 0,
            }
            for line in lines
        ]
        result["budget"] = asdict(check)
        result["summary"] = _summary(request, plan, result["shopping_list"], check)
        if not check.within_budget:
            result["code_suggestions"] = _code_suggestions(request, check, lines)
        if supermarket:  # a hand-made catalogue (tests) belongs to no shop: nothing to compare
            result["comparison"] = compare_supermarkets(plan, request, supermarket)
    return result


def _meal_view(meal, photo: str, catalogue: dict, request: PlanRequest, name) -> dict:
    """One meal as the web page shows it. Every number here comes from code."""
    nutrition = meal_nutrition(meal.ingredients, meal.servings, catalogue)  # per serving, estimates
    # The model labels its meals, but "protein" is a claim about a number,
    # so the code decides it from the counted grams.
    tags = [tag for tag in meal.tags if tag != "protein"]
    if nutrition["protein_g"] >= PROTEIN_TAG_GRAMS:
        tags = tags[:2] + ["protein"]
    return {
        "day": meal.day,
        "meal": meal.meal,
        "recipe_name": meal.recipe_name,
        "servings": meal.servings,
        "ingredients": [{**asdict(need), "name": name(need.ingredient_id)} for need in meal.ingredients],
        "steps": list(meal.steps),
        "minutes": meal.minutes,
        "tags": tags,
        "nutrition": nutrition,
        # Share of the packages this meal uses. The total is still whole packages.
        "cost_cents": used_cost_cents(meal.ingredients, catalogue, request.already_have),
        # Chosen by code from the name and ingredients (src/photos.py), never by the model.
        "photo": photo,
    }


def _supermarket_of(catalogue: dict) -> str:
    """The supermarket a catalogue was loaded from ("" for a hand-made one)."""
    return next(iter(catalogue.values())).supermarket if catalogue else ""
