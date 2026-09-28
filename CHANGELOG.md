# Changelog

All notable changes to this project are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Repo hygiene: MIT `LICENSE`, issue templates, this changelog, and a CI badge in the README.

## [0.1.0] — 2026-09-23

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

[Unreleased]: https://github.com/Matdimon90/student-meal-planner/compare/main...HEAD
