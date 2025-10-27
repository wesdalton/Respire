"""
Oura API Client

Handles all interactions with Oura Ring API v2.
Includes automatic token refresh and pagination support.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Awaitable
import httpx


class OuraAPIClient:
    """Client for Oura Ring API v2"""

    BASE_URL = "https://api.ouraring.com/v2"

    def __init__(
        self,
        access_token: str,
        refresh_token: str = None,
        token_expires_at: datetime = None,
        token_refresh_callback: Callable[[str], Awaitable[Dict]] = None
    ):
        """
        Initialize Oura API client

        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token (for automatic refresh)
            token_expires_at: Token expiration datetime
            token_refresh_callback: Async function to call when token needs refresh
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at
        self.token_refresh_callback = token_refresh_callback

    async def _ensure_valid_token(self):
        """Refresh token if expired or expiring soon"""
        if not self.token_expires_at or not self.refresh_token:
            return

        # Refresh if token expires in less than 5 minutes
        if datetime.utcnow() >= self.token_expires_at - timedelta(minutes=5):
            if self.token_refresh_callback:
                new_tokens = await self.token_refresh_callback(self.refresh_token)
                self.access_token = new_tokens["access_token"]
                self.refresh_token = new_tokens["refresh_token"]
                self.token_expires_at = new_tokens["token_expires_at"]

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None
    ) -> Dict:
        """
        Make authenticated API request

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            Response JSON
        """
        await self._ensure_valid_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        url = f"{self.BASE_URL}/{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def _paginated_request(
        self,
        endpoint: str,
        params: Dict = None
    ) -> List[Dict]:
        """
        Make paginated API request and collect all results

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            List of all items across all pages
        """
        all_items = []
        next_token = None
        params = params or {}

        while True:
            if next_token:
                params["next_token"] = next_token

            response = await self._make_request("GET", endpoint, params)

            # Handle both 'data' and direct array responses
            if "data" in response:
                items = response["data"]
            else:
                items = response if isinstance(response, list) else []

            all_items.extend(items)

            # Check for pagination
            next_token = response.get("next_token")
            if not next_token:
                break

        return all_items

    # Personal Info
    async def get_personal_info(self) -> Dict:
        """Get user's personal information"""
        return await self._make_request("GET", "usercollection/personal_info")

    # Daily Activity
    async def get_daily_activity(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get daily activity summaries

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of daily activity summaries
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/daily_activity", params)
        return response.get("data", [])

    # Daily Readiness
    async def get_daily_readiness(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get daily readiness scores

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of daily readiness scores
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/daily_readiness", params)
        return response.get("data", [])

    # Daily Sleep
    async def get_daily_sleep(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get daily sleep summaries

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of daily sleep summaries
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/daily_sleep", params)
        return response.get("data", [])

    # Heart Rate
    async def get_heart_rate(
        self,
        start_datetime: str = None,
        end_datetime: str = None
    ) -> List[Dict]:
        """
        Get heart rate time series data (Gen 3 only)

        Args:
            start_datetime: Start datetime (ISO 8601)
            end_datetime: End datetime (ISO 8601)

        Returns:
            List of heart rate data points
        """
        params = {}
        if start_datetime:
            params["start_datetime"] = start_datetime
        if end_datetime:
            params["end_datetime"] = end_datetime

        response = await self._make_request("GET", "usercollection/heartrate", params)
        return response.get("data", [])

    # Sleep Time Series
    async def get_sleep_time_series(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get detailed sleep time series data

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of sleep periods with time series data
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/sleep", params)
        return response.get("data", [])

    # Workouts
    async def get_workouts(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get workout summaries

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of workout summaries
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/workout", params)
        return response.get("data", [])

    # Sessions
    async def get_sessions(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get session summaries (guided/unguided sessions in Oura app)

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of session summaries
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/session", params)
        return response.get("data", [])

    # SpO2
    async def get_spo2(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Get SpO2 (blood oxygen) averages

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of daily SpO2 averages
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        response = await self._make_request("GET", "usercollection/daily_spo2", params)
        return response.get("data", [])


def create_oura_client(
    access_token: str,
    refresh_token: str = None,
    token_expires_at: datetime = None,
    token_refresh_callback: Callable[[str], Awaitable[Dict]] = None
) -> OuraAPIClient:
    """
    Factory function to create Oura API client

    Args:
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        token_expires_at: Token expiration datetime
        token_refresh_callback: Callback for token refresh

    Returns:
        Configured OuraAPIClient instance
    """
    return OuraAPIClient(
        access_token=access_token,
        refresh_token=refresh_token,
        token_expires_at=token_expires_at,
        token_refresh_callback=token_refresh_callback
    )
