"""Score one prompt version against the test cases in tests/prompt_cases.json.

Usage:
    python3 scripts/evaluate_prompt.py v3
    python3 scripts/evaluate_prompt.py v3 --cases basic,sycophancy
    python3 scripts/evaluate_prompt.py v3 --fake      (no API key: checks the script itself)

Every case is run through the real pipeline. We score the model's FIRST reply
(what the prompt achieves alone) and the FINAL result (after code repairs).
Results are saved in outputs/ and a Markdown row is printed for docs/prompt-log.md.

Each run makes 10 to 30 model calls, so it costs a little money. Do not loop it.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.catalogue import allowed_catalogue, load_catalogue  # noqa: E402
from src.plan import PlanFormatError, PlanRequest, parse_plan, validate_plan  # noqa: E402
from src.llm import DEFAULT_MODEL  # noqa: E402
from src.planner import generate_plan  # noqa: E402
from src.shopping import build_shopping_list, check_budget  # noqa: E402

RUBRIC = [
    ("json", "First reply is valid JSON in our format"),
    ("real", "First reply uses no invented ingredient"),
    ("safe", "First reply uses no forbidden ingredient (diet, allergy, dislike)"),
    ("complete", "First reply has every meal, right servings, right units"),
    ("budget", "First reply is within budget when priced by code (or honestly says infeasible when expected)"),
    ("final", "Final status is the expected one"),
]


def to_request(data: dict) -> PlanRequest:
    data = dict(data)
    for key in ("allergies", "disliked", "already_have"):
        data[key] = frozenset(data.get(key, []))
    data["meals"] = tuple(data["meals"])
    return PlanRequest(**data)


def score_first_reply(reply: str, request: PlanRequest, expect: str, catalogue: dict) -> dict:
    allowed = allowed_catalogue(catalogue, request.diet, request.allergies, request.disliked)
    scores = dict.fromkeys(("json", "real", "safe", "complete", "budget"), False)
    try:
        plan = parse_plan(reply)
    except PlanFormatError:
        return scores
    scores["json"] = True
    if not plan.feasible:
        honest = expect == "infeasible"
        return {**scores, "real": True, "safe": True, "complete": honest, "budget": honest}

    problems = validate_plan(plan, request, catalogue, allowed)
    scores["real"] = not any(p.startswith("UNKNOWN_INGREDIENT") for p in problems)
    scores["safe"] = not any(p.startswith("FORBIDDEN_INGREDIENT") for p in problems)
    scores["complete"] = not problems
    if not problems and expect == "ok":
        lines = build_shopping_list(plan.needs, allowed, request.already_have)
        scores["budget"] = check_budget(lines, round(request.budget_eur * 100)).within_budget
    return scores


def fake_model(system, messages):
    return json.dumps({"feasible": False, "reason": "fake model", "meals": [], "suggestions": []})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version", help="prompt version, for example v3")
    parser.add_argument("--cases", help="comma-separated case ids (default: all)")
    parser.add_argument("--fake", action="store_true", help="use a fake model instead of the API")
    args = parser.parse_args()

    if args.fake:
        model = fake_model
    else:
        from dotenv import load_dotenv

        load_dotenv()
        from src.llm import call_claude as model

    catalogue = load_catalogue()
    cases = json.loads((REPO_ROOT / "tests" / "prompt_cases.json").read_text(encoding="utf-8"))
    if args.cases:
        cases = [case for case in cases if case["id"] in args.cases.split(",")]

    report = []
    for case in cases:
        request = to_request(case["request"])
        replies = []

        def recording_model(system, messages):
            replies.append(model(system, messages))
            return replies[-1]

        result = generate_plan(request, recording_model, prompt_version=args.version, catalogue=catalogue)
        scores = score_first_reply(replies[0], request, case["expect"], catalogue)
        scores["final"] = result["status"] == case["expect"]
        row = {
            "case": case["id"],
            "expect": case["expect"],
            "status": result["status"],
            "scores": scores,
            "points": sum(scores.values()),
            "model_calls": len(replies),
            "seconds": [step.get("seconds") for step in result["trace"]],
            "total_eur": result["budget"]["total_cents"] / 100 if result["budget"] else None,
            "summary": result["summary"],
            "trace": result["trace"],
            "first_reply": replies[0],
        }
        report.append(row)
        marks = " ".join(f"{name}:{'Y' if scores[name] else 'N'}" for name, _ in RUBRIC)
        print(f"{case['id']:<32} {row['points']}/6  {marks}  status={result['status']} calls={len(replies)}")

    total, maximum = sum(r["points"] for r in report), 6 * len(report)
    out_dir = REPO_ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"eval_{args.version}_{datetime.now():%Y%m%d_%H%M%S}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    column = {name: sum(r["scores"][name] for r in report) for name, _ in RUBRIC}
    calls = sum(r["model_calls"] for r in report)
    seconds = [sec for r in report for sec in r["seconds"] if sec]
    model_name = "fake" if args.fake else os.environ.get("PLANNER_MODEL") or DEFAULT_MODEL
    print(f"\nModel: {model_name}. Average {sum(seconds) / len(seconds):.1f} s per model call." if seconds else "")
    priced = [r for r in report if r["summary"]]
    if priced:
        def average(key):
            return sum(r["summary"][key] for r in priced) / len(priced)

        waste = sum(r["summary"]["leftover_value_cents"] for r in priced) / sum(r["total_eur"] * 100 for r in priced)
        print(
            f"\nQuality of the {len(priced)} priced plans (not part of the score): "
            f"reuse ratio {average('reuse_ratio'):.2f}, "
            f"{average('cost_per_serving_cents') / 100:.2f} EUR per serving, "
            f"{waste:.0%} of the money goes to leftovers"
        )
    print(f"\nSaved {out_path.relative_to(REPO_ROOT)}")
    print("\nRow for docs/prompt-log.md:")
    print(f"| {args.version} | {datetime.now():%Y-%m-%d} | " + " | ".join(f"{column[name]}/{len(report)}" for name, _ in RUBRIC) + f" | {total}/{maximum} | {calls} |")


if __name__ == "__main__":
    main()
