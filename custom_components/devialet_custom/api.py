"""Minimal client for the Devialet Custom (CI) HTTP API.

The speaker runs a small configuration web app. Every setting lives under
/cisettings/<key>: GET returns {"data": {"<key>": value}} and POST with
{"<key>": value} sets it. /cisettings/getall returns all settings at once.
Errors are reported with HTTP 200 and an {"error": {...}} body.
"""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=10)


class DevialetError(Exception):
    """Base error for the Devialet Custom API."""


class DevialetConnectionError(DevialetError):
    """The speaker could not be reached."""


class DevialetApiError(DevialetError):
    """The speaker rejected a request."""


class DevialetCustomApi:
    """Talk to a Devialet Custom speaker."""

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self.host = host

    async def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"http://{self.host}{path}"
        try:
            async with self._session.request(
                method, url, json=payload, timeout=TIMEOUT
            ) as resp:
                resp.raise_for_status()
                body = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise DevialetConnectionError(f"Error talking to {url}: {err}") from err

        if not isinstance(body, dict):
            raise DevialetApiError(f"Unexpected response from {url}: {body!r}")
        if "error" in body:
            error = body["error"]
            raise DevialetApiError(
                f"{error.get('code', 'Error')}: {error.get('message', error)}"
            )
        return body.get("data", {})

    async def get_device_info(self) -> dict[str, Any]:
        """Return model, serial and firmware information."""
        return await self._request("GET", "/device/info")

    async def get_settings(self) -> dict[str, Any]:
        """Return every CI setting and status value."""
        return await self._request("GET", "/cisettings/getall")

    async def set_setting(self, key: str, value: Any) -> None:
        """Set a single CI setting."""
        await self._request("POST", f"/cisettings/{key}", {key: value})
