"""The only file that talks to the language model API.

The API key is read from the environment (ANTHROPIC_API_KEY), loaded from a
local .env file if there is one. It is never written in the code.
"""

import os

# Haiku answers in a fraction of the time of Sonnet, and the code validates every
# answer anyway. Set PLANNER_MODEL=claude-sonnet-5 in .env to compare quality.
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 16000  # a 7-day, 3-meal plan for 4 people is a long JSON answer
# Note: there is no temperature setting here. Version 1.x of the Anthropic SDK
# no longer accepts one (see docs/failures.md). Repeatability comes from strict
# prompts and from validating every answer, not from a sampling dial.


def call_claude(system: str, messages: list) -> str:
    """Send a conversation to Claude and return the text of its reply.

    `messages` is a list of {"role": "user" | "assistant", "content": str}.
    The Anthropic client retries rate-limit and server errors by itself.
    """
    from anthropic import Anthropic
    from dotenv import load_dotenv

    load_dotenv()
    client = Anthropic(max_retries=3)
    # Some API keys are not tied to a workspace; Anthropic then requires the
    # workspace id on every request. It is optional and comes from .env.
    extra = {}
    if os.environ.get("ANTHROPIC_WORKSPACE_ID"):
        extra["workspace_id"] = os.environ["ANTHROPIC_WORKSPACE_ID"]
    response = client.messages.create(
        model=os.environ.get("PLANNER_MODEL") or DEFAULT_MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=messages,
        **extra,
    )
    return "".join(block.text for block in response.content if block.type == "text")
