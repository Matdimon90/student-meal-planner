# Decisions and changes of direction

Short notes on the choices that shaped the project, in order.

## 1. We changed idea

Our first idea ("4yourfridge") was an app that recognises food in a photo of your fridge and suggests dishes. We dropped it and kept the theme (students and food), moving to a problem we have every week: what to cook, what to buy, and whether the budget allows it.

_Team: write here, in your own words, why you dropped the fridge idea._

## 2. No live supermarket prices

We looked for a price API. There is no official one for Mercadona, Dia, Carrefour or Lidl. Mercadona's website has an internal API that people use unofficially, but its `robots.txt` blocks `/api`, it can change without notice, and a demo that breaks on the day of the defence is a bad trade. We use a dated extract of the open [OpenCesta](https://github.com/ruvelro/opencesta) dataset instead. Details and limits: [`data/README.md`](../data/README.md).

## 3. One supermarket first

Every extra supermarket means mapping 86 ingredients to products again. Mercadona only for the MVP. The data format already has `supermarket` and `zone` columns, so adding Dia later is a data task, not a code change.

## 4. The model never touches the money

See [`ai-approach.md`](ai-approach.md). Quantities, package rounding, totals and the budget verdict are plain Python with tests.

## 5. Ingredient ids instead of free text

The model must pick `ingredient_id` values from our catalogue instead of writing "2 onions". This removes the fuzzy matching problem between recipe words and shop products, and makes invented ingredients easy to detect.

## 6. Python backend, one static page

FastAPI for the API because Python is what the course teaches and what all three of us can explain. The page is a single HTML file with no framework and no build step. Preferences are saved in the browser, so there are no user accounts and no database.

## 7. An access code on the public site

Each plan costs real money in model calls. When `ACCESS_CODE` is set on the server, only people who know it can generate plans.

## 8. How we used AI to build this

Code was written with Claude as a coding assistant, in small slices. Each slice went through a branch, a pull request and a review by a teammate who had to understand it before approving. Prompt experiments were run and written up by us.
