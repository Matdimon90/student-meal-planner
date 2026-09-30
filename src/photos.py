"""Pick a photo for each meal. No AI in this file.

We ship a small library of dish photos (public/img/dishes/, credits in
CREDITS.md there). The model never chooses or invents an image: the code
reads the recipe name (English or Spanish) and its ingredients and picks the
closest photo. It is an illustration of the kind of dish, not a picture of
the exact recipe.
"""

import re
import unicodedata

# (photo, pattern on the recipe name). Checked in this order: the more specific first.
NAME_RULES = [
    ("tortilla", r"tortilla (de patatas?|espanola)|spanish (omelet\w*|tortilla)|potato omelet\w*"),
    ("shakshuka", r"shakshuka|huevos? (al plato|con tomate)|eggs? in tomato"),
    ("rice_egg", r"arroz a la cubana|rice with (a )?fried egg|arroz con huevo"),
    ("eggs_potatoes", r"huevos rotos|eggs? (and|with) (potato\w*|chips|fries)|patatas con huevo"),
    ("omelette", r"omelet\w*|tortilla francesa|revuelto|scrambled"),
    ("pancakes", r"pancake\w*|tortitas?|crepes?"),
    ("porridge", r"porridge|oatmeal|overnight oats|gachas|\bavena\b|\boats\b"),
    ("tomato_toast", r"\btoasts?\b|^tostadas?\b|\btostadas? (con|de)\b|pan con tomate|bruschetta"),
    ("sandwich", r"sandwich\w*|bocadillo|\bmixto\b|panini"),
    ("quesadilla", r"quesadilla"),
    ("wrap", r"\bwraps?\b|burrito|fajitas?|tacos?\b(?! de (jamon|queso|chorizo|bacon|beicon))|tortillas? de trigo|enrollado"),
    ("pizza", r"pizza|flatbread"),
    ("curry", r"curry|korma|masala"),
    ("paella", r"paella|arroz (con|de) (pollo|verduras)|arroz amarillo"),
    ("fried_rice", r"fried rice|arroz frito|tres delicias"),
    ("chili", r"\bchil+i\b|chile con carne"),
    ("meatballs", r"meatballs?|albondigas?"),
    ("stir_fry", r"stir[- ]?fr\w*|salteado|\bwok\b|teriyaki"),
    ("salad", r"salad|ensalada"),
    ("cream_soup", r"cream of|crema de|\bpure\b|velvety|veloute"),
    ("soup", r"\bsoup\b|\bsopa\b|broth|\bcaldo\b|gazpacho|minestrone"),
    ("pasta_bake", r"lasa(gn|n)\w*|mac(aroni)? (and|&) cheese|(pasta|macaroni|macarrones)\b.*\b(bake[ds]?|gratin\w*|al horno)"
                   r"|(baked|gratin\w*)\b.*\b(pasta|macaroni|macarrones|penne)"),
    ("pasta_creamy", r"carbonara|alfredo|cream(y)?\b.*\b(pasta|spaghetti|penne|macaroni)"
                     r"|(pasta|spaghetti|penne|macaroni|espaguetis|macarrones)\b.*\b(cream\w*|nata|crema)"),
    ("pasta_tomato", r"pasta|spaghetti|espaguetis?|macaroni|macarrones|penne|noodles?|fideos?|bolognese|bolonesa"),
    ("lentils", r"lentils?|lentejas?|\bdh?al\b"),
    ("chickpeas", r"chickpeas?|garbanzos?|chana"),
    ("beans", r"(white|red|kidney|black|butter) beans?|alubias?|fabada|judiones"),
    ("tofu", r"tofu"),
    ("salmon", r"salmon"),
    ("sausages", r"sausages?|salchichas?"),
    ("chicken_roast", r"drumsticks?|jamoncitos?|muslos?|(roast\w*|oven|baked|al horno|asad[oa]).*(chicken|pollo)|(chicken|pollo).*(roast\w*|al horno|asad[oa])"),
    ("vegetable_stew", r"pisto|ratatouille|samfaina|menestra|\bstew\b|guiso|estofado"),
    ("roasted_veg", r"roast(ed)? vegetables|verduras asadas|traybake"),
    ("potatoes", r"potato\w*|patatas?|papas"),
    ("rice_bowl", r"\bbowl\b|\brice\b|\barroz\b|risotto"),
    ("chicken_plate", r"chicken|pollo"),
    ("yogurt", r"yogh?urt|yogur"),
    ("omelette", r"\beggs?\b|huevos?"),
]

