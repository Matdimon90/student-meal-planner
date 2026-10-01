# Changelog

All notable changes to this project are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Optional Stripe payment: a pass bought through Stripe Checkout unlocks plan generation for 30 days (`/api/checkout`, `src/payment.py`). Off unless `STRIPE_SECRET_KEY` and `STRIPE_PRICE_ID` are set; the access code keeps working.

## [1.1.0] — 2026-09-30

### Added
- Step-by-step form, one question per screen: supermarket, people, days and meals, budget slider, meal styles, diet and allergies, plate size, protein target, ingredients to avoid, what is at home, kitchen equipment. Answers are remembered and can be edited from a Preferences tab.
- Prompt v7 (`prompts/v7_preferences.md`) and swap prompt `swap2_preferences.md`: the new preferences, kcal and protein columns in the catalogue, `minutes` and `tags` per meal. 58/60 on the rubric, like v4 and v6; now the shipped prompt.
- Calories and protein per plate, counted by code from `data/nutrition.csv`, and one retry when lunches or dinners miss the plate or protein target (the better plan within budget is kept).
- Recipes that need an appliance the user does not have (oven, microwave, air fryer, slow cooker) are rejected by code (`MISSING_EQUIPMENT`).
- Dish photos: 48 Unsplash photos in `public/img/dishes/`, picked by code from the recipe name and ingredients (`src/photos.py`).
- Price per meal (its share of the packages) and a "protein" label decided from the counted grams.
- Results in three tabs: the week as photo cards, a shopping list you can tick, and your answers.

### Changed
- `/api/options` lists the new preferences and each ingredient's diet and allergens; `/api/plan` and `/api/swap` accept `styles`, `portion`, `protein` and `equipment`.

### Fixed
- `/api/swap` always used the default swap prompt, whatever version was passed.

## [1.0.1] — 2026-09-28

### Fixed
- Leftover text from a merge conflict in `docs/failures.md` and `prompts/README.md`, outdated lines in `CONTRIBUTING.md` and `docs/presentation.md`.

## [1.0.0] — 2026-09-28

The version handed in for DAT32-91 Prompt Engineering & Git.

### Added
- Swap a single meal without regenerating the week: `/api/swap` and a one-recipe prompt (`prompts/swap_meal.md`). The code forces the day and servings, validates the new meal like a full plan and prices the whole basket again (#41, documented in #42).
- Download button for the shopping list, next to Copy and Print (#39).
- Prompt v6: the v4 rules with a second, pasta-and-lentils example (#40). It scored 58/60 like v4 but did not widen the menu, so v4 stays the shipped prompt (#55).
- Ablations x2 and x3: v3 without the reuse rule and without the honesty rule, with predictions written before the run. Both predictions were wrong: the retry message in the code turned out to be a second honesty defence (#50).
- Failures log: our Git mistakes (a pull request merged into the wrong branch, commits pushed straight to `main`, our first merge conflict) and the course brief kept out of the history (#51, #54).
- MIT licence for the code (the data in `data/` stays under ODbL), issue templates, this changelog and a CI badge in the README (#38).
- Plan for the final presentation and oral defence in `docs/presentation.md` (#52).

### Changed
- README: link to the live site, final result and the real challenges we met (#53).
- Prompt log: v6 results, the v4 re-run after the piece weights, and the Haiku speeds measured on every run instead of an empty model comparison (#55).
- `main` is protected: every change goes through a pull request, needs one approval and green tests.

### Fixed
- Oscar's surname in the README team table (#37).

## [0.1.0] — 2026-09-24

First working version, built for the DAT32-91 Prompt Engineering & Git course.

### Added
- Meal planner pipeline: the model proposes meals and ingredients as JSON; Python
  builds the shopping list, prices it in whole packages, and decides the budget verdict.
- Shopping maths (`src/shopping.py`): whole-package rounding, total cost, budget check.
- Catalogue loading and filtering by diet, allergies and dislikes (`src/catalogue.py`).
- Request validation and model-answer checking (`src/plan.py`).
- Repair and one cheaper-retry loop when a plan is invalid or over budget (`src/planner.py`).
- Two supermarkets, Mercadona and Dia, from dated OpenCesta snapshots, with the same
  basket priced in the other shop for comparison.
- Produce counted in pieces, converted to grams with an average piece weight.
- Bilingual (EN/ES) single-page web app: supermarket landing grid, week board, recipe dialog.
- FastAPI backend with `/api/options` and `/api/plan`, plus an optional access code.
- Prompt versions v1–v5 and the `x1` "model adds up the bill" experiment, scored on a shared
  rubric over 10 test cases (including impossible-budget, sycophancy and prompt-injection traps).
- Test suite (pytest) and a GitHub Actions workflow that runs it on every pull request.
- Project docs: AI approach, prompt log, decisions, failures.

[Unreleased]: https://github.com/Matdimon90/student-meal-planner/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/Matdimon90/student-meal-planner/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Matdimon90/student-meal-planner/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/Matdimon90/student-meal-planner/releases/tag/v0.1.0
