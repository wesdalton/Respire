"""
Supabase Authentication Service
Handles user authentication with Supabase Auth
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
from jose import JWTError, jwt


class SupabaseAuthService:
    """Supabase authentication service"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

        # Allow missing credentials in development
        if not self.supabase_url or not self.supabase_anon_key:
            print("⚠️  WARNING: Supabase credentials not set")
            print("   Authentication endpoints will not work until configured")
            self.supabase_url = "http://localhost:54321"
            self.supabase_anon_key = "PLACEHOLDER"
            self.jwt_secret = "PLACEHOLDER"

        self.auth_url = f"{self.supabase_url}/auth/v1"

    async def sign_up(
        self,
        email: str,
        password: str,
        metadata: Optional[Dict[str, Any]] = None,
        redirect_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register new user with Supabase Auth

        Args:
            email: User email
            password: User password
            metadata: Additional user metadata
            redirect_to: URL to redirect to after email confirmation

        Returns:
            User data and session tokens

        Raises:
            httpx.HTTPStatusError: If registration fails
        """
        # Use production URL if not specified
        if not redirect_to:
            redirect_to = os.getenv("APP_URL", "https://app.tryrespire.ai")

        payload = {
            "email": email,
            "password": password,
            "data": metadata or {},
            "options": {
                "emailRedirectTo": f"{redirect_to}/auth/confirm"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/signup",
                json=payload,
                headers={
                    "apikey": self.supabase_anon_key,
                    "Content-Type": "application/json"
                }
            )

            response.raise_for_status()
            return response.json()

    async def sign_in(
        self,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Sign in user with email and password

        Args:
            email: User email
            password: User password

        Returns:
            User data and session tokens

        Raises:
            Exception: With user-friendly error message
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token?grant_type=password",
                json={
                    "email": email,
                    "password": password
                },
                headers={
                    "apikey": self.supabase_anon_key,
                    "Content-Type": "application/json"
                }
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error_description") or error_data.get("msg") or "Authentication failed"
                except Exception:
                    error_message = "Invalid email or password"
                raise Exception(error_message)

            return response.json()

    async def sign_out(self, access_token: str) -> bool:
        """
        Sign out user and revoke token

        Args:
            access_token: User's access token

        Returns:
            True if successful
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/logout",
                headers={
                    "apikey": self.supabase_anon_key,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )

            return response.status_code == 204

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token and refresh token

        Raises:
            httpx.HTTPStatusError: If refresh fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token?grant_type=refresh_token",
                json={
                    "refresh_token": refresh_token
                },
                headers={
                    "apikey": self.supabase_anon_key,
                    "Content-Type": "application/json"
                }
            )

            response.raise_for_status()
            return response.json()

    async def get_user(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile from access token

        Args:
            access_token: User's access token

        Returns:
            User data

        Raises:
            httpx.HTTPStatusError: If token is invalid
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.auth_url}/user",
                headers={
                    "apikey": self.supabase_anon_key,
                    "Authorization": f"Bearer {access_token}",
                }
            )

            response.raise_for_status()
            return response.json()

    async def update_user(
        self,
        access_token: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user metadata

        Args:
            access_token: User's access token
            metadata: User metadata to update

        Returns:
            Updated user data

        Raises:
            httpx.HTTPStatusError: If update fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.auth_url}/user",
                json={
                    "data": metadata
                },
                headers={
                    "apikey": self.supabase_anon_key,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )

            response.raise_for_status()
            return response.json()

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and extract payload

        Args:
            token: JWT access token

        Returns:
            Token payload if valid, None otherwise
        """
        if not self.jwt_secret or self.jwt_secret == "PLACEHOLDER":
            # Development mode: basic validation
            try:
                # Decode without verification for development
                payload = jwt.decode(token, key="", options={"verify_signature": False})
                return payload
            except JWTError:
                return None

        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience="authenticated"
            )
            return payload
        except JWTError:
            return None

    def extract_user_id(self, token: str) -> Optional[str]:
        """
        Extract user ID from JWT token

        Args:
            token: JWT access token

        Returns:
            User ID if valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None


# Singleton instance
supabase_auth = SupabaseAuthService()