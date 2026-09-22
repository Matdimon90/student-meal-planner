"""The whole pipeline, from a user's request to a priced meal plan.

    request -> code checks the input
            -> code removes forbidden ingredients
            -> MODEL proposes meals (JSON)
            -> code checks the answer, asks the model to repair it if needed
            -> code builds the shopping list and the real total
            -> if over budget, MODEL gets one chance to make it cheaper
            -> code reports the final result honestly

The model is creative; the code is the judge. The model never calculates
the total and never decides whether the budget is respected.
"""

import time
from dataclasses import asdict

from src.catalogue import allowed_catalogue, load_catalogue, snapshot_info
from src.plan import PlanFormatError, PlanRequest, parse_plan, validate_plan, validate_request
from src.prompting import render_prompt
from src.shopping import build_shopping_list, check_budget, format_euros

DEFAULT_PROMPT_VERSION = "v4"
MAX_REPAIRS = 1
MAX_CHEAPER_RETRIES = 1


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
    catalogue = catalogue or load_catalogue()
    allowed = allowed_catalogue(catalogue, request.diet, request.allergies, request.disliked)

    system, user_message = render_prompt(prompt_version, request, allowed)
    messages = [{"role": "user", "content": user_message}]
    trace = []  # what happened at each model call, kept for transparency and for evaluation
    repairs_left, cheaper_left = MAX_REPAIRS, MAX_CHEAPER_RETRIES
    plan = lines = check = None

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
            if repairs_left == 0:
                return _result("invalid_plan", request, prompt_version, trace, catalogue)
            repairs_left -= 1
            messages.append({"role": "user", "content": _repair_message(problems)})
            continue

        if not plan.feasible:
            trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "model_says_infeasible"})
            return _result("infeasible", request, prompt_version, trace, catalogue, plan=plan, lines=lines, check=check)

        lines = build_shopping_list(plan.needs, allowed, request.already_have)
        check = check_budget(lines, round(request.budget_eur * 100))
        trace.append({"call": len(trace) + 1, "seconds": seconds, "result": "priced", "total_cents": check.total_cents})

        if check.within_budget:
            return _result("ok", request, prompt_version, trace, catalogue, plan, lines, check)
        if cheaper_left == 0:
            return _result("over_budget", request, prompt_version, trace, catalogue, plan, lines, check)
        cheaper_left -= 1
        messages.append({"role": "user", "content": _cheaper_message(check, lines, catalogue)})


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


def _result(status, request, prompt_version, trace, catalogue, plan=None, lines=None, check=None) -> dict:
    language = request.language

    def name(ingredient_id):
        product = catalogue[ingredient_id]
        return product.name_es if language == "es" else product.name_en

    result = {
        "status": status,  # ok | over_budget | infeasible | invalid_plan
        "prompt_version": prompt_version,
        "prices": snapshot_info(),
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
        result["meals"] = [
            {
                "day": meal.day,
                "meal": meal.meal,
                "recipe_name": meal.recipe_name,
                "servings": meal.servings,
                "ingredients": [{**asdict(need), "name": name(need.ingredient_id)} for need in meal.ingredients],
                "steps": list(meal.steps),
            }
            for meal in sorted(plan.meals, key=lambda m: (m.day, ("breakfast", "lunch", "dinner").index(m.meal)))
        ]
    if lines and check and plan and plan.feasible:
        result["shopping_list"] = [
            {
                **asdict(line),
                "name": name(line.ingredient_id),
                "package_size": catalogue[line.ingredient_id].package_size,
                "package_unit": catalogue[line.ingredient_id].package_unit,
                "package_price_cents": catalogue[line.ingredient_id].package_price_cents,
                "category": catalogue[line.ingredient_id].category,
                # What the unused part of the packages is worth: money spent on food not in the plan.
                "leftover_cents": round(line.cost_cents * line.leftover / line.bought) if line.bought else 0,
            }
            for line in lines
        ]
        result["budget"] = asdict(check)
        result["summary"] = _summary(request, plan, result["shopping_list"], check)
        if not check.within_budget:
            result["code_suggestions"] = _code_suggestions(request, check, lines)
    return result
