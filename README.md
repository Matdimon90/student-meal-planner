# Student Meal Planner

AI meal planner and grocery budgeting for students living in Spain.

Give it a budget, a number of people and days, and what you cannot or will not eat. Pick your supermarket (Mercadona or Dia). It returns a meal plan, simple recipes, and a shopping list priced with that shop's real packages, compared with your budget, plus what the same basket would cost in the other shop. If the budget is not realistic, it says so.

Course project for DAT32-91 Prompt Engineering & Git, Albert School.

## Objective

Students cooking on a tight budget answer three questions every week: what do I cook, what do I buy, can I afford it? Recipe sites ignore the budget. Budget apps ignore the recipes. Neither knows that 100 g of rice still costs a full 1 kg bag.

Our goal: one tool that plans meals **and** tells the truth about what they cost at the till.

The project started as a different idea (recognising food in a fridge photo). Why we changed: [`docs/decisions.md`](docs/decisions.md).

## Team

| Name | GitHub |
| --- | --- |
| Matteo Asscher | [@Matdimon90](https://github.com/Matdimon90) |
| Oscar Khalil | [@oskr-kal](https://github.com/oskr-kal) |
| Tom Makhlouf | [@TomMakhlouf](https://github.com/TomMakhlouf) |

How we work together: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Tools

| Tool | Role |
| --- | --- |
| Python 3, FastAPI | Backend and all calculations |
| HTML, CSS, JavaScript (one file, no framework) | Web page, English and Spanish |
| Anthropic API (Claude Haiku 4.5 by default, Sonnet 5 optional) | Proposes meals and recipes as JSON |
| OpenCesta open dataset | Real Mercadona and Dia prices, dated snapshot |
| pytest | Automated tests |
| Git, GitHub (issues, branches, pull requests, reviews) | Collaboration and project history |
| Vercel | Hosting |
| Claude (assistant) | Coding assistant, see "AI usage" |

## Installation

You need Python 3.9 or newer, Git, and an Anthropic API key.

```
git clone https://github.com/Matdimon90/student-meal-planner.git
cd student-meal-planner
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env               # then open .env and paste your API key (and workspace id if Anthropic asks for one)
```

Run the tests (no API key needed, the model is faked):

```
python3 -m pytest
```

Start the app:

```
uvicorn app:app --reload
```

Open http://127.0.0.1:8000, fill in the form, press "Plan my meals". A plan takes up to a minute.

Online version: _(Vercel link, to add)_. It may ask for an access code, because every plan costs us model calls.

## Project structure

```
app.py                  web entry point (FastAPI): /api/options, /api/plan
public/index.html       the web page (EN/ES)
src/
  shopping.py           quantities, whole packages, total, budget check   (no AI)
  catalogue.py          load prices, filter by diet / allergies / dislikes (no AI)
  plan.py               request rules, parsing and checking the model's answer (no AI)
  prompting.py          loads a prompt version and fills it in
  llm.py                the only file that calls the model API
  planner.py            the pipeline that ties everything together
prompts/                one file per prompt version (v1 to v4) + README
data/                   price snapshot, our ingredient list, source and limits
scripts/                build the price snapshot, evaluate a prompt version
tests/                  automated tests + the 10 prompt test cases
docs/                   AI approach, prompt log, decisions, failures
outputs/                evaluation results (generated, not committed)
```

## AI usage

**In the product.** The model proposes meals, quantities and steps as JSON, choosing only from our ingredient catalogue. Python checks the answer, builds the shopping list, prices it and decides whether the budget is respected. The model never calculates the total. Full explanation, pipeline diagram and the LLM failure modes we handle: [`docs/ai-approach.md`](docs/ai-approach.md).

**Prompt engineering.** Four prompt versions (zero-shot → structured output → constraints and role separation → few-shot), each scored with the same rubric on the same 10 test cases, including an impossible budget, a sycophancy trap and a prompt injection. Scores and what we learned: [`docs/prompt-log.md`](docs/prompt-log.md).

**In development.** Code was written with Claude as a coding assistant, in small slices. Every slice went through a branch, a pull request and a review by a teammate who had to understand it before approving. We ran and wrote up the prompt experiments ourselves.

## Main challenges

- No supermarket offers a price API. We use a dated open-data snapshot and say so everywhere.
- Models are unreliable with money. We moved every calculation into tested code.
- Models invent ingredients and agree too easily. We validate every answer and price it ourselves.
- _(Add the real ones as they happen.)_ Full list: [`docs/failures.md`](docs/failures.md).

## Final result

_(To complete at the end: what works today, a screenshot, the final evaluation score.)_

## Limitations

- Prices are frozen on 2026-09-21: Mercadona (Madrid online zone) and Dia (national online shop). Shelf prices will differ. Dia sells no tofu online, so vegan plans priced at Dia may miss one ingredient; the app says so.
- 86 ingredients, one product per ingredient, usually the cheapest store brand.
- Allergen and diet tags were written by us, not read from labels. **Always check the label.**
- Recipes come from an AI model and are not tested in a kitchen. Quantities are checked for plausibility only.
- No nutrition information.

## Future improvements

- More supermarkets (Dia is already in the same dataset) and automatic weekly price refresh.
- Carry leftovers from one week to the next.
- Nutrition targets (protein, calories).
- Let the user swap a single meal without regenerating the whole plan.
