"""
Authentication API Routes
User registration, login, logout, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import os
import uuid
from pathlib import Path

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
    profile_picture_url: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class ConfirmEmailRequest(BaseModel):
    token_hash: str
    type: str = "email"


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


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture_url: Optional[str] = None


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
        if request.profile_picture_url:
            metadata["profile_picture_url"] = request.profile_picture_url

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


@router.post("/confirm", response_model=AuthResponse)
async def confirm_email(request: ConfirmEmailRequest):
    """
    Confirm email address with token from confirmation email

    Returns access token and user profile after successful confirmation.
    """
    try:
        result = await supabase_auth.verify_otp(
            token_hash=request.token_hash,
            type=request.type
        )

        return AuthResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=result.get("expires_in", 3600),
            user=result["user"]
        )

    except Exception as e:
        error_message = str(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
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


@router.put("/me", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_id: str = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update current user profile

    Updates user metadata (first_name, last_name, profile_picture_url)
    """
    try:
        # Get the access token
        token = credentials.credentials

        # Prepare metadata update
        metadata = {}
        if request.first_name is not None:
            metadata["first_name"] = request.first_name
        if request.last_name is not None:
            metadata["last_name"] = request.last_name
        if request.profile_picture_url is not None:
            metadata["profile_picture_url"] = request.profile_picture_url

        # Update user metadata with Supabase
        updated_user = await supabase_auth.update_user(token, metadata)

        return UserResponse(
            id=updated_user.get("id", user_id),
            email=updated_user.get("email", ""),
            user_metadata=updated_user.get("user_metadata", {}),
            created_at=updated_user.get("created_at", "")
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload profile picture to Supabase Storage

    Uploads an image file to Supabase Storage bucket and returns the public URL
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )

        # Read file content
        content = await file.read()

        # Validate file size (max 5MB)
        if len(content) > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 5MB"
            )

        # Generate unique filename
        file_ext = Path(file.filename or 'image.jpg').suffix
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_ext}"

        # Upload to Supabase Storage
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not supabase_url or not supabase_service_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Storage configuration missing"
            )

        # Upload file to Supabase Storage bucket "profile-pictures"
        storage_url = f"{supabase_url}/storage/v1/object/profile-pictures/{unique_filename}"

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                storage_url,
                headers={
                    "Authorization": f"Bearer {supabase_service_key}",
                    "Content-Type": file.content_type or "image/jpeg",
                },
                content=content,
                timeout=30.0
            )

            if response.status_code not in [200, 201]:
                print(f"Supabase storage error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload to storage: {response.text}"
                )

        # Return public URL
        public_url = f"{supabase_url}/storage/v1/object/public/profile-pictures/{unique_filename}"

        return {"url": public_url}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.delete("/delete-all-data")
async def delete_all_user_data(user_id: str = Depends(get_current_user)):
    """
    Delete all user data (health metrics, moods, insights, burnout scores, WHOOP connection)

    This does NOT delete the user account itself, only their data.
    """
    from sqlalchemy import select, delete
    from app.database import get_db
    from app.models import HealthMetric, MoodRating, BurnoutScore, AIInsight, WHOOPConnection

    try:
        async for db in get_db():
            # Delete all data for this user
            await db.execute(delete(HealthMetric).where(HealthMetric.user_id == user_id))
            await db.execute(delete(MoodRating).where(MoodRating.user_id == user_id))
            await db.execute(delete(BurnoutScore).where(BurnoutScore.user_id == user_id))
            await db.execute(delete(AIInsight).where(AIInsight.user_id == user_id))
            await db.execute(delete(WHOOPConnection).where(WHOOPConnection.user_id == user_id))

            await db.commit()

            return {
                "message": "All account data has been permanently deleted"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user data: {str(e)}"
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


# User Preferences Endpoints
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import UserPreferences
from app.schemas import UserPreferencesResponse, UserPreferencesUpdate


@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences"""
    stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create default preferences
        prefs = UserPreferences(user_id=user_id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)

    return prefs


@router.patch("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    updates: UserPreferencesUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences"""
    stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
    result = await db.execute(stmt)
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create with provided values
        prefs = UserPreferences(user_id=user_id, **updates.model_dump(exclude_unset=True))
        db.add(prefs)
    else:
        # Update existing
        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(prefs, key, value)

    await db.commit()
    await db.refresh(prefs)
    return prefs