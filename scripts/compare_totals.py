"""Compare the total the model estimated with the total our code computed.

Used for the x1 experiment (prompts/x1_model_total.md), where the model is asked
to add up the packages itself and write the sum in "estimated_total_eur".

Usage:
    python3 scripts/compare_totals.py outputs/eval_x1_<date>.json
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.catalogue import allowed_catalogue, load_catalogue  # noqa: E402
from src.plan import PlanFormatError, extract_json, parse_plan, validate_plan  # noqa: E402
from src.shopping import build_shopping_list, total_cost_cents  # noqa: E402

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from evaluate_prompt import to_request  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in json.loads((REPO_ROOT / "tests" / "prompt_cases.json").read_text(encoding="utf-8"))}
    catalogue = load_catalogue()

    print(f"{'case':32} {'budget':>7} {'model says':>10} {'code says':>10} {'error':>8}")
    rows = []
    for entry in report:
        request = to_request(cases[entry["case"]]["request"])
        allowed = allowed_catalogue(catalogue, request.diet, request.allergies, request.disliked)
        reply = entry["first_reply"]
        try:
            data = extract_json(reply)
            plan = parse_plan(reply)
        except PlanFormatError:
            print(f"{entry['case']:32} {request.budget_eur:7.2f} {'no json':>10}")
            continue
        model_total = data.get("estimated_total_eur")
        if not plan.feasible or validate_plan(plan, request, catalogue, allowed):
            print(f"{entry['case']:32} {request.budget_eur:7.2f} {str(model_total):>10} {'not priced':>10}")
            continue
        code_total = total_cost_cents(build_shopping_list(plan.needs, allowed, request.already_have)) / 100
        error = None if model_total is None else code_total - float(model_total)
        rows.append((entry["case"], request.budget_eur, model_total, code_total, error))
        error_text = "-" if error is None else f"{error:+.2f}"
        print(f"{entry['case']:32} {request.budget_eur:7.2f} {str(model_total):>10} {code_total:10.2f} {error_text:>8}")

    errors = [abs(r[4]) for r in rows if r[4] is not None]
    if errors:
        under = sum(1 for r in rows if r[4] is not None and r[4] > 0)
        print(f"\nPriced plans: {len(errors)}. Model underestimated the real cost in {under} of them. "
              f"Average absolute error: {sum(errors) / len(errors):.2f} EUR.")


if __name__ == "__main__":
    main()
