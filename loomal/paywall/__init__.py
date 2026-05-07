"""
Loomal Pay paywall middleware for Python web frameworks.

Currently ships a FastAPI dependency. Importing the helper from
``loomal.paywall`` returns the FastAPI version by default since it is the
most common Python framework. For other frameworks, build on the
lower-level ``build_challenge`` and ``verify_and_settle`` helpers in
``loomal.paywall._core``.

Usage with FastAPI::

    from fastapi import FastAPI, Depends
    from loomal.paywall import require_payment

    app = FastAPI()

    @app.get(
        "/api/search",
        dependencies=[Depends(require_payment(amount="0.01"))],
    )
    def search():
        return {"results": [...]}
"""

from loomal.paywall._core import (
    build_challenge,
    build_challenge_async,
    verify_and_settle,
    verify_and_settle_async,
    PaywallConfig,
    PaywallRouteOptions,
    PaymentRequiredError,
)
from loomal.paywall.fastapi import require_payment

__all__ = [
    "require_payment",
    "build_challenge",
    "build_challenge_async",
    "verify_and_settle",
    "verify_and_settle_async",
    "PaywallConfig",
    "PaywallRouteOptions",
    "PaymentRequiredError",
]
