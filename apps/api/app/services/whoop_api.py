"""
WHOOP API v2 Client
Wrapper for all WHOOP API v2 endpoints with automatic token refresh
"""
import httpx
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from .whoop_oauth import WHOOPOAuthService


class WHOOPAPIClient:
    """Client for WHOOP API v2 endpoints"""

    API_BASE_URL = "https://api.prod.whoop.com/developer/v2"

    def __init__(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ):
        """
        Initialize WHOOP API client

        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token (for auto-refresh)
            expires_at: Token expiration timestamp
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.oauth_service = WHOOPOAuthService()

    async def _ensure_valid_token(self):
        """Refresh token if expired"""
        if self.refresh_token and self.expires_at:
            new_token, token_data = await self.oauth_service.ensure_valid_token(
                self.access_token,
                self.refresh_token,
                self.expires_at
            )
            if token_data:
                self.access_token = new_token
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                self.expires_at = token_data["expires_at"]

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to WHOOP API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response JSON

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        await self._ensure_valid_token()

        url = f"{self.API_BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )

            if response.status_code >= 400:
                print(f"❌ WHOOP API Error: {response.status_code} - {url}")

            response.raise_for_status()
            return response.json()

    # User Profile
    async def get_user_profile(self) -> Dict[str, Any]:
        """
        Get authenticated user's profile

        Returns:
            User profile data including user_id, email, first_name, last_name
        """
        return await self._make_request("GET", "user/profile/basic")

    # Cycle Endpoints
    async def get_cycles(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        limit: int = 10,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get physiological cycles

        Args:
            start: Start date (ISO format)
            end: End date (ISO format)
            limit: Number of records (max 50)
            next_token: Pagination token

        Returns:
            List of cycles with pagination info
        """
        params = {"limit": limit}

        if start:
            # Convert date to datetime at start of day (midnight UTC)
            start_dt = datetime.combine(start, datetime.min.time())
            params["start"] = start_dt.isoformat() + "Z"
        if end:
            # Convert date to datetime at end of day (midnight UTC next day)
            end_dt = datetime.combine(end, datetime.max.time()).replace(microsecond=0)
            params["end"] = end_dt.isoformat() + "Z"
        if next_token:
            params["nextToken"] = next_token

        return await self._make_request("GET", "cycle", params=params)

    async def get_cycle_by_id(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get single cycle by ID

        Args:
            cycle_id: Cycle ID

        Returns:
            Cycle data
        """
        return await self._make_request("GET", f"cycle/{cycle_id}")

    # Recovery Endpoints
    async def get_recovery(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        limit: int = 10,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get recovery data

        Args:
            start: Start date
            end: End date
            limit: Number of records (max 50)
            next_token: Pagination token

        Returns:
            List of recovery records
        """
        params = {"limit": limit}

        if start:
            # Convert date to datetime at start of day (midnight UTC)
            start_dt = datetime.combine(start, datetime.min.time())
            params["start"] = start_dt.isoformat() + "Z"
        if end:
            # Convert date to datetime at end of day (midnight UTC next day)
            end_dt = datetime.combine(end, datetime.max.time()).replace(microsecond=0)
            params["end"] = end_dt.isoformat() + "Z"
        if next_token:
            params["nextToken"] = next_token

        return await self._make_request("GET", "recovery", params=params)

    async def get_recovery_by_cycle_id(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get recovery for specific cycle

        Args:
            cycle_id: Cycle ID

        Returns:
            Recovery data for that cycle
        """
        return await self._make_request("GET", f"cycle/{cycle_id}/recovery")

    # Sleep Endpoints
    async def get_sleep_by_cycle_id(self, cycle_id: str) -> Dict[str, Any]:
        """
        Get sleep for specific cycle

        Args:
            cycle_id: Cycle ID

        Returns:
            Sleep data for that cycle
        """
        return await self._make_request("GET", f"cycle/{cycle_id}/sleep")
    async def get_sleep(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        limit: int = 10,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get sleep data

        Args:
            start: Start date
            end: End date
            limit: Number of records (max 50)
            next_token: Pagination token

        Returns:
            List of sleep records
        """
        params = {"limit": limit}

        if start:
            # Convert date to datetime at start of day (midnight UTC)
            start_dt = datetime.combine(start, datetime.min.time())
            params["start"] = start_dt.isoformat() + "Z"
        if end:
            # Convert date to datetime at end of day (midnight UTC next day)
            end_dt = datetime.combine(end, datetime.max.time()).replace(microsecond=0)
            params["end"] = end_dt.isoformat() + "Z"
        if next_token:
            params["nextToken"] = next_token

        return await self._make_request("GET", "activity/sleep", params=params)

    async def get_sleep_by_id(self, sleep_id: str) -> Dict[str, Any]:
        """
        Get single sleep record by ID

        Args:
            sleep_id: Sleep ID

        Returns:
            Sleep data
        """
        return await self._make_request("GET", f"activity/sleep/{sleep_id}")

    # Workout Endpoints
    async def get_workouts(
        self,
        start: Optional[date] = None,
        end: Optional[date] = None,
        limit: int = 10,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get workout data

        Args:
            start: Start date
            end: End date
            limit: Number of records (max 50)
            next_token: Pagination token

        Returns:
            List of workout records
        """
        params = {"limit": limit}

        if start:
            # Convert date to datetime at start of day (midnight UTC)
            start_dt = datetime.combine(start, datetime.min.time())
            params["start"] = start_dt.isoformat() + "Z"
        if end:
            # Convert date to datetime at end of day (midnight UTC next day)
            end_dt = datetime.combine(end, datetime.max.time()).replace(microsecond=0)
            params["end"] = end_dt.isoformat() + "Z"
        if next_token:
            params["nextToken"] = next_token

        return await self._make_request("GET", "activity/workout", params=params)

    async def get_workout_by_id(self, workout_id: str) -> Dict[str, Any]:
        """
        Get single workout by ID

        Args:
            workout_id: Workout ID

        Returns:
            Workout data
        """
        return await self._make_request("GET", f"activity/workout/{workout_id}")

    # Body Measurement Endpoints
    async def get_body_measurement(self) -> Dict[str, Any]:
        """
        Get body measurement data (height, weight, max heart rate)

        Note: According to WHOOP API v2 docs, this endpoint does not support
        date filtering or pagination. It returns the current body measurements.

        Returns:
            Body measurement data (height_meter, weight_kilogram, max_heart_rate)
        """
        return await self._make_request("GET", "user/measurement/body")

    # Convenience Methods
    async def sync_all_data(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all data types for date range

        Args:
            start_date: Start date for sync
            end_date: End date (defaults to today)

        Returns:
            Dictionary with cycles, recovery, sleep, workouts data
        """
        if not end_date:
            end_date = date.today()

        # Fetch all data types in parallel (max limit is 25 per WHOOP API)
        cycles_data = await self.get_cycles(start=start_date, end=end_date, limit=25)
        recovery_data = await self.get_recovery(start=start_date, end=end_date, limit=25)
        sleep_data = await self.get_sleep(start=start_date, end=end_date, limit=25)
        workout_data = await self.get_workouts(start=start_date, end=end_date, limit=25)

        return {
            "cycles": cycles_data.get("records", []),
            "recovery": recovery_data.get("records", []),
            "sleep": sleep_data.get("records", []),
            "workouts": workout_data.get("records", []),
        }

    async def get_latest_recovery(self) -> Optional[Dict[str, Any]]:
        """
        Get most recent recovery score

        Returns:
            Latest recovery data or None
        """
        recovery_data = await self.get_recovery(limit=1)
        records = recovery_data.get("records", [])
        return records[0] if records else None

    async def get_latest_sleep(self) -> Optional[Dict[str, Any]]:
        """
        Get most recent sleep record

        Returns:
            Latest sleep data or None
        """
        sleep_data = await self.get_sleep(limit=1)
        records = sleep_data.get("records", [])
        return records[0] if records else None


def create_whoop_client(
    access_token: str,
    refresh_token: Optional[str] = None,
    expires_at: Optional[datetime] = None
) -> WHOOPAPIClient:
    """
    Factory function to create WHOOP API client

    Args:
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        expires_at: Token expiration timestamp

    Returns:
        Configured WHOOPAPIClient instance
    """
    return WHOOPAPIClient(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at
    )