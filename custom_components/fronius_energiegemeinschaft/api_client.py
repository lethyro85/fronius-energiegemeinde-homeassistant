"""API client for Fronius Energiegemeinschaft."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant

from .const import (
    BASE_URL,
    API_LOGIN,
    API_CSRF,
    API_COMMUNITY,
    API_COMMUNITY_ENERGY,
    API_COUNTER_POINT,
    API_COUNTER_POINT_ENERGY,
)

_LOGGER = logging.getLogger(__name__)


class FroniusEnergyClient:
    """Client to interact with Fronius Energiegemeinschaft API."""

    def __init__(self, username: str, password: str, hass: HomeAssistant) -> None:
        """Initialize the client."""
        self.username = username
        self.password = password
        self.hass = hass
        self.session: aiohttp.ClientSession | None = None
        self.cookies: dict[str, str] = {}
        self.csrf_token: str | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def login(self) -> bool:
        """Login to the Fronius Energiegemeinschaft portal."""
        session = await self._get_session()

        # First, get the login page to get initial cookies
        async with session.get(f"{BASE_URL}/backend/login") as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get login page: {resp.status}")

            # Store cookies
            for cookie in resp.cookies.values():
                self.cookies[cookie.key] = cookie.value

        # Get CSRF token
        async with session.get(
            f"{BASE_URL}{API_CSRF}",
            cookies=self.cookies
        ) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get CSRF token: {resp.status}")

            csrf_data = await resp.json()
            self.csrf_token = csrf_data.get("token")

            # Update cookies
            for cookie in resp.cookies.values():
                self.cookies[cookie.key] = cookie.value

        # Perform login
        login_data = {
            "email": self.username,
            "password": self.password,
        }

        headers = {
            "X-XSRF-TOKEN": self.cookies.get("XSRF-TOKEN", ""),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with session.post(
            f"{BASE_URL}/backend/api/auth/login",
            json=login_data,
            headers=headers,
            cookies=self.cookies
        ) as resp:
            if resp.status not in [200, 204]:
                raise Exception(f"Login failed: {resp.status}")

            # Update cookies after login
            for cookie in resp.cookies.values():
                self.cookies[cookie.key] = cookie.value

            _LOGGER.info("Successfully logged in to Fronius Energiegemeinschaft")
            return True

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make an authenticated request to the API."""
        session = await self._get_session()

        # Add CSRF token header
        headers = kwargs.get("headers", {})
        if self.cookies.get("XSRF-TOKEN"):
            headers["X-XSRF-TOKEN"] = self.cookies["XSRF-TOKEN"]
        headers["Accept"] = "application/json"
        kwargs["headers"] = headers
        kwargs["cookies"] = self.cookies

        url = f"{BASE_URL}{endpoint}"

        async with session.request(method, url, **kwargs) as resp:
            if resp.status == 401:
                # Try to re-login
                _LOGGER.warning("Session expired, attempting re-login")
                await self.login()

                # Update headers with new CSRF token
                if self.cookies.get("XSRF-TOKEN"):
                    headers["X-XSRF-TOKEN"] = self.cookies["XSRF-TOKEN"]
                kwargs["headers"] = headers
                kwargs["cookies"] = self.cookies

                # Retry request
                async with session.request(method, url, **kwargs) as retry_resp:
                    if retry_resp.status != 200:
                        raise Exception(f"Request failed after re-login: {retry_resp.status}")
                    return await retry_resp.json()

            if resp.status != 200:
                raise Exception(f"Request failed: {resp.status}")

            # Update cookies
            for cookie in resp.cookies.values():
                self.cookies[cookie.key] = cookie.value

            return await resp.json()

    async def get_communities(self) -> list[dict[str, Any]]:
        """Get list of communities."""
        return await self._make_request("GET", API_COMMUNITY)

    async def get_community_energy_data(
        self, community_id: int, view: str = "month", time: str | None = None
    ) -> dict[str, Any]:
        """Get energy data for a community."""
        if time is None:
            time = datetime.now().strftime("%Y-%m")

        endpoint = API_COMMUNITY_ENERGY.format(community_id=community_id)
        params = {"view": view, "time": time}

        return await self._make_request("GET", endpoint, params=params)

    async def get_counter_points(self) -> list[dict[str, Any]]:
        """Get list of counter points."""
        return await self._make_request("GET", API_COUNTER_POINT)

    async def get_counter_point_energy_data(
        self, counter_point_id: int, view: str = "month", time: str | None = None
    ) -> dict[str, Any]:
        """Get energy data for a counter point."""
        if time is None:
            time = datetime.now().strftime("%Y-%m")

        endpoint = API_COUNTER_POINT_ENERGY.format(counter_point_id=counter_point_id)
        params = {"view": view, "time": time}

        return await self._make_request("GET", endpoint, params=params)

    async def close(self) -> None:
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
