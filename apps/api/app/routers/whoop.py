"""
WHOOP Integration API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, date
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import WHOOPConnection, HealthMetric
from app.schemas import (
    WHOOPAuthRequest,
    WHOOPAuthResponse,
    WHOOPTokenExchange,
    WHOOPConnectionResponse,
)
from app.services.whoop_oauth import whoop_oauth
from app.services.whoop_api import create_whoop_client
from app.services.data_transformer import whoop_transformer


router = APIRouter(prefix="/whoop", tags=["whoop"])


@router.post("/auth/authorize", response_model=WHOOPAuthResponse)
async def authorize_whoop(request: WHOOPAuthRequest):
    """
    Step 1: Get WHOOP authorization URL

    User should be redirected to this URL to grant access
    """
    try:
        auth_url, state = whoop_oauth.generate_authorization_url(request.redirect_uri)

        return WHOOPAuthResponse(
            authorization_url=auth_url,
            state=state
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )


@router.post("/auth/callback", response_model=WHOOPConnectionResponse)
async def whoop_callback(
    exchange: WHOOPTokenExchange,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Handle OAuth callback and exchange code for tokens

    This endpoint should be called after user grants access and is redirected back
    """
    try:
        # Exchange authorization code for tokens
        token_data = await whoop_oauth.exchange_code_for_token(
            code=exchange.code,
            redirect_uri=exchange.redirect_uri
        )

        # Get WHOOP user profile
        whoop_client = create_whoop_client(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=token_data["expires_at"]
        )
        profile = await whoop_client.get_user_profile()

        # Check if connection already exists
        result = await db.execute(
            select(WHOOPConnection).where(WHOOPConnection.user_id == user_id)
        )
        connection = result.scalar_one_or_none()

        # Convert whoop_user_id to string (WHOOP returns it as an integer)
        whoop_user_id = str(profile.get("user_id")) if profile.get("user_id") else None

        if connection:
            # Update existing connection
            connection.access_token = token_data["access_token"]
            connection.refresh_token = token_data.get("refresh_token")
            connection.token_expires_at = token_data["expires_at"]
            connection.whoop_user_id = whoop_user_id
            connection.scope = token_data.get("scope", "").split()
            connection.connected_at = datetime.utcnow()
            connection.sync_enabled = True
        else:
            # Create new connection
            connection = WHOOPConnection(
                user_id=user_id,
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                token_expires_at=token_data["expires_at"],
                whoop_user_id=whoop_user_id,
                scope=token_data.get("scope", "").split(),
                sync_enabled=True
            )
            db.add(connection)

        await db.commit()
        await db.refresh(connection)

        # Trigger initial sync in the background (last 90 days)
        try:
            from datetime import timedelta

            # Create WHOOP client for syncing
            sync_client = create_whoop_client(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=token_data["expires_at"]
            )

            # Fetch last 90 days of data
            start_date = date.today() - timedelta(days=90)
            end_date = date.today()

            data = await sync_client.sync_all_data(start_date, end_date)

            # Transform and store health metrics
            health_metrics = whoop_transformer.transform_sync_data(
                user_id=user_id,
                whoop_data=data
            )

            records_inserted = 0
            for metric_data in health_metrics:
                # Check if record exists
                existing = await db.execute(
                    select(HealthMetric).where(
                        HealthMetric.user_id == user_id,
                        HealthMetric.date == metric_data["date"]
                    )
                )
                existing_metric = existing.scalar_one_or_none()

                if not existing_metric:
                    # Insert new record
                    new_metric = HealthMetric(**metric_data)
                    db.add(new_metric)
                    records_inserted += 1

            # Update last synced timestamp
            connection.last_synced_at = datetime.utcnow()
            await db.commit()


        except Exception as sync_error:
            # Don't fail the connection if sync fails - user can manually sync
            # Rollback any partial sync changes but keep the connection
            await db.rollback()
            # Re-commit just the connection
            await db.commit()

        return WHOOPConnectionResponse(
            id=connection.id,
            user_id=connection.user_id,
            whoop_user_id=connection.whoop_user_id,
            scope=connection.scope,
            connected_at=connection.connected_at,
            last_synced_at=connection.last_synced_at,
            sync_enabled=connection.sync_enabled
        )

    except Exception as e:
        await db.rollback()
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect WHOOP account: {str(e)}"
        )


