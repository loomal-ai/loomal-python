"""
FastAPI dependency for the Loomal Pay paywall.

Usage::

    from fastapi import FastAPI, Depends
    from loomal.paywall import require_payment

    app = FastAPI()

    @app.get(
        "/api/search",
        dependencies=[Depends(require_payment(amount="0.01"))],
    )
    def search():
        return {"results": [...]}

The dependency reads the seller's Loomal API key from ``LOOMAL_API_KEY``
or ``SELLER_LOOMAL_API_KEY`` by default. Pass ``api_key`` to override.

When no ``X-Payment`` header is present the dependency raises an
``HTTPException(402)`` with the challenge body. When a signed header
is present, it verifies and settles the payment and writes the
``X-Payment-Response`` header for you. On settle failure the
dependency raises 402 again with the fresh requirement so the buyer
can re-sign.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from loomal.paywall._core import (
    build_challenge_async,
    verify_and_settle_async,
    PaywallConfig,
    PaywallRouteOptions,
)


def require_payment(
    amount: str,
    *,
    description: Optional[str] = None,
    resource: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    network: str = "base",
) -> Callable[..., Any]:
    """Build a FastAPI dependency that gates a route behind a USDC payment.

    Parameters
    ----------
    amount: str
        Decimal USDC amount, e.g. ``"0.01"`` for one cent.
    description: str, optional
        Human-readable label shown to buyers in the 402 body.
    resource: str, optional
        Override the resource URL recorded in the receipt.
    api_key: str, optional
        Loomal seller API key. Falls back to LOOMAL_API_KEY env var.
    base_url: str, optional
        Loomal API base URL. Defaults to https://api.loomal.ai.
    network: str
        Settlement network. Currently only ``"base"`` is supported.
    """
    # Lazy-import FastAPI so non-FastAPI users can still import
    # `loomal.paywall` without the framework installed.
    try:
        from fastapi import HTTPException, Request, Response  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "loomal.paywall.require_payment needs FastAPI. "
            "Install it with: pip install fastapi"
        ) from exc

    config = PaywallConfig(api_key=api_key, base_url=base_url, network=network)
    options = PaywallRouteOptions(
        amount=amount, description=description, resource=resource
    )

    async def dependency(request: Request, response: Response) -> None:
        resolved_resource = (
            options.resource or str(request.url)
        )
        x_payment = request.headers.get("x-payment")

        if not x_payment:
            challenge = await build_challenge_async(
                config, resolved_resource, options
            )
            raise HTTPException(status_code=402, detail=challenge)

        result = await verify_and_settle_async(
            config, resolved_resource, x_payment, options
        )
        if not result.get("ok"):
            raise HTTPException(
                status_code=402, detail=result.get("requirement")
            )

        response.headers["X-Payment-Response"] = result["paymentResponse"]

    return dependency
