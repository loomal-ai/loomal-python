"""
Framework-agnostic core for the loomal paywall middleware.

Sellers wrap a route with a framework-specific dependency (FastAPI today;
Flask and Starlette in follow-ups). The framework adapter calls these two
functions:

* ``build_challenge`` — when no X-Payment header is present, ask Loomal to
  construct the 402 body (an x402 PaymentRequirements set).
* ``verify_and_settle`` — when a buyer retries with a signed X-Payment
  header, ask Loomal to verify, settle on chain, and sign a receipt.

Both async and sync variants are exposed since FastAPI handlers are
typically async but Flask handlers typically are not.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

DEFAULT_BASE_URL = "https://api.loomal.ai"
DEFAULT_NETWORK = "base"


@dataclass
class PaywallConfig:
    """Connection config for the paywall middleware.

    All fields are optional. The seller API key falls back to the
    LOOMAL_API_KEY or SELLER_LOOMAL_API_KEY environment variable.
    """

    api_key: Optional[str] = None
    base_url: Optional[str] = None
    network: str = DEFAULT_NETWORK


@dataclass
class PaywallRouteOptions:
    """Per-route paywall options.

    ``amount`` is the only required field. ``description`` and
    ``resource`` are optional overrides.
    """

    amount: str
    description: Optional[str] = None
    resource: Optional[str] = None
    extra_headers: dict[str, str] = field(default_factory=dict)


class PaymentRequiredError(Exception):
    """Raised when a request needs to pay (or repay) before continuing.

    The framework adapter catches this and returns HTTP 402 with the
    ``challenge`` body so the buyer can sign and retry.
    """

    def __init__(self, challenge: Any) -> None:
        super().__init__("Payment required")
        self.challenge = challenge


def _resolve_api_key(explicit: Optional[str]) -> str:
    key = (
        explicit
        or os.environ.get("LOOMAL_API_KEY")
        or os.environ.get("SELLER_LOOMAL_API_KEY")
        or ""
    )
    if not key.startswith("loid-"):
        raise RuntimeError(
            "Loomal paywall: missing API key. Pass api_key= or set "
            "LOOMAL_API_KEY in your environment."
        )
    return key


def _resolve_base_url(explicit: Optional[str]) -> str:
    return (
        explicit
        or os.environ.get("LOOMAL_BASE_URL")
        or DEFAULT_BASE_URL
    ).rstrip("/")


def build_challenge(
    config: PaywallConfig,
    resource: str,
    options: PaywallRouteOptions,
) -> Any:
    """Sync: ask Loomal to build a 402 challenge body."""
    api_key = _resolve_api_key(config.api_key)
    base_url = _resolve_base_url(config.base_url)
    body = {
        "amount": options.amount,
        "network": config.network,
        "resource": options.resource or resource,
        "description": options.description or resource,
    }
    res = httpx.post(
        f"{base_url}/v0/payments/challenge",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30.0,
    )
    res.raise_for_status()
    return res.json()


async def build_challenge_async(
    config: PaywallConfig,
    resource: str,
    options: PaywallRouteOptions,
) -> Any:
    """Async: ask Loomal to build a 402 challenge body."""
    api_key = _resolve_api_key(config.api_key)
    base_url = _resolve_base_url(config.base_url)
    body = {
        "amount": options.amount,
        "network": config.network,
        "resource": options.resource or resource,
        "description": options.description or resource,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            f"{base_url}/v0/payments/challenge",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )
    res.raise_for_status()
    return res.json()


def verify_and_settle(
    config: PaywallConfig,
    resource: str,
    payment_header: str,
    options: PaywallRouteOptions,
) -> Any:
    """Sync: verify a signed payment header and settle on chain."""
    api_key = _resolve_api_key(config.api_key)
    base_url = _resolve_base_url(config.base_url)
    body = {
        "paymentHeader": payment_header,
        "resource": options.resource or resource,
        "amount": options.amount,
        "network": config.network,
    }
    res = httpx.post(
        f"{base_url}/v0/payments/redeem",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30.0,
    )
    res.raise_for_status()
    return res.json()


async def verify_and_settle_async(
    config: PaywallConfig,
    resource: str,
    payment_header: str,
    options: PaywallRouteOptions,
) -> Any:
    """Async: verify a signed payment header and settle on chain."""
    api_key = _resolve_api_key(config.api_key)
    base_url = _resolve_base_url(config.base_url)
    body = {
        "paymentHeader": payment_header,
        "resource": options.resource or resource,
        "amount": options.amount,
        "network": config.network,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            f"{base_url}/v0/payments/redeem",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )
    res.raise_for_status()
    return res.json()
