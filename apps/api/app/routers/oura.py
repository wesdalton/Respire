"""
Oura Ring API Router

Handles Oura OAuth flow, connection management, and data synchronization.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.dependencies import get_current_user
from app.models import OuraConnection, HealthMetric
from app.schemas import (
    OuraAuthRequest,
    OuraAuthResponse,
    OuraTokenExchange,
    OuraConnectionResponse,
    OuraSyncRequest,
    OuraSyncResponse,
    OuraDisconnectResponse
)
from app.services.oura_oauth import oura_oauth
from app.services.oura_api import create_oura_client
from app.services.data_transformer import OuraDataTransformer
from app.services.burnout_calculator import BurnoutCalculator

router = APIRouter(prefix="/oura", tags=["oura"])


@router.post("/auth/authorize", response_model=OuraAuthResponse)
async def authorize_oura(request: OuraAuthRequest):
    """Generate Oura OAuth authorization URL"""
    auth_url, state = oura_oauth.generate_authorization_url(request.redirect_uri)
    return OuraAuthResponse(authorization_url=auth_url, state=state)


@router.post("/auth/callback", response_model=OuraConnectionResponse)
async def oura_callback(
    exchange: OuraTokenExchange,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth callback and store connection

    Steps:
    1. Exchange code for tokens
    2. Get Oura user profile
    3. Store/update connection
    4. Initial sync (90 days)
    5. Calculate burnout
    """
    # Exchange code for tokens
    token_data = await oura_oauth.exchange_code_for_token(
        exchange.code,
        exchange.redirect_uri
    )

    # Create API client
    client = create_oura_client(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_expires_at=token_data["token_expires_at"]
    )

    # Get user profile
    try:
        profile = await client.get_personal_info()
        oura_user_id = profile.get("id")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch Oura profile: {str(e)}"
        )

    # Check for existing connection
    stmt = select(OuraConnection).where(OuraConnection.user_id == user_id)
    result = await db.execute(stmt)
    existing_connection = result.scalar_one_or_none()

    if existing_connection:
        # Update existing connection
        existing_connection.access_token = token_data["access_token"]
        existing_connection.refresh_token = token_data["refresh_token"]
        existing_connection.token_expires_at = token_data["token_expires_at"]
        existing_connection.oura_user_id = oura_user_id
        existing_connection.connected_at = datetime.utcnow()
        existing_connection.sync_enabled = True
        connection = existing_connection
    else:
        # Create new connection
        connection = OuraConnection(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires_at=token_data["token_expires_at"],
            oura_user_id=oura_user_id,
            scope=oura_oauth.SCOPES,
            connected_at=datetime.utcnow(),
            sync_enabled=True
        )
        db.add(connection)

    await db.commit()
    await db.refresh(connection)

    # Initial sync - last 90 days
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=90)

    try:
        await sync_oura_data(
            user_id=user_id,
            connection=connection,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            db=db
        )
    except Exception as e:
        # Log error but don't fail the connection
        print(f"Initial sync error: {str(e)}")

    return OuraConnectionResponse(
        id=str(connection.id),
        user_id=str(connection.user_id),
        oura_user_id=connection.oura_user_id,
        connected_at=connection.connected_at,
        last_synced_at=connection.last_synced_at,
        sync_enabled=connection.sync_enabled
    )


@router.get("/connection", response_model=Optional[OuraConnectionResponse])
async def get_oura_connection(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's Oura connection status"""
    stmt = select(OuraConnection).where(OuraConnection.user_id == user_id)
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        return None

    return OuraConnectionResponse(
        id=str(connection.id),
        user_id=str(connection.user_id),
        oura_user_id=connection.oura_user_id,
        connected_at=connection.connected_at,
        last_synced_at=connection.last_synced_at,
        sync_enabled=connection.sync_enabled
    )


@router.post("/disconnect", response_model=OuraDisconnectResponse)
async def disconnect_oura(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect Oura and optionally revoke token"""
    stmt = select(OuraConnection).where(OuraConnection.user_id == user_id)
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="No Oura connection found")

    # Try to revoke token (don't fail if it doesn't work)
    try:
        await oura_oauth.revoke_token(connection.access_token)
    except Exception:
        pass

    # Delete connection
    await db.delete(connection)
    await db.commit()

    return OuraDisconnectResponse(success=True, message="Oura disconnected successfully")


@router.post("/sync/manual", response_model=OuraSyncResponse)
async def manual_sync(
    request: OuraSyncRequest = None,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger Oura data sync

    Default: Last 7 days
    Max: 90 days per request
    """
    stmt = select(OuraConnection).where(OuraConnection.user_id == user_id)
    result = await db.execute(stmt)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="No Oura connection found")

    if not connection.sync_enabled:
        raise HTTPException(status_code=400, detail="Sync is disabled for this connection")

    # Determine date range
    end_date = datetime.utcnow().date()
    if request and request.start_date:
        start_date = datetime.fromisoformat(request.start_date).date()
    else:
        start_date = end_date - timedelta(days=7)

    if request and request.end_date:
        end_date = datetime.fromisoformat(request.end_date).date()

    # Validate date range
    if (end_date - start_date).days > 90:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 90 days"
        )

    try:
        records_synced = await sync_oura_data(
            user_id=user_id,
            connection=connection,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            db=db
        )

        return OuraSyncResponse(
            success=True,
            records_synced=records_synced,
            last_synced_at=connection.last_synced_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )


