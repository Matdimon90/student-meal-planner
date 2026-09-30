# Decisions and changes of direction

Short notes on the choices that shaped the project, in order.

## 1. We changed idea

Our first idea ("4yourfridge") was an app that recognises food in a photo of your fridge and suggests dishes. We dropped it and kept the theme (students and food), moving to a problem we have every week: what to cook, what to buy, and whether the budget allows it.

_Team: We dropped it because the photo recognition would have been the whole project: an ingredient classifier is hard to make reliable in one week, and a wrong detection ("chicken" instead of "tofu") makes every suggestion wrong. Budget was also missing from the idea, and budget is what actually decides what a student cooks. The meal planner keeps the useful part (help us decide what to cook) and adds the part we care about (does it fit in the money we have).

## 2. No live supermarket prices

We looked for a price API. There is no official one for Mercadona, Dia, Carrefour or Lidl. Mercadona's website has an internal API that people use unofficially, but its `robots.txt` blocks `/api`, it can change without notice, and a demo that breaks on the day of the defence is a bad trade. We use a dated extract of the open [OpenCesta](https://github.com/ruvelro/opencesta) dataset instead. Details and limits: [`data/README.md`](../data/README.md).

## 3. One supermarket first, then a second one the same way

Every extra supermarket means mapping 86 ingredients to products again, so the MVP shipped with Mercadona only. The data format already had `supermarket` and `zone` columns on purpose. Adding Dia was then a data task, not a code change: one mapping file (`data/skus_dia.csv`), one run of the same script, one more `prices_*.csv`. What Dia does not sell (tofu) is simply absent from its snapshot, and the app says "not sold there" instead of guessing a price.

Choosing the supermarket became the first screen of the app, and because every shop uses the same ingredient ids, the same meal plan can be priced in every shop by code: no second model call, just different packages.

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

## 9. Pieces or grams: a problem we moved from the prompt to the code

Three prompt versions could not stop the model writing "banana: 2 ud" when our catalogue sells bananas by weight. The evaluation log showed the same failure in v2, v3 and v4, and v5 only fixed it by listing gram equivalents in the prompt, at the cost of everything else. So we fixed it where it belongs: `data/staples.csv` now has an average `piece_grams` for produce people count rather than weigh, and the code accepts both "2 ud" and "360 g" for those products. The prompt still says grams; the validator no longer punishes a natural answer.

## 10. A step-by-step form, and the model aims while the code counts

The first page was one long form. We replaced it with one question per screen (shop, people, days, budget, styles, diet and allergies, plate, protein, dislikes, what is at home, kitchen), like the meal-planning apps students already use, because a long form hides the questions that matter. The new answers go to the model through prompt v7. What can be checked is checked in code: calories and protein are counted from `data/nutrition.csv` and the model gets one retry when meals miss the target, recipes that need an appliance the user does not have are rejected, and the "protein" label is set from the counted grams. When a tight budget and a protein target cannot both be met, the budget wins and the page says how many plates reach the target.

## 11. Dish photos from a library, not generated

Each meal card shows a photo, like the apps we took the idea from. Generating one image per recipe would cost money and seconds on every plan, and could show a dish that looks nothing like what the student will cook. We chose 48 free photos from Unsplash (credits in `public/img/dishes/CREDITS.md`) and let the code pick one from the recipe name and ingredients (`src/photos.py`). The photo shows the kind of dish, not the exact recipe, and the footer says so.