@router.get("/connection", response_model=WHOOPConnectionResponse)
async def get_whoop_connection(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's WHOOP connection status
    """
    result = await db.execute(
        select(WHOOPConnection).where(WHOOPConnection.user_id == user_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WHOOP not connected"
        )

    return WHOOPConnectionResponse(
        id=connection.id,
        user_id=connection.user_id,
        whoop_user_id=connection.whoop_user_id,
        scope=connection.scope,
        connected_at=connection.connected_at,
        last_synced_at=connection.last_synced_at,
        sync_enabled=connection.sync_enabled
    )


@router.delete("/connection")
async def disconnect_whoop(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect WHOOP account
    """
    result = await db.execute(
        select(WHOOPConnection).where(WHOOPConnection.user_id == user_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WHOOP not connected"
        )

    await db.delete(connection)
    await db.commit()

    return {"message": "WHOOP account disconnected successfully"}


@router.post("/sync/manual")
async def manual_sync(
    user_id: str = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="Start date for sync"),
    end_date: Optional[date] = Query(None, description="End date for sync"),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger WHOOP data sync

    This will fetch data for the specified date range (or last 7 days by default)
    and store it in the database
    """
    # Get WHOOP connection
    result = await db.execute(
        select(WHOOPConnection).where(WHOOPConnection.user_id == user_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WHOOP not connected"
        )

    if not connection.sync_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sync is disabled for this account"
        )

    try:
        # Create WHOOP client
        whoop_client = create_whoop_client(
            access_token=connection.access_token,
            refresh_token=connection.refresh_token,
            expires_at=connection.token_expires_at
        )

        # Default to last 7 days if no dates specified
        if not start_date:
            from datetime import timedelta
            start_date = date.today() - timedelta(days=7)
        if not end_date:
            end_date = date.today()

        # Fetch all data
        data = await whoop_client.sync_all_data(start_date, end_date)

        # Update connection tokens if they were refreshed
        if whoop_client.access_token != connection.access_token:
            connection.access_token = whoop_client.access_token
            connection.refresh_token = whoop_client.refresh_token
            connection.token_expires_at = whoop_client.expires_at
            await db.commit()

        # Get user preferences for smart fallback
        from app.models import UserPreferences
        prefs_stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
        prefs_result = await db.execute(prefs_stmt)
        user_prefs = prefs_result.scalar_one_or_none()
        primary_device = user_prefs.primary_data_source if user_prefs else 'whoop'

        # Transform WHOOP data to HealthMetric format
        health_metrics = whoop_transformer.transform_sync_data(
            user_id=user_id,
            whoop_data=data
        )

        # Store health metrics in database with smart fallback
        records_inserted = 0
        records_updated = 0

        for metric_data in health_metrics:
            # Check if record exists
            existing = await db.execute(
                select(HealthMetric).where(
                    HealthMetric.user_id == user_id,
                    HealthMetric.date == metric_data["date"]
                )
            )
            existing_metric = existing.scalar_one_or_none()

            if existing_metric:
                # Smart fallback: Only overwrite if WHOOP is primary OR existing data is not from primary device
                should_update = (
                    not existing_metric.data_source or  # No source set (legacy data)
                    primary_device == 'whoop' or  # WHOOP is primary
                    existing_metric.data_source != primary_device  # Existing data is not from primary
                )

                if should_update:
                    # Update existing record
                    for key, value in metric_data.items():
                        if key not in ["user_id", "date"]:
                            setattr(existing_metric, key, value)
                    existing_metric.data_source = 'whoop'
                    records_updated += 1
                # else: Skip update - primary device data takes precedence
            else:
                # Insert new record with data source
                new_metric = HealthMetric(**metric_data, data_source='whoop')
                db.add(new_metric)
                records_inserted += 1

        # Update last synced timestamp
        connection.last_synced_at = datetime.utcnow()

        # Update tokens if they were refreshed
        if whoop_client.access_token != connection.access_token:
            connection.access_token = whoop_client.access_token
            connection.refresh_token = whoop_client.refresh_token
            connection.token_expires_at = whoop_client.expires_at

        await db.commit()

        # Auto-calculate burnout after sync if we have enough data
        if records_inserted + records_updated > 0:
            try:
                from app.services.burnout_calculator import burnout_calculator
                from app.models import BurnoutScore, MoodRating

                # Get last 14 days for calculation
                calc_start_date = date.today() - timedelta(days=14)

                health_calc_result = await db.execute(
                    select(HealthMetric).where(
                        and_(
                            HealthMetric.user_id == user_id,
                            HealthMetric.date >= calc_start_date
                        )
                    ).order_by(HealthMetric.date)
                )
                health_calc_metrics = health_calc_result.scalars().all()

                mood_calc_result = await db.execute(
                    select(MoodRating).where(
                        and_(
                            MoodRating.user_id == user_id,
                            MoodRating.date >= calc_start_date
                        )
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
                    risk_analysis = burnout_calculator.calculate_overall_risk(
                        health_metrics=health_dicts,
                        mood_ratings=mood_dicts
                    )

                    # Check if burnout score already exists for today
                    today = date.today()
                    existing_burnout_result = await db.execute(
                        select(BurnoutScore).where(
                            and_(
                                BurnoutScore.user_id == user_id,
                                BurnoutScore.date == today
                            )
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


            except Exception as calc_error:
                # Don't fail sync if burnout calculation fails
                await db.rollback()

        return {
            "message": "Sync completed successfully",
            "data": {
                "cycles": len(data["cycles"]),
                "recovery": len(data["recovery"]),
                "sleep": len(data["sleep"]),
                "workouts": len(data["workouts"]),
            },
            "metrics": {
                "inserted": records_inserted,
                "updated": records_updated,
                "total": records_inserted + records_updated
            },
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    except Exception as e:
        await db.rollback()
        import traceback
        error_details = traceback.format_exc()

        # Check if it's an authentication error
        error_str = str(e)
        if "401" in error_str or "Unauthorized" in error_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="WHOOP authorization expired. Please reconnect your WHOOP account in Settings."
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )