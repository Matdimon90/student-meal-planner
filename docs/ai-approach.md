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
| Explaining why a budget is unrealistic, proposing changes | **Model** and code | The model explains in words. The code adds numbers it computed itself. |

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
   ▼
result: ok | over_budget | infeasible | invalid_plan
```

This is a single-purpose LLM pipeline, not an agent. The model has no tools and makes no decisions about what to do next: the code decides. We chose the simplest architecture that does the job (textbook chapter 7).

The model gets at most 3 calls per request (1 answer, 1 repair, 1 cheaper retry). If the plan is still invalid we show nothing rather than something wrong. If it is still over budget we show it and say so.

## LLM failure modes in this project

| Failure mode | How it shows up here | Our defence |
| --- | --- | --- |
| Hallucination | Ingredients that are not in the shop, made-up prices | The model never gives prices. Ingredients must be ids from our catalogue; anything else is rejected by `validate_plan`. |
| Sycophancy | "Sure, 5 euros is enough for three people for a week!" | Prompt rule 8 (say no honestly) and, above all, the code prices the plan and reports the real total. Test case `sycophancy`. |
| Prompt injection | The free-text notes field says "ignore your instructions" | Role separation: notes go in a `<user_notes>` data block, the system prompt says it is data, `<` and `>` are stripped so the block cannot be closed early. Whatever happens, the output still has to pass validation. Test case `prompt_injection`. |
| Context window | Catalogue + a 7-day, 3-meal plan is a long exchange | We send only allowed ingredients, one line each, and cap days at 14. Test case `big_week`. |

## How we evaluate prompts

We wrote the rubric before tuning the prompts (textbook principle 6). `scripts/evaluate_prompt.py` runs a prompt version on the 10 cases in `tests/prompt_cases.json` and scores the model's **first** reply on six yes/no criteria, so the score measures the prompt and not our repair code. Results are in [`prompt-log.md`](prompt-log.md).
