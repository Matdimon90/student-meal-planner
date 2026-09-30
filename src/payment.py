"""The only file that talks to Stripe.

A payment buys a pass: for PASS_DAYS days, the person can generate plans.
We keep no database. The browser keeps the id of its Stripe Checkout session
and sends it with every plan request; we ask Stripe whether that session was
paid, and when.

Payment is off unless STRIPE_SECRET_KEY and STRIPE_PRICE_ID are both set.
"""

import os
import time

import stripe
from dotenv import load_dotenv

load_dotenv()  # locally, the Stripe keys live in .env like the Anthropic one

DEFAULT_PASS_DAYS = 30

# Sessions already confirmed as paid: id -> end of the pass (unix time).
# Saves one call to Stripe per plan. It is lost when the server restarts, which is fine.
_paid_until = {}


def enabled() -> bool:
    return bool(os.environ.get("STRIPE_SECRET_KEY") and os.environ.get("STRIPE_PRICE_ID"))


def pass_days() -> int:
    try:
        return max(1, int(os.environ.get("STRIPE_PASS_DAYS") or DEFAULT_PASS_DAYS))
    except ValueError:
        return DEFAULT_PASS_DAYS


def create_checkout(base_url: str) -> str:
    """Open a Stripe Checkout session and return the URL of Stripe's payment page."""
    base_url = base_url.rstrip("/")
    session = stripe.checkout.Session.create(
        api_key=os.environ["STRIPE_SECRET_KEY"],
        mode="payment",
        line_items=[{"price": os.environ["STRIPE_PRICE_ID"], "quantity": 1}],
        # Stripe replaces {CHECKOUT_SESSION_ID} with the real id when it sends the person back.
        success_url=f"{base_url}/?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}/?checkout=cancelled",
    )
    return session.url


def is_paid(session_id: str) -> bool:
    """True if this Checkout session was paid and its pass has not expired."""
    if not session_id or not session_id.startswith("cs_"):
        return False
    now = time.time()
    if _paid_until.get(session_id, 0) > now:
        return True
    try:
        session = stripe.checkout.Session.retrieve(session_id, api_key=os.environ["STRIPE_SECRET_KEY"])
    except stripe.StripeError:
        return False  # unknown id, or Stripe unreachable: no pass
    if session.payment_status != "paid":
        return False
    until = session.created + pass_days() * 86400
    if until <= now:
        return False
    _paid_until[session_id] = until
    return True
