"""Shopping list maths. No AI in this file.

The language model proposes meals and how much of each ingredient they need.
Everything that has to be exactly right is done here in plain Python:
adding up quantities, rounding up to whole packages, pricing, and comparing
the total with the budget.

Money is handled in integer cents to avoid floating point surprises
(0.1 + 0.2 != 0.3 in Python).
"""

import math
from dataclasses import dataclass

# Recipes use small units (g, ml, ud). The shop sells in big ones (kg, l, ud).
# Everything is converted to a base unit before any calculation.
TO_BASE_UNIT = {
    "g": ("g", 1),
    "kg": ("g", 1000),
    "ml": ("ml", 1),
    "l": ("ml", 1000),
    "ud": ("ud", 1),
}


class ShoppingError(ValueError):
    """Raised when a plan cannot be priced (unknown ingredient, wrong unit...)."""


@dataclass(frozen=True)
class Product:
    """One row of the price snapshot: what the shop actually sells."""

    ingredient_id: str
    name_en: str
    name_es: str
    package_price_cents: int
    package_size: float
    package_unit: str  # "kg", "l" or "ud"


@dataclass(frozen=True)
class IngredientNeed:
    """One ingredient line of one recipe, as proposed by the model."""

    ingredient_id: str
    quantity: float
    unit: str  # "g", "ml" or "ud" ("kg" and "l" are accepted too)


@dataclass(frozen=True)
class ShoppingLine:
    """One line of the final shopping list."""

    ingredient_id: str
    needed: float  # in base unit (g, ml or ud)
    base_unit: str
    packages: int
    bought: float  # in base unit
    leftover: float  # bought - needed
    cost_cents: int
    already_have: bool  # True = not counted in the total


@dataclass(frozen=True)
class BudgetCheck:
    total_cents: int
    budget_cents: int
    difference_cents: int  # positive = money left, negative = over budget
    within_budget: bool


def to_base(quantity: float, unit: str) -> tuple[float, str]:
    """Convert a quantity to its base unit: 1.5 kg -> (1500, "g")."""
    if unit not in TO_BASE_UNIT:
        raise ShoppingError(f"Unknown unit '{unit}'. Allowed: {sorted(TO_BASE_UNIT)}")
    if quantity <= 0:
        raise ShoppingError(f"Quantity must be positive, got {quantity}")
    base_unit, factor = TO_BASE_UNIT[unit]
    return quantity * factor, base_unit


def consolidate(needs: list[IngredientNeed], catalogue: dict[str, Product]) -> dict[str, float]:
    """Add up every recipe's needs into one total per ingredient (base units).

    This is what makes ingredient reuse visible: rice used in three recipes
    becomes a single line, so we buy one bag instead of three.
    """
    totals: dict[str, float] = {}
    for need in needs:
        product = catalogue.get(need.ingredient_id)
        if product is None:
            raise ShoppingError(f"'{need.ingredient_id}' is not in the price catalogue")

        quantity, base_unit = to_base(need.quantity, need.unit)
        _, product_base_unit = to_base(product.package_size, product.package_unit)
        if base_unit != product_base_unit:
            raise ShoppingError(
                f"'{need.ingredient_id}' is sold in {product.package_unit} "
                f"but the recipe asks for {need.unit}"
            )
        totals[need.ingredient_id] = totals.get(need.ingredient_id, 0) + quantity
    return totals


def build_shopping_list(
    needs: list[IngredientNeed],
    catalogue: dict[str, Product],
    already_have: frozenset[str] = frozenset(),
) -> list[ShoppingLine]:
    """Turn recipe needs into whole packages to buy, with their cost.

    `already_have` lists ingredients the user has at home (salt, oil...).
    They stay on the list for information but cost nothing.
    """
    lines = []
    for ingredient_id, needed in sorted(consolidate(needs, catalogue).items()):
        product = catalogue[ingredient_id]
        package_size, base_unit = to_base(product.package_size, product.package_unit)
        have_it = ingredient_id in already_have

        # You cannot buy 0.3 of a bag of rice: always round up to whole packages.
        # The tiny tolerance stops 2.0000000001 from becoming 3 packages.
        packages = 0 if have_it else math.ceil(needed / package_size - 1e-9)
        bought = packages * package_size

        lines.append(
            ShoppingLine(
                ingredient_id=ingredient_id,
                needed=needed,
                base_unit=base_unit,
                packages=packages,
                bought=bought,
                leftover=0 if have_it else bought - needed,
                cost_cents=packages * product.package_price_cents,
                already_have=have_it,
            )
        )
    return lines


def total_cost_cents(lines: list[ShoppingLine]) -> int:
    return sum(line.cost_cents for line in lines)


def check_budget(lines: list[ShoppingLine], budget_cents: int) -> BudgetCheck:
    """Compare the real shopping total with the budget. Never rounds in the user's favour."""
    if budget_cents <= 0:
        raise ShoppingError("Budget must be positive")
    total = total_cost_cents(lines)
    return BudgetCheck(
        total_cents=total,
        budget_cents=budget_cents,
        difference_cents=budget_cents - total,
        within_budget=total <= budget_cents,
    )


def euros_to_cents(euros: float) -> int:
    return round(euros * 100)


def format_euros(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d} €"
