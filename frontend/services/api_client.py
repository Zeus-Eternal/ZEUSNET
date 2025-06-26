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
