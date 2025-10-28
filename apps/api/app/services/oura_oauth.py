"""
Oura OAuth2 Service

Handles OAuth2 authorization flow for Oura Ring API.
Implements authorization code flow with Basic Authentication for token exchange.
"""

import os
import base64
import secrets
from datetime import datetime, timedelta
from typing import Dict, Tuple
from urllib.parse import urlencode

import httpx


class OuraOAuthService:
    """Service for handling Oura OAuth2 authentication"""

    AUTH_BASE_URL = "https://cloud.ouraring.com/oauth/authorize"
    TOKEN_URL = "https://api.ouraring.com/oauth/token"
    SCOPES = [
        "email",
        "personal",
        "daily",
        "heartrate",
        "tag",
        "workout",
        "session",
        "spo2",
        "ring_configuration",
        "stress"
    ]

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None
    ):
        self.client_id = client_id or os.getenv("OURA_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OURA_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("OURA_REDIRECT_URI")

        if not self.client_id or not self.client_secret:
            raise ValueError("OURA_CLIENT_ID and OURA_CLIENT_SECRET must be set")

    def _get_basic_auth_header(self) -> str:
        """Generate Basic Auth header for token exchange"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def generate_authorization_url(self, redirect_uri: str = None) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL with state parameter

        Args:
            redirect_uri: Optional override for redirect URI

        Returns:
            Tuple of (authorization_url, state)
        """
        state = secrets.token_urlsafe(32)
        uri = redirect_uri or self.redirect_uri

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": uri,
            "scope": " ".join(self.SCOPES),
            "state": state
        }

        auth_url = f"{self.AUTH_BASE_URL}?{urlencode(params)}"
        return auth_url, state

    def get_authorization_url(self, state: str = None, redirect_uri: str = None) -> str:
        """
        Generate OAuth authorization URL

        Args:
            state: Optional state parameter for CSRF protection
            redirect_uri: Optional override for redirect URI

        Returns:
            Authorization URL string
        """
        if not state:
            state = secrets.token_urlsafe(32)

        uri = redirect_uri or self.redirect_uri

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": uri,
            "scope": " ".join(self.SCOPES),
            "state": state
        }

        return f"{self.AUTH_BASE_URL}?{urlencode(params)}"

    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str = None
    ) -> Dict:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback
            redirect_uri: Must match the redirect_uri used in authorization

        Returns:
            Dict containing access_token, refresh_token, expires_in, token_type
        """
        uri = redirect_uri or self.redirect_uri

        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": uri
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            token_data = response.json()

        # Calculate token expiration
        expires_in = token_data.get("expires_in", 86400)  # Default 24 hours
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_in": expires_in,
            "token_expires_at": token_expires_at
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token

        NOTE: Oura uses single-use refresh tokens. Each refresh returns a NEW
        refresh token that must be stored and used for the next refresh.

        Args:
            refresh_token: Current refresh token

        Returns:
            Dict containing new access_token, refresh_token, expires_in
        """
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            token_data = response.json()

        # Calculate token expiration
        expires_in = token_data.get("expires_in", 86400)
        token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        return {
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],  # NEW refresh token
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_in": expires_in,
            "token_expires_at": token_expires_at
        }

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token

        Args:
            token: Token to revoke

        Returns:
            True if revocation successful
        """
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "token": token
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.ouraring.com/oauth/revoke",
                    headers=headers,
                    data=data
                )
                response.raise_for_status()
                return True
        except Exception:
            return False


# Global instance
oura_oauth = OuraOAuthService()
