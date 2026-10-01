import pytest


@pytest.fixture(autouse=True)
def no_stripe_from_env(monkeypatch):
    # A developer's .env may hold Stripe keys: tests start with payment off.
    for name in ("STRIPE_SECRET_KEY", "STRIPE_PRICE_ID", "STRIPE_PASS_DAYS", "PUBLIC_URL"):
        monkeypatch.delenv(name, raising=False)
