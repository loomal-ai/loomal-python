from __future__ import annotations

import os
from typing import Optional

from loomal._http import SyncHttpClient, AsyncHttpClient, DEFAULT_BASE_URL
from loomal.resources.supervisor_identities import SupervisorIdentitiesResource, AsyncSupervisorIdentitiesResource


class LoomalSupervisor:
    """Synchronous Loomal Supervisor client for identity management."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: float = 30.0) -> None:
        resolved_key = api_key or os.environ.get("LOOMAL_SUPERVISOR_KEY")
        if not resolved_key:
            raise ValueError("Supervisor key is required. Pass api_key= or set LOOMAL_SUPERVISOR_KEY env var.")

        http = SyncHttpClient(
            base_url=base_url or os.environ.get("LOOMAL_API_URL", DEFAULT_BASE_URL),
            api_key=resolved_key, timeout=timeout,
        )
        self.identities = SupervisorIdentitiesResource(http)
        self._http = http

    def close(self) -> None:
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class AsyncLoomalSupervisor:
    """Asynchronous Loomal Supervisor client for identity management."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: float = 30.0) -> None:
        resolved_key = api_key or os.environ.get("LOOMAL_SUPERVISOR_KEY")
        if not resolved_key:
            raise ValueError("Supervisor key is required. Pass api_key= or set LOOMAL_SUPERVISOR_KEY env var.")

        http = AsyncHttpClient(
            base_url=base_url or os.environ.get("LOOMAL_API_URL", DEFAULT_BASE_URL),
            api_key=resolved_key, timeout=timeout,
        )
        self.identities = AsyncSupervisorIdentitiesResource(http)
        self._http = http

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
