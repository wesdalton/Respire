"""
WHOOP OAuth 2.0 Service
Handles authentication flow and token management for WHOOP API v2
"""
import os
import secrets
import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode


class WHOOPOAuthService:
    """WHOOP OAuth 2.0 authentication service"""

    # WHOOP API v2 endpoints
    AUTH_BASE_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
    TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
    API_BASE_URL = "https://api.prod.whoop.com/developer/v2"

    # OAuth scopes
    SCOPES = [
        "read:profile",
        "read:cycles",
        "read:recovery",
        "read:sleep",
        "read:workout",
        "read:body_measurement",
        "offline",  # Required to receive refresh tokens
    ]

    def __init__(self):
        self.client_id = os.getenv("WHOOP_CLIENT_ID")
        self.client_secret = os.getenv("WHOOP_CLIENT_SECRET")

        # Allow missing credentials in development for testing other endpoints
        if not self.client_id or not self.client_secret:
            print("⚠️  WARNING: WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET not set")
            print("   WHOOP OAuth endpoints will not work until credentials are configured")
            self.client_id = "PLACEHOLDER"
            self.client_secret = "PLACEHOLDER"

    def generate_authorization_url(self, redirect_uri: str) -> Tuple[str, str]:
        """
        Generate WHOOP OAuth authorization URL

        Args:
            redirect_uri: Registered redirect URI

        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "state": state,
        }

        authorization_url = f"{self.AUTH_BASE_URL}?{urlencode(params)}"

        return authorization_url, state

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization

        Returns:
            Token response with access_token, refresh_token, expires_in, etc.

        Raises:
            httpx.HTTPStatusError: If token exchange fails
        """
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data=payload,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            )

            if response.status_code != 200:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"   Response: {response.text}")

            response.raise_for_status()
            token_data = response.json()

            # Add expiration timestamp
            token_data["expires_at"] = datetime.now(timezone.utc) + timedelta(
                seconds=token_data["expires_in"]
            )

            return token_data

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, any]:
        """
        Refresh an expired access token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token response with access_token, refresh_token, expires_in, etc.

        Raises:
            httpx.HTTPStatusError: If token refresh fails
        """
        print(f"🔄 Refreshing WHOOP access token...")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "offline",  # Required by WHOOP to get new refresh token
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                }
            )

            if response.status_code != 200:
                print(f"❌ Token refresh failed: {response.status_code}")
                print(f"   Response: {response.text}")

            response.raise_for_status()
            token_data = response.json()

            # Add expiration timestamp
            token_data["expires_at"] = datetime.now(timezone.utc) + timedelta(
                seconds=token_data["expires_in"]
            )

            print(f"✅ Access token refreshed successfully")

            return token_data

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token

        Args:
            token: Token to revoke

        Returns:
            True if successful
        """
        # WHOOP doesn't have a documented revoke endpoint in v2
        # Deletion happens by removing the connection in database
        return True

    def is_token_expired(self, expires_at: datetime) -> bool:
        """
        Check if token is expired or expiring soon

        Args:
            expires_at: Token expiration timestamp

        Returns:
            True if expired or expiring within 5 minutes
        """
        # Add 5 minute buffer to refresh before actual expiration
        buffer = timedelta(minutes=5)
        return datetime.now(timezone.utc) + buffer >= expires_at

    async def ensure_valid_token(
        self,
        access_token: str,
        refresh_token: str,
        expires_at: datetime
    ) -> Tuple[str, Optional[Dict[str, any]]]:
        """
        Ensure access token is valid, refreshing if necessary

        Args:
            access_token: Current access token
            refresh_token: Current refresh token
            expires_at: Token expiration timestamp

        Returns:
            Tuple of (valid_access_token, new_token_data_if_refreshed)
        """
        if not self.is_token_expired(expires_at):
            return access_token, None

        # Token expired, refresh it
        new_token_data = await self.refresh_access_token(refresh_token)
        return new_token_data["access_token"], new_token_data


# Singleton instance
whoop_oauth = WHOOPOAuthService()