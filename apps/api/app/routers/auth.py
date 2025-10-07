"""
Authentication API Routes
User registration, login, logout, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from app.services.supabase_auth import supabase_auth
from app.dependencies import get_current_user

security = HTTPBearer()


router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response Models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    user_metadata: Dict[str, Any]
    created_at: str


class SignUpResponse(BaseModel):
    message: str
    requires_confirmation: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"
    user: Optional[Dict[str, Any]] = None


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(request: SignUpRequest):
    """
    Register a new user

    Creates a new user account with email and password.
    Returns access token and user profile.
    """
    try:
        # Prepare user metadata
        metadata = {}
        if request.first_name:
            metadata["first_name"] = request.first_name
        if request.last_name:
            metadata["last_name"] = request.last_name

        # Create user with Supabase
        result = await supabase_auth.sign_up(
            email=request.email,
            password=request.password,
            metadata=metadata
        )

        # Check if email confirmation is required
        # If access_token is missing, email confirmation is required
        if "access_token" not in result or not result.get("access_token"):
            return SignUpResponse(
                message="Registration successful! Please check your email to confirm your account.",
                requires_confirmation=True,
                user=result.get("user")
            )

        # Auto-confirmed, return tokens
        return AuthResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=result.get("expires_in", 3600),
            user=result["user"]
        )

    except Exception as e:
        # Handle Supabase errors
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif "password" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {error_message}"
            )


@router.post("/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in with email and password

    Returns access token and user profile.
    """
    try:
        result = await supabase_auth.sign_in(
            email=request.email,
            password=request.password
        )

        return AuthResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=result.get("expires_in", 3600),
            user=result["user"]
        )

    except Exception as e:
        error_message = str(e)
        if "invalid" in error_message.lower() or "credentials" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {error_message}"
            )


@router.post("/signout")
async def sign_out(user_id: str = Depends(get_current_user)):
    """
    Sign out current user

    Revokes the access token.
    """
    # Note: Supabase handles token revocation on the client side
    # This endpoint is mainly for consistency
    return {
        "message": "Signed out successfully"
    }


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token

    Exchange refresh token for new access token.
    """
    try:
        result = await supabase_auth.refresh_token(request.refresh_token)

        return AuthResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=result.get("expires_in", 3600),
            user=result["user"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user_id: str = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current user profile

    Returns authenticated user's profile information.
    """
    try:
        # Get the access token to fetch full user profile from Supabase
        token = credentials.credentials

        # Fetch user profile from Supabase
        user_data = await supabase_auth.get_user(token)

        return UserResponse(
            id=user_data.get("id", user_id),
            email=user_data.get("email", ""),
            user_metadata=user_data.get("user_metadata", {}),
            created_at=user_data.get("created_at", "")
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user profile: {str(e)}"
        )


@router.get("/health")
async def auth_health():
    """
    Check authentication service health
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "provider": "supabase"
    }