"""Tests for the web API. The model is replaced by a fake, so no key is needed."""

import json

from fastapi.testclient import TestClient

import app as app_module

client = TestClient(app_module.app)

GOOD_REPLY = json.dumps(
    {
        "feasible": True,
        "reason": "cheap",
        "meals": [
            {
                "day": 1,
                "meal": "dinner",
                "recipe_name": "Rice and lentils",
                "servings": 1,
                "ingredients": [{"ingredient_id": "rice_round", "quantity": 100, "unit": "g"}],
                "steps": ["Cook."],
            }
        ],
        "suggestions": [],
    }
)
BODY = {"budget_eur": 10, "people": 1, "days": 1, "meals": ["dinner"]}


def test_options_lists_ingredients_and_price_date():
    data = client.get("/api/options").json()
    assert data["prices"]["captured_at"] == "2026-09-21"
    assert len(data["ingredients"]) >= 80


import pytest


@pytest.fixture(autouse=True)
def fake_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")


def test_missing_api_key_gives_a_clear_message(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)
    response = client.post("/api/plan", json=BODY)
    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["detail"]


def test_plan_endpoint_returns_a_priced_plan(monkeypatch):
    monkeypatch.setattr(app_module, "call_claude", lambda system, messages: GOOD_REPLY)
    data = client.post("/api/plan", json=BODY).json()
    assert data["status"] == "ok"
    assert data["budget"]["total_cents"] == 115


def test_invalid_input_gives_a_clear_422(monkeypatch):
    monkeypatch.setattr(app_module, "call_claude", lambda system, messages: GOOD_REPLY)
    response = client.post("/api/plan", json={**BODY, "people": 99})
    assert response.status_code == 422
    assert "people" in response.json()["detail"].lower()


def test_wrong_types_are_rejected_before_any_model_call():
    assert client.post("/api/plan", json={**BODY, "budget_eur": "lots"}).status_code == 422


def test_access_code_protects_the_endpoint(monkeypatch):
    monkeypatch.setenv("ACCESS_CODE", "secret")
    monkeypatch.setattr(app_module, "call_claude", lambda system, messages: GOOD_REPLY)
    assert client.post("/api/plan", json=BODY).status_code == 401
    assert client.post("/api/plan", json=BODY, headers={"X-Access-Code": "secret"}).status_code == 200


def test_model_failure_gives_502_without_leaking_details(monkeypatch):
    def broken(system, messages):
        raise RuntimeError("sk-ant-secret-key-in-error")

    monkeypatch.setattr(app_module, "call_claude", broken)
    response = client.post("/api/plan", json=BODY)
    assert response.status_code == 502
    assert "sk-ant" not in response.text


SWAP_REPLY = json.dumps(
    {
        "feasible": True,
        "reason": "reuses the rice",
        "meals": [
            {
                "day": 1,
                "meal": "dinner",
                "recipe_name": "Tomato rice",
                "servings": 1,
                "ingredients": [{"ingredient_id": "rice_round", "quantity": 120, "unit": "g"}],
                "steps": ["Cook."],
            }
        ],
        "suggestions": [],
    }
)


def test_swap_endpoint_replaces_one_meal(monkeypatch):
    monkeypatch.setattr(app_module, "call_claude", lambda system, messages: SWAP_REPLY)
    current = [
        {"day": 1, "meal": "dinner", "recipe_name": "Rice and lentils", "servings": 1,
         "ingredients": [{"ingredient_id": "rice_round", "quantity": 100, "unit": "g"}], "steps": ["Cook."]}
    ]
    body = {**BODY, "day": 1, "meal": "dinner", "plan_meals": current}
    data = client.post("/api/swap", json=body).json()
    assert data["status"] == "ok"
    assert data["meals"][0]["recipe_name"] == "Tomato rice"


def test_options_lists_supermarkets_and_switches_prices():
    data = client.get("/api/options").json()
    assert [s["supermarket"] for s in data["supermarkets"]][:2] == ["mercadona", "dia"]
    dia = client.get("/api/options?supermarket=dia").json()
    assert dia["prices"]["supermarket"] == "dia"
    assert len(dia["ingredients"]) == 85
    assert client.get("/api/options?supermarket=lidl").status_code == 404


def test_options_list_the_preferences_the_form_asks_for():
    data = client.get("/api/options").json()
    assert "healthy" in data["styles"] and data["max_styles"] == 3
    assert data["portions"]["balanced"] == [600, 800]
    assert data["protein_targets"]["high"] == 30
    assert "oven" in data["equipment"]


def test_preferences_are_accepted_by_the_plan_endpoint(monkeypatch):
    monkeypatch.setattr(app_module, "call_claude", lambda system, messages: GOOD_REPLY)
    body = {**BODY, "styles": ["quick"], "portion": "light", "protein": "high", "equipment": ["hob"]}
    assert client.post("/api/plan", json=body).json()["status"] == "ok"


def test_unknown_preference_gives_a_422():
    response = client.post("/api/plan", json={**BODY, "equipment": ["barbecue"]})
    assert response.status_code == 422
