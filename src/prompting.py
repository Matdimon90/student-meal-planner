"""Load a prompt version from prompts/ and fill in its placeholders.

Prompts live in their own files, not in Python strings, so a prompt change
shows up as its own diff and can be reviewed without reading code.
"""

from pathlib import Path

from src.nutrition import load_nutrition
from src.plan import PORTIONS, PROTEIN_TARGETS, PlanRequest

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SEPARATOR = "---USER---"


def load_prompt(version: str) -> tuple:
    """Return (system_prompt, user_template) for a version such as "v3"."""
    matches = sorted(PROMPTS_DIR.glob(f"{version}_*.md"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected exactly one prompt file for '{version}', found {len(matches)}")
    system, separator, user = matches[0].read_text(encoding="utf-8").partition(SEPARATOR)
    if not separator:
        raise ValueError(f"{matches[0].name} has no '{SEPARATOR}' line")
    return system.strip(), user.strip()


def catalogue_lines(allowed: dict, language: str, with_prices: bool, with_nutrition: bool = False) -> str:
    lines = []
    nutrition = load_nutrition() if with_nutrition else {}
    for product in allowed.values():
        name = product.name_es if language == "es" else product.name_en
        unit = product.recipe_unit
        if product.piece_grams:
            unit = f"g (1 piece = {product.piece_grams:g} g)"
        line = f"{product.ingredient_id} | {name} | {unit}"
        if with_prices:
            line += f" | {product.package_size:g} {product.package_unit} | {product.package_price_cents / 100:.2f}"
        if with_nutrition:
            _, kcal, protein = nutrition.get(product.ingredient_id, ("", 0, 0))
            line += f" | {kcal:g} | {protein:g}"
        lines.append(line)
    return "\n".join(lines)


def clean_notes(notes: str) -> str:
    """Stop the user's free text from closing our <user_notes> block early."""
    return notes.replace("<", "(").replace(">", ")").strip() or "none"


def preference_values(request: PlanRequest) -> dict:
    """The step-by-step form's answers, written as plain words for the prompt."""
    portion = PORTIONS[request.portion]
    protein = PROTEIN_TARGETS[request.protein]
    return {
        "styles": ", ".join(request.styles) or "no preference",
        "portion": (f"{request.portion}: {portion[0]} to {portion[1]} kcal per serving" if portion and portion[1]
                    else f"{request.portion}: at least {portion[0]} kcal per serving" if portion else "no preference"),
        "protein": f"at least {protein} g of protein per serving" if protein else "no preference",
        "equipment": ", ".join(sorted(e.replace("_", " ") for e in request.equipment)) or "a normal kitchen (hob, oven, microwave)",
    }


def render_prompt(version: str, request: PlanRequest, allowed: dict) -> tuple:
    """Return (system_prompt, user_message) ready to send to the model."""
    system, template = load_prompt(version)
    values = {
        "people": str(request.people),
        "days": str(request.days),
        "meals": ", ".join(meal for _, meal in request.slots[: len(request.meals)]),
        "budget": f"{request.budget_eur:.2f}",
        "diet": request.diet,
        "language": {"en": "English", "es": "Spanish"}[request.language],
        "already_have": ", ".join(sorted(request.already_have & set(allowed))) or "nothing",
        "notes": clean_notes(request.notes),
        "ingredient_ids": ", ".join(allowed),
        "catalogue_short": catalogue_lines(allowed, request.language, with_prices=False),
        "catalogue_full": catalogue_lines(allowed, request.language, with_prices=True),
        "catalogue_nutrition": catalogue_lines(allowed, request.language, with_prices=True, with_nutrition=True),
        **preference_values(request),
    }
    for key, value in values.items():
        system = system.replace("{{" + key + "}}", value)
        template = template.replace("{{" + key + "}}", value)
    return system, template


def render_swap_prompt(request: PlanRequest, allowed: dict, day: int, meal: str, current_recipe: str, other_meals: list, version: str = "swap") -> tuple:
    """Prompt to replace one meal. `other_meals` are the meals that stay, so the
    model can reuse the packages they already open. Returns (system, user_message)."""
    system, template = load_prompt(version)
    other_recipes = "\n".join(
        f"- day {m.day} {m.meal}: {m.recipe_name} ({', '.join(need.ingredient_id for need in m.ingredients)})"
        for m in sorted(other_meals, key=lambda m: (m.day, m.meal))
    )
    values = {
        "people": str(request.people),
        "diet": request.diet,
        "language": {"en": "English", "es": "Spanish"}[request.language],
        "already_have": ", ".join(sorted(request.already_have & set(allowed))) or "nothing",
        "notes": clean_notes(request.notes),
        "catalogue_full": catalogue_lines(allowed, request.language, with_prices=True),
        "catalogue_nutrition": catalogue_lines(allowed, request.language, with_prices=True, with_nutrition=True),
        **preference_values(request),
        "target_day": str(day),
        "target_meal": meal,
        "current_recipe": current_recipe or "none",
        "other_recipes": other_recipes or "none",
    }
    for key, value in values.items():
        system = system.replace("{{" + key + "}}", value)
        template = template.replace("{{" + key + "}}", value)
    return system, template
