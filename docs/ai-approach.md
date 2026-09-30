# AI approach

## The one rule

**The model is creative. The code is the judge.**

A language model is good at inventing sensible recipes from a list of ingredients. It is bad at arithmetic, it can invent things that do not exist, and it tends to agree with the user. So every task that must be exactly right is done by ordinary Python.

| Task | Who does it | Why |
| --- | --- | --- |
| Checking the user's input (budget, people, days...) | Code (`src/plan.py`) | Rules are fixed. No reason to pay for a model call. |
| Removing ingredients the user cannot eat | Code (`src/catalogue.py`) | Safety. The model never even sees forbidden ingredients. |
| Choosing meals, quantities and cooking steps | **Model** | Open-ended, creative, language-dependent. |
| Writing recipes in English or Spanish | **Model** | Natural language generation. |
| Checking the model's answer (invented ingredients, units, missing meals) | Code (`src/plan.py`) | The model's output is never trusted as it comes. |
| Adding quantities, rounding up to whole packages, total cost | Code (`src/shopping.py`) | Arithmetic must be exact. Done in integer cents. |
| Deciding whether the budget is respected | Code (`src/shopping.py`) | The model must not grade its own work. |
| Pricing the same plan in another supermarket | Code (`src/planner.py`) | Same ingredient ids, other packages: arithmetic again, no new model call. |
| Explaining why a budget is unrealistic, proposing changes | **Model** and code | The model explains in words. The code adds numbers it computed itself. |
| Following the user's styles, plate size and protein target | **Model** | Choosing and sizing dishes is creative work. It gets the kcal and protein of every ingredient in the catalogue (prompt v7). |
| Counting calories and protein per plate, checking the targets | Code (`src/nutrition.py`) | Same reason as the prices: the model under-counts (see the v7 entry of the prompt log). |
| Refusing recipes that need an appliance the user does not have | Code (`src/plan.py`) | A rule in the prompt is a request; the check on the steps is a guarantee. |
| The "protein" label, the price of each meal, the dish photo | Code (`src/planner.py`, `src/shopping.py`, `src/photos.py`) | A label that makes a claim about a number is decided by the number. Photos come from our own library, picked from the recipe name. |

## The pipeline

```
user request
   │  code: validate input
   │  code: filter catalogue (diet, allergies, dislikes)
   ▼
MODEL: propose a plan as JSON  ◄────────────────┐
   │  code: parse + validate                    │ one repair request,
   │      problems? ────────────────────────────┘ listing the exact problems
   │  code: build shopping list, whole packages, total
   │      over budget? ─────► MODEL: one "make it cheaper" request with the real numbers
   │  code: count kcal and protein per plate
   │      targets missed? ──► MODEL: one "adjust these meals" request with the counted numbers;
   │                          the code keeps whichever plan misses fewer targets within budget
   ▼
result: ok | over_budget | infeasible | invalid_plan
```

This is a single-purpose LLM pipeline, not an agent. The model has no tools and makes no decisions about what to do next: the code decides. We chose the simplest architecture that does the job (textbook chapter 7).

The model gets at most 4 calls per request (1 answer, 1 repair, 1 cheaper retry, 1 nutrition retry, the last one only when the user set a plate or protein target). If the plan is still invalid we show nothing rather than something wrong. If it is still over budget we show it and say so.

### Swapping one meal

Replacing a single meal follows the same rule with a smaller model call. `swap_meal()` sends one request (`prompts/swap2_preferences.md` since v7, `prompts/swap_meal.md` before) that asks for one recipe only, and shows the other meals of the plan so that the new dish reuses packages they already open. Everything that must be exact stays in the code: the day, the meal slot and the number of servings are overwritten with the values we asked for instead of being read from the reply, `validate_plan` checks the new meal against the catalogue and the diet exactly as it checks a fresh plan, and the whole plan — the untouched meals included — is priced again from scratch, because one different recipe changes which packages the basket needs. The result has the same shape as a normal plan, so the page renders it the same way and the budget verdict comes from our arithmetic, never from the model.

## LLM failure modes in this project

| Failure mode | How it shows up here | Our defence |
| --- | --- | --- |
| Hallucination | Ingredients that are not in the shop, made-up prices | The model never gives prices. Ingredients must be ids from our catalogue; anything else is rejected by `validate_plan`. |
| Sycophancy | "Sure, 5 euros is enough for three people for a week!" | Prompt rule 8 (say no honestly) and, above all, the code prices the plan and reports the real total. Test case `sycophancy`. |
| Prompt injection | The free-text notes field says "ignore your instructions" | Role separation: notes go in a `<user_notes>` data block, the system prompt says it is data, `<` and `>` are stripped so the block cannot be closed early. Whatever happens, the output still has to pass validation. Test case `prompt_injection`. |
| Context window | Catalogue + a 7-day, 3-meal plan is a long exchange | We send only allowed ingredients, one line each, and cap days at 14. Test case `big_week`. |

## How we evaluate prompts

We wrote the rubric before tuning the prompts (textbook principle 6). `scripts/evaluate_prompt.py` runs a prompt version on the 10 cases in `tests/prompt_cases.json` and scores the model's **first** reply on six yes/no criteria, so the score measures the prompt and not our repair code. Results are in [`prompt-log.md`](prompt-log.md).
