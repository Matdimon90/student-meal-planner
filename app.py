"""Web entry point. Run locally with:  uvicorn app:app --reload

Vercel finds the `app` object in this file and serves everything in public/
as static files. Locally, FastAPI serves public/ itself (last line).
"""

import os
from typing import List

from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.catalogue import DIET_ALLOWS, KNOWN_ALLERGENS, load_catalogue, snapshot_info
from src.llm import call_claude
from src.plan import MAX_BUDGET_EUR, MAX_DAYS, MAX_NOTES_CHARS, MAX_PEOPLE, MEAL_TYPES, PlanRequest, RequestError
from src.planner import DEFAULT_PROMPT_VERSION, generate_plan

app = FastAPI(title="Student Meal Planner")


class PlanBody(BaseModel):
    budget_eur: float
    people: int
    days: int
    meals: List[str] = ["lunch", "dinner"]
    diet: str = "omnivore"
    allergies: List[str] = []
    disliked: List[str] = []
    already_have: List[str] = []
    language: str = "en"
    notes: str = ""


@app.get("/api/options")
def options():
    """Everything the web page needs to build its form."""
    return {
        "prices": snapshot_info(),
        "diets": sorted(DIET_ALLOWS),
        "allergens": sorted(KNOWN_ALLERGENS),
        "meals": list(MEAL_TYPES),
        "limits": {"people": MAX_PEOPLE, "days": MAX_DAYS, "budget_eur": MAX_BUDGET_EUR, "notes": MAX_NOTES_CHARS},
        "prompt_version": DEFAULT_PROMPT_VERSION,
        "access_code_required": bool(os.environ.get("ACCESS_CODE")),
        "ingredients": [
            {
                "id": p.ingredient_id, "en": p.name_en, "es": p.name_es, "category": p.category,
                "package": f"{p.package_size:g} {p.package_unit}", "price_cents": p.package_price_cents,
            }
            for p in load_catalogue().values()
        ],
    }


@app.post("/api/plan")
def plan(body: PlanBody, x_access_code: str = Header(default="")):
    # Each plan costs us real money in model calls. If ACCESS_CODE is set on the
    # server, only people who know it (us, the teacher) can generate plans.
    expected = os.environ.get("ACCESS_CODE")
    if expected and x_access_code != expected:
        raise HTTPException(status_code=401, detail="Wrong or missing access code")

    request = PlanRequest(
        budget_eur=body.budget_eur,
        people=body.people,
        days=body.days,
        meals=tuple(body.meals),
        diet=body.diet,
        allergies=frozenset(body.allergies),
        disliked=frozenset(body.disliked),
        already_have=frozenset(body.already_have),
        language=body.language,
        notes=body.notes,
    )
    if not os.environ.get("ANTHROPIC_API_KEY"):
        from dotenv import load_dotenv

        load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not set. Put it in the .env file (or in Vercel's environment variables) and restart the server.")
    try:
        return generate_plan(request, call_claude)
    except RequestError as error:
        raise HTTPException(status_code=422, detail=str(error))
    except Exception as error:  # missing key, network problem, provider error
        hints = {
            "AuthenticationError": "the API key was refused. Check ANTHROPIC_API_KEY.",
            "PermissionDeniedError": "this API key is not allowed to use the model.",
            "NotFoundError": "the model name is unknown. Check PLANNER_MODEL.",
            "RateLimitError": "too many requests or no credit left. Wait a minute and try again.",
            "APIConnectionError": "no network connection to the model provider.",
        }
        reason = hints.get(type(error).__name__, type(error).__name__)
        if type(error).__name__ == "BadRequestError":
            # The provider explains what it did not like; show it, but never a key.
            reason = "the request was refused: " + str(error).replace(os.environ.get("ANTHROPIC_API_KEY", "x"), "***")[:300]
        raise HTTPException(status_code=502, detail=f"The language model call failed: {reason}")


# Local development only: on Vercel, public/ is served before this app is reached.
if os.path.isdir("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")
