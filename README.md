# Student Meal Planner

AI meal planner and grocery budgeting for students living in Spain.

> Status: project kickoff. Nothing below "Run" works yet beyond the starter script.

## Objective

Students cooking on a tight budget have to answer three questions every week: what do I cook, what do I buy, and can I afford it?
This app takes a budget in euros, a number of people, a number of days and food preferences, and returns a meal plan, recipes, and a shopping list priced with real supermarket data, compared against the budget.

If the budget is not realistic, the app must say so and suggest adjustments instead of pretending it works.

## Team

- Matteo Asscher (@Matdimon90)
- Oscar (GitHub handle to add)
- Tom (GitHub handle to add)

## Current scope (MVP)

- One supermarket (Mercadona), using a dated snapshot of open price data. No live prices.
- The LLM proposes meals and ingredients. Ordinary Python code does all the maths: quantities, package sizes, totals, budget check, allergy filtering.
- English and Spanish.

## Tools

- Python 3
- An LLM API (provider to be confirmed)
- Git and GitHub for all collaboration
- Claude as a coding assistant (see "AI usage", to be written)

## Run

```
python3 src/main.py
```

Expected output:

```
Student Meal Planner starts successfully.
```

## Project structure

```
src/       application code
prompts/   prompt versions, one file per iteration
data/      price data snapshot and its source notes
tests/     automated tests and prompt test cases
docs/      AI approach, experiments, failures, decisions
outputs/   generated results (not committed)
```

## Still to write

AI usage, main challenges, final result, future improvements.
