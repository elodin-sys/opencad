"""USD prices for the Codex worker's pinned model.

Fast-tier short-context list prices, which are twice the standard card. A request over
272k input tokens is priced higher by the provider; exec usage is a sum across requests,
so this card applies the short-context rates. Reasoning tokens are already inside
output tokens and are not added again. Cache-write tokens are not priced separately.

Source: https://developers.openai.com/api/docs/pricing (2026-10-14).
"""

from __future__ import annotations

from typing import Any

CARD_ID = "gpt-6-astra-fast-short-2026-10-14"
SOURCE = "https://developers.openai.com/api/docs/pricing"
AS_OF = "2026-10-14"
MODEL = "gpt-6-astra"

# USD per 1M tokens. Fast tier, short context.
PER_MILLION = {"input": 20.0, "cached": 2.0, "output": 100.0}


def rates() -> dict[str, float]:
    return {key: value / 1_000_000 for key, value in PER_MILLION.items()}


def cost_usd(usage: dict[str, Any] | None, *, model: str | None = MODEL) -> dict[str, Any]:
    """Price one turn. `usage` keys are input, cached, output (reasoning is ignored)."""
    if model != MODEL:
        return {"usd": None, "card": None, "reason": f"no price card for model {model or 'unset'}"}
    usage = usage or {}
    incoming = int(usage.get("input") or 0)
    cached = min(int(usage.get("cached") or 0), incoming)
    outgoing = int(usage.get("output") or 0)
    price = rates()
    usd = (incoming - cached) * price["input"] + cached * price["cached"] + outgoing * price["output"]
    return {"usd": round(usd, 6), "card": CARD_ID, "reason": None}
