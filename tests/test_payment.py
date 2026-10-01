"""Tests for the Stripe pass. Stripe is replaced by a fake, so no key is needed."""

import time
from types import SimpleNamespace

import pytest
import stripe
from fastapi.testclient import TestClient

import app as app_module
from src import payment

client = TestClient(app_module.app)
BODY = {"budget_eur": 10, "people": 1, "days": 1, "meals": ["dinner"]}


@pytest.fixture
def stripe_on(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_not_real")
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    monkeypatch.setattr(payment, "_paid_until", {})
    sessions = {}

    def retrieve(session_id, api_key):
        if session_id not in sessions:
            raise stripe.InvalidRequestError("No such checkout session", "id")
        return sessions[session_id]

    monkeypatch.setattr(stripe.checkout.Session, "retrieve", retrieve)
    return sessions


def paid(days_ago=0):
    return SimpleNamespace(payment_status="paid", created=time.time() - days_ago * 86400)


def test_payment_is_off_without_keys():
    assert not payment.enabled()
    assert client.get("/api/options").json()["payment_required"] is False
    assert client.post("/api/checkout").status_code == 404


def test_checkout_returns_the_stripe_page(stripe_on, monkeypatch):
    seen = {}

    def create(**params):
        seen.update(params)
        return SimpleNamespace(url="https://checkout.stripe.com/c/pay/cs_test_1")

    monkeypatch.setattr(stripe.checkout.Session, "create", create)
    monkeypatch.setenv("PUBLIC_URL", "https://example.app/")
    data = client.post("/api/checkout").json()
    assert data["url"].startswith("https://checkout.stripe.com/")
    assert seen["line_items"] == [{"price": "price_test", "quantity": 1}]
    assert seen["success_url"] == "https://example.app/?session_id={CHECKOUT_SESSION_ID}"


def test_plan_needs_a_paid_session(stripe_on, monkeypatch):
    monkeypatch.setattr(app_module, "generate_plan", lambda request, call: {"status": "ok"})
    assert client.post("/api/plan", json=BODY).status_code == 402
    assert client.post("/api/plan", json=BODY, headers={"X-Payment-Session": "cs_unknown"}).status_code == 402
    stripe_on["cs_test_paid"] = paid()
    response = client.post("/api/plan", json=BODY, headers={"X-Payment-Session": "cs_test_paid"})
    assert response.status_code == 200


def test_unpaid_and_expired_sessions_are_refused(stripe_on):
    stripe_on["cs_open"] = SimpleNamespace(payment_status="unpaid", created=time.time())
    stripe_on["cs_old"] = paid(days_ago=31)
    assert not payment.is_paid("cs_open")
    assert not payment.is_paid("cs_old")
    assert not payment.is_paid("not_a_session")


def test_access_code_still_works_when_payment_is_on(stripe_on, monkeypatch):
    monkeypatch.setenv("ACCESS_CODE", "secret")
    monkeypatch.setattr(app_module, "generate_plan", lambda request, call: {"status": "ok"})
    response = client.post("/api/plan", json=BODY, headers={"X-Access-Code": "secret"})
    assert response.status_code == 200
