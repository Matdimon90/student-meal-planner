"""Load a prompt version from prompts/ and fill in its placeholders.

Prompts live in their own files, not in Python strings, so a prompt change
shows up as its own diff and can be reviewed without reading code.
"""

from pathlib import Path

from src.plan import PlanRequest

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


def catalogue_lines(allowed: dict, language: str, with_prices: bool) -> str:
    lines = []
    for product in allowed.values():
        name = product.name_es if language == "es" else product.name_en
        unit = product.recipe_unit
        if product.piece_grams:
            unit = f"g (1 piece = {product.piece_grams:g} g)"
        line = f"{product.ingredient_id} | {name} | {unit}"
        if with_prices:
            line += f" | {product.package_size:g} {product.package_unit} | {product.package_price_cents / 100:.2f}"
        lines.append(line)
    return "\n".join(lines)


def clean_notes(notes: str) -> str:
    """Stop the user's free text from closing our <user_notes> block early."""
    return notes.replace("<", "(").replace(">", ")").strip() or "none"


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
    }
    for key, value in values.items():
        system = system.replace("{{" + key + "}}", value)
        template = template.replace("{{" + key + "}}", value)
    return system, template
