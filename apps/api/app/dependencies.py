"""
FastAPI Dependencies
Authentication and authorization dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.services.supabase_auth import supabase_auth


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Get current authenticated user ID from JWT token

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User ID (UUID string)

    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials

    user_id = supabase_auth.extract_user_id(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Get current user ID if token is provided, otherwise None

    Useful for endpoints that work with or without authentication

    Args:
        credentials: Bearer token from Authorization header (optional)

    Returns:
        User ID if authenticated, None otherwise
    """
    if not credentials:
        return None

    token = credentials.credentials
    return supabase_auth.extract_user_id(token)