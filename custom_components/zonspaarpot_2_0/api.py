"""API client for Zonspaarpot 2.0."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import DEFAULT_TIMEOUT


class ZonspaarpotApiError(Exception):
    """Base exception for API errors."""


class ZonspaarpotApiConnectionError(ZonspaarpotApiError):
    """Exception for connection errors."""


class ZonspaarpotApiClient:
    """Small API wrapper for Zonspaarpot endpoints."""

    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self._base_url = f"http://{host}"

    async def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with self._session.request(method, url, json=payload) as response:
                    if response.status >= 400:
                        body = await response.text()
                        raise ZonspaarpotApiError(f"{method} {path} failed ({response.status}): {body}")
                    return await response.json()
        except TimeoutError as err:
            raise ZonspaarpotApiConnectionError(f"Timeout while calling {method} {path}") from err
        except ClientError as err:
            raise ZonspaarpotApiConnectionError(f"Connection error while calling {method} {path}: {err}") from err

    async def async_get_info(self) -> dict[str, Any]:
        """Fetch static product info."""
        return await self._request_json("GET", "/api")

    async def async_get_config(self) -> dict[str, Any]:
        """Fetch current config."""
        return await self._request_json("GET", "/api/v2/config")

    async def async_get_actual(self) -> dict[str, Any]:
        """Fetch actual live values."""
        return await self._request_json("GET", "/api/v2/actual")

    async def async_set_mode(self, mode: str) -> dict[str, Any]:
        """Set optimizer mode."""
        return await self._request_json("PUT", "/api/v2/setmode", {"mode": mode})

    async def async_set_load(self, watt: int) -> dict[str, Any]:
        """Set additional consumption."""
        return await self._request_json("PUT", "/api/v2/setload", {"watt": watt})

    async def async_save_load_config(
        self,
        watt: int,
        wait_after_update: int,
        awake: int,
        sleep: int,
    ) -> None:
        """Persist load configuration from the web form endpoint."""
        url = f"{self._base_url}/saveconfigload"
        payload = {
            "watt": str(watt),
            "ws": str(wait_after_update),
            "awake": str(awake),
            "sleep": str(sleep),
        }
        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                async with self._session.post(url, data=payload) as response:
                    if response.status >= 400:
                        body = await response.text()
                        raise ZonspaarpotApiError(
                            f"POST /saveconfigload failed ({response.status}): {body}"
                        )
                    await response.read()
        except TimeoutError as err:
            raise ZonspaarpotApiConnectionError("Timeout while calling POST /saveconfigload") from err
        except ClientError as err:
            try:
                config = await self.async_get_config()
                load = config.get("load", {})
                if (
                    int(load.get("maxwatt", -1)) == watt
                    and int(load.get("waitafterupdate", -1)) == wait_after_update
                    and int(load.get("awake", -1)) == awake
                    and int(load.get("sleep", -1)) == sleep
                ):
                    return
            except ZonspaarpotApiError:
                pass
            raise ZonspaarpotApiConnectionError(
                f"Connection error while calling POST /saveconfigload: {err}"
            ) from err