# (photo, ingredient ids) when the name says nothing useful: the first rule
# with an ingredient in the recipe wins.
INGREDIENT_RULES = [
    ("pasta_tomato", {"spaghetti", "macaroni"}),
    ("lentils", {"lentils_cooked", "lentils_dry"}),
    ("chickpeas", {"chickpeas_cooked"}),
    ("beans", {"white_beans_cooked", "red_beans_cooked"}),
    ("rice_bowl", {"rice_round", "rice_long"}),
    ("salmon", {"salmon_frozen"}),
    ("tofu", {"tofu"}),
    ("chicken_plate", {"chicken_breast", "chicken_thighs", "minced_chicken"}),
    ("chicken_roast", {"chicken_drumsticks"}),
    ("sausages", {"sausages"}),
    ("meatballs", {"minced_pork", "minced_beef_pork"}),
    ("wrap", {"wheat_tortillas"}),
    ("sandwich", {"sliced_bread", "baguette"}),
    ("porridge", {"oats"}),
    ("yogurt", {"yogurt"}),
    ("omelette", {"eggs_6", "eggs_12"}),
    ("potatoes", {"potato"}),
    ("salad", {"lettuce", "salad_mix", "cucumber"}),
    ("stir_fry", {"veg_stirfry_frozen", "broccoli"}),
    ("vegetable_stew", {"zucchini", "eggplant", "pepper_red", "pepper_green", "menestra_frozen"}),
]

DEFAULT_PHOTO = "generic"
PHOTOS = sorted({photo for photo, _ in NAME_RULES} | {photo for photo, _ in INGREDIENT_RULES} | {DEFAULT_PHOTO})
# Kinds of dish that come up often have a second photo, so a week of rice does
# not show the same bowl every day. Files: <photo>.webp, <photo>_2.webp.
VARIANTS = {"pasta_tomato": 2, "rice_bowl": 2, "fried_rice": 2, "chickpeas": 2, "lentils": 2, "salad": 2, "soup": 2,
            "omelette": 2, "chicken_plate": 2, "stir_fry": 2}


def photo_files() -> list:
    """Every image file name (without .webp) the code can return."""
    return sorted(f"{photo}_{n}" if n > 1 else photo for photo in PHOTOS for n in range(1, VARIANTS.get(photo, 1) + 1))


def _plain(text: str) -> str:
    """Lower case without accents, so "Albóndigas" matches "albondigas"."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in text if not unicodedata.combining(char))


def candidate_photos(recipe_name: str, ingredient_ids) -> tuple:
    """(photos that fit the name, photos that fit the ingredients), best first, no repeats."""
    name = _plain(recipe_name)
    ids = set(ingredient_ids)
    by_name = list(dict.fromkeys(photo for photo, pattern in NAME_RULES if re.search(pattern, name)))
    by_ingredients = list(dict.fromkeys(photo for photo, group in INGREDIENT_RULES if ids & group))
    return by_name, by_ingredients


def best_photo(recipe_name: str, ingredient_ids) -> str:
    """The name is trusted before the ingredients; the default photo is the last resort."""
    by_name, by_ingredients = candidate_photos(recipe_name, ingredient_ids)
    return (by_name or by_ingredients or [DEFAULT_PHOTO])[0]


def choose_photos(meals) -> list:
    """One photo file per meal, in the same order.

    Always the best-fitting kind of dish, never a worse one just to be
    different. When the same kind comes back, its other photo is shown in turn.
    """
    seen, chosen = {}, []
    for meal in meals:
        photo = best_photo(meal.recipe_name, [need.ingredient_id for need in meal.ingredients])
        n = seen.get(photo, 0) % VARIANTS.get(photo, 1) + 1
        seen[photo] = seen.get(photo, 0) + 1
        chosen.append(f"{photo}_{n}" if n > 1 else photo)
    return chosen
