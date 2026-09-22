# Prompt log

Problem → Prompt → Output → Evaluation → Improvement.

Each version is a file in [`prompts/`](../prompts). Scores come from `python3 scripts/evaluate_prompt.py <version>` (10 cases, 6 criteria each, first reply only). Raw outputs of each run are saved in `outputs/` (not committed; the interesting ones are quoted below).

## Rubric

| Column | Criterion |
| --- | --- |
| json | First reply is valid JSON in our format |
| real | No invented ingredient |
| safe | No forbidden ingredient (diet, allergy, dislike) |
| complete | Every meal present, right servings, right units |
| budget | Within budget when priced by our code, or honestly infeasible when that is the right answer |
| final | Final status after repairs is the expected one |

## Scores

| Version | Date | json | real | safe | complete | budget | final | Total | Model calls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _paste the row printed by the script here, one per run_ | | | | | | | | | |

### Quality of the plans (not part of the score)

The script also prints three numbers for the plans that could be priced. They show whether a prompt makes *better* plans, not just valid ones.

| Version | Reuse ratio (recipes per ingredient) | EUR per serving | Share of money spent on leftovers |
| --- | --- | --- | --- |
| _fill in_ | | | |

Model and settings used for all runs: _fill in (model name; no temperature setting exists in the current SDK, so runs are not exactly repeatable: run important comparisons twice)_.

## v1 — zero-shot baseline

**Problem.** We need a starting point to measure against.

**Prompt.** One loose instruction, ingredient ids listed, "answer in JSON".

**What we expected.** Replies we cannot parse, invented field names, wrong units.

**What happened.** _Fill in after running. Quote one bad reply._

**What we changed next and why.** _Fill in._

## v2 — structured output

**Problem.** _Fill in from v1 results._

**Prompt.** Exact JSON shape, unit rule, servings rule, catalogue with units.

**What happened.** _Fill in._

**What we changed next and why.** _Fill in._

## v3 — constraints and role separation

**Problem.** _Fill in from v2 results (we expect: over-budget plans, many half-used packages, agreeing to impossible budgets)._

**Prompt.** Package sizes and prices shown, 9 explicit rules, honesty rule, user notes isolated in a data block, recipe language.

**What happened.** _Fill in. Look closely at the `sycophancy`, `impossible_budget` and `prompt_injection` cases._

**What we changed next and why.** _Fill in._

## v4 — few-shot

**Problem.** _Fill in from v3 results._

**Prompt.** v3 plus two worked examples: one cheap plan that reuses ingredients, one honest refusal.

**What happened.** _Fill in. Did the reuse ratio go up? Did the model copy the example recipes too often?_

## Model comparison (speed vs quality)

The first real runs with `claude-sonnet-5` took a long time per plan (fill in: how long). We switched the default to `claude-haiku-4-5-20251001`. Run the evaluation with both (`PLANNER_MODEL=... python3 scripts/evaluate_prompt.py v4`) and record score, seconds per call (in the `trace` of the outputs file) and plan quality here.

| Model | Score | Avg seconds per call | Reuse ratio | Notes |
| --- | --- | --- | --- | --- |
| claude-sonnet-5 | | | | |
| claude-haiku-4-5-20251001 | | | | |

## Experiments that did not work

_At least one. Ideas to try on a branch `prompt/...`: asking the model to compute the total itself and comparing with the code's total; a heavy persona; removing rule 4 to see what it was doing; letting the API enforce the JSON format (`output_config` with a JSON schema) instead of asking for it in the prompt._

## What would happen if we removed...

_The teacher may ask this. Pick two rules from v3, remove each one, run the evaluation, write the result here._