async def sync_oura_data(
    user_id: str,
    connection: OuraConnection,
    start_date: str,
    end_date: str,
    db: AsyncSession
) -> int:
    """
    Internal function to sync Oura data

    Args:
        user_id: User ID
        connection: OuraConnection object
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        db: Database session

    Returns:
        Number of records synced
    """
    # Create API client with token refresh callback
    async def token_refresh_callback(refresh_token: str):
        new_tokens = await oura_oauth.refresh_access_token(refresh_token)
        # Update connection with new tokens
        connection.access_token = new_tokens["access_token"]
        connection.refresh_token = new_tokens["refresh_token"]
        connection.token_expires_at = new_tokens["token_expires_at"]
        await db.commit()
        return new_tokens

    client = create_oura_client(
        access_token=connection.access_token,
        refresh_token=connection.refresh_token,
        token_expires_at=connection.token_expires_at,
        token_refresh_callback=token_refresh_callback
    )

    # Fetch data from Oura
    daily_sleep = await client.get_daily_sleep(start_date, end_date)
    daily_activity = await client.get_daily_activity(start_date, end_date)
    daily_readiness = await client.get_daily_readiness(start_date, end_date)
    heart_rate = await client.get_heart_rate(
        f"{start_date}T00:00:00Z",
        f"{end_date}T23:59:59Z"
    )

    # Get user preferences for smart fallback
    from app.models import UserPreferences
    prefs_stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
    prefs_result = await db.execute(prefs_stmt)
    user_prefs = prefs_result.scalar_one_or_none()
    primary_device = user_prefs.primary_data_source if user_prefs else 'whoop'

    # Transform data
    transformer = OuraDataTransformer()
    health_metrics = transformer.transform_to_health_metrics(
        daily_sleep=daily_sleep,
        daily_activity=daily_activity,
        daily_readiness=daily_readiness,
        heart_rate_data=heart_rate
    )

    records_synced = 0

    # Upsert health metrics with smart fallback
    for metric_data in health_metrics:
        metric_date = metric_data["date"]

        # Check if record exists
        stmt = select(HealthMetric).where(
            HealthMetric.user_id == user_id,
            HealthMetric.date == metric_date
        )
        result = await db.execute(stmt)
        existing_metric = result.scalar_one_or_none()

        if existing_metric:
            # Smart fallback: Only overwrite if Oura is primary OR existing data is not from primary device
            should_update = (
                not existing_metric.data_source or  # No source set (legacy data)
                primary_device == 'oura' or  # Oura is primary
                existing_metric.data_source != primary_device  # Existing data is not from primary
            )

            if should_update:
                # Update existing record
                for key, value in metric_data.items():
                    if value is not None and key != "date":
                        setattr(existing_metric, key, value)
                existing_metric.data_source = "oura"
                records_synced += 1
            # else: Skip update - primary device data takes precedence
        else:
            # Create new record
            metric = HealthMetric(
                user_id=user_id,
                date=metric_date,
                data_source="oura",
                **{k: v for k, v in metric_data.items() if k != "date"}
            )
            db.add(metric)
            records_synced += 1

    # Update last sync time
    connection.last_synced_at = datetime.utcnow()
    await db.commit()

    # Auto-calculate burnout after sync if we have data
    if records_synced > 0:
        try:
            from app.models import BurnoutScore, MoodRating
            from datetime import date

            # Get last 14 days for calculation
            calc_start_date = date.today() - timedelta(days=14)

            health_calc_result = await db.execute(
                select(HealthMetric).where(
                    HealthMetric.user_id == user_id,
                    HealthMetric.date >= calc_start_date
                ).order_by(HealthMetric.date)
            )
            health_calc_metrics = health_calc_result.scalars().all()

            mood_calc_result = await db.execute(
                select(MoodRating).where(
                    MoodRating.user_id == user_id,
                    MoodRating.date >= calc_start_date
                ).order_by(MoodRating.date)
            )
            mood_calc_ratings = mood_calc_result.scalars().all()

            if health_calc_metrics or mood_calc_ratings:
                # Convert to dicts
                health_dicts = [
                    {
                        "date": m.date,
                        "recovery_score": m.recovery_score,
                        "resting_hr": m.resting_hr,
                        "hrv": m.hrv,
                        "sleep_duration_minutes": m.sleep_duration_minutes,
                        "sleep_quality_score": m.sleep_quality_score,
                        "day_strain": m.day_strain
                    }
                    for m in health_calc_metrics
                ]

                mood_dicts = [
                    {"date": m.date, "rating": m.rating}
                    for m in mood_calc_ratings
                ]

                # Calculate risk
                calculator = BurnoutCalculator()
                risk_analysis = calculator.calculate_overall_risk(
                    health_metrics=health_dicts,
                    mood_ratings=mood_dicts
                )

                # Check if burnout score already exists for today
                today = date.today()
                existing_burnout_result = await db.execute(
                    select(BurnoutScore).where(
                        BurnoutScore.user_id == user_id,
                        BurnoutScore.date == today
                    )
                )
                existing_burnout = existing_burnout_result.scalar_one_or_none()

                if existing_burnout:
                    # Update existing record
                    existing_burnout.overall_risk_score = risk_analysis["overall_risk_score"]
                    existing_burnout.risk_factors = risk_analysis["risk_factors"]
                    existing_burnout.confidence_score = risk_analysis["confidence_score"]
                    existing_burnout.data_points_used = risk_analysis["data_points_used"]
                else:
                    # Create new record
                    new_burnout = BurnoutScore(
                        user_id=user_id,
                        date=today,
                        overall_risk_score=risk_analysis["overall_risk_score"],
                        risk_factors=risk_analysis["risk_factors"],
                        confidence_score=risk_analysis["confidence_score"],
                        data_points_used=risk_analysis["data_points_used"]
                    )
                    db.add(new_burnout)

                await db.commit()
        except Exception as e:
            # Don't fail the sync if burnout calculation fails
            print(f"Burnout calculation error: {str(e)}")

    return records_synced
