"""Async API client for ZeusNet backend."""

import aiohttp
from typing import Any, Dict, List


class APIError(Exception):
    """Raised when an API request returns an error status."""


class NetworkAPIClient:
    """Client for network-related API endpoints."""

    BASE_URL = "http://localhost:8000/api"

    async def get_networks(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/networks", params=filters) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise APIError(f"HTTP {resp.status}")


class SettingsAPIClient:
    """Client for application settings endpoints."""

    BASE_URL = "http://localhost:8000/api"

    async def _get(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/settings") as resp:
                if resp.status == 200:
                    return await resp.json()
                raise APIError(f"HTTP {resp.status}")

    async def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.BASE_URL}/settings", json=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
                raise APIError(f"HTTP {resp.status}")

    def fetch_settings_async(self, on_success, on_error) -> None:
        async def task():
            try:
                data = await self._get()
                if on_success:
                    on_success(data)
            except Exception as exc:  # pragma: no cover - network errors
                if on_error:
                    on_error(exc)

        import asyncio

        asyncio.create_task(task())

    def set_mode_async(self, mode: str, on_success, on_error) -> None:
        async def task():
            try:
                data = await self._post({"mode": mode})
                if on_success:
                    on_success(data)
            except Exception as exc:  # pragma: no cover - network errors
                if on_error:
                    on_error(exc)

        import asyncio

        asyncio.create_task(task())

    def set_serial_port_async(self, port: str, on_success, on_error) -> None:
        async def task():
            try:
                data = await self._post({"serial_port": port})
                if on_success:
                    on_success(data)
            except Exception as exc:  # pragma: no cover - network errors
                if on_error:
                    on_error(exc)

        import asyncio

        asyncio.create_task(task())

    def set_watchdog_async(self, enabled: bool, on_success, on_error) -> None:
        async def task():
            try:
                data = await self._post({"watchdog": enabled})
                if on_success:
                    on_success(data)
            except Exception as exc:  # pragma: no cover - network errors
                if on_error:
                    on_error(exc)

        import asyncio

        asyncio.create_task(task())
