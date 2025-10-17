"""
Health Metrics and Dashboard API Routes
Query health data, calculate burnout risk, generate insights
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import HealthMetric, MoodRating, BurnoutScore, AIInsight, WHOOPConnection
from app.schemas import (
    HealthMetricResponse,
    BurnoutScoreResponse,
    AIInsightResponse,
    DashboardResponse,
    DashboardMetrics
)
from app.services.burnout_calculator import burnout_calculator
from app.services.ai_insights import ai_insights_service


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/metrics", response_model=List[HealthMetricResponse])
async def get_health_metrics(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get health metrics for authenticated user

    Returns metrics sorted by date (oldest first for charts)
    """
    query = select(HealthMetric).where(HealthMetric.user_id == user_id)

    if start_date:
        query = query.where(HealthMetric.date >= start_date)
    if end_date:
        query = query.where(HealthMetric.date <= end_date)

    query = query.order_by(HealthMetric.date.asc()).limit(limit)

    result = await db.execute(query)
    metrics = result.scalars().all()

    return [
        HealthMetricResponse(
            id=m.id,
            user_id=m.user_id,
            date=m.date,
            recovery_score=m.recovery_score,
            resting_hr=m.resting_hr,
            hrv=m.hrv,
            sleep_duration_minutes=m.sleep_duration_minutes,
            sleep_quality_score=m.sleep_quality_score,
            sleep_latency_minutes=m.sleep_latency_minutes,
            time_in_bed_minutes=m.time_in_bed_minutes,
            sleep_consistency_score=m.sleep_consistency_score,
            day_strain=m.day_strain,
            workout_count=m.workout_count,
            average_hr=m.average_hr,
            max_hr=m.max_hr,
            created_at=m.created_at,
            updated_at=m.updated_at
        )
        for m in metrics
    ]


@router.post("/burnout/calculate", response_model=BurnoutScoreResponse)
async def calculate_burnout_risk(
    days: int = Query(14, ge=7, le=90, description="Days to analyze"),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate current burnout risk score

    Analyzes recent health metrics and mood ratings to calculate risk.
    Stores the result in the database for historical tracking.
    """
    start_date = date.today() - timedelta(days=days)

    # Fetch health metrics
    health_result = await db.execute(
        select(HealthMetric).where(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.date >= start_date
            )
        ).order_by(HealthMetric.date)
    )
    health_metrics = health_result.scalars().all()

    # Fetch mood ratings
    mood_result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date >= start_date
            )
        ).order_by(MoodRating.date)
    )
    mood_ratings = mood_result.scalars().all()

    if not health_metrics and not mood_ratings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient data to calculate burnout risk. Need at least some health metrics or mood ratings."
        )

    # Convert to dictionaries for calculator
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
        for m in health_metrics
    ]

    mood_dicts = [
        {"date": m.date, "rating": m.rating}
        for m in mood_ratings
    ]

    # Calculate risk
    risk_analysis = burnout_calculator.calculate_overall_risk(
        health_metrics=health_dicts,
        mood_ratings=mood_dicts
    )

    # Store burnout score
    burnout_score = BurnoutScore(
        user_id=user_id,
        date=date.today(),
        overall_risk_score=risk_analysis["overall_risk_score"],
        risk_factors=risk_analysis["risk_factors"],
        confidence_score=risk_analysis["confidence_score"],
        data_points_used=risk_analysis["data_points_used"]
    )

    db.add(burnout_score)
    await db.commit()
    await db.refresh(burnout_score)

    return BurnoutScoreResponse(
        id=burnout_score.id,
        user_id=burnout_score.user_id,
        date=burnout_score.date,
        overall_risk_score=burnout_score.overall_risk_score,
        risk_factors=burnout_score.risk_factors,
        confidence_score=burnout_score.confidence_score,
        data_points_used=burnout_score.data_points_used,
        calculated_at=burnout_score.calculated_at
    )


@router.get("/burnout/history", response_model=List[BurnoutScoreResponse])
async def get_burnout_history(
    limit: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical burnout risk scores
    """
    result = await db.execute(
        select(BurnoutScore).where(
            BurnoutScore.user_id == user_id
        ).order_by(BurnoutScore.date.desc()).limit(limit)
    )
    scores = result.scalars().all()

    return [
        BurnoutScoreResponse(
            id=s.id,
            user_id=s.user_id,
            date=s.date,
            overall_risk_score=s.overall_risk_score,
            risk_factors=s.risk_factors,
            confidence_score=s.confidence_score,
            data_points_used=s.data_points_used,
            calculated_at=s.calculated_at
        )
        for s in scores
    ]


@router.post("/insights/generate")
async def generate_ai_insight(
    insight_type: str = Query("weekly_summary", description="Type: weekly_summary, burnout_alert, trend_analysis"),
    days: int = Query(14, ge=7, le=90),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered health insight

    First calculates burnout risk, then generates personalized insight using AI.
    """
    start_date = date.today() - timedelta(days=days)

    # Fetch data
    health_result = await db.execute(
        select(HealthMetric).where(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.date >= start_date
            )
        ).order_by(HealthMetric.date)
    )
    health_metrics = health_result.scalars().all()

    mood_result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date >= start_date
            )
        ).order_by(MoodRating.date)
    )
    mood_ratings = mood_result.scalars().all()

    if not health_metrics and not mood_ratings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient data to generate insights"
        )

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
        for m in health_metrics
    ]

    mood_dicts = [
        {"date": m.date, "rating": m.rating}
        for m in mood_ratings
    ]

    # Calculate burnout risk
    risk_analysis = burnout_calculator.calculate_overall_risk(
        health_metrics=health_dicts,
        mood_ratings=mood_dicts
    )

    # Generate AI insight
    insight_data = await ai_insights_service.generate_insight(
        insight_type=insight_type,
        health_metrics=health_dicts,
        mood_ratings=mood_dicts,
        burnout_analysis=risk_analysis
    )

    # Store insight
    ai_insight = AIInsight(
        user_id=user_id,
        insight_type=insight_type,
        date_range_start=start_date,
        date_range_end=date.today(),
        title=insight_data["title"],
        content=insight_data["content"],
        recommendations={"items": insight_data["recommendations"]},
        structured_data=insight_data.get("structured_data"),  # Store structured data
        metrics_snapshot=risk_analysis,
        model_used=insight_data["model_used"],
        tokens_used=insight_data.get("tokens_used", 0),
        expires_at=datetime.utcnow() + timedelta(days=7)  # Insights expire after 7 days
    )

    db.add(ai_insight)
    await db.commit()
    await db.refresh(ai_insight)

    return AIInsightResponse(
        id=ai_insight.id,
        user_id=ai_insight.user_id,
        insight_type=ai_insight.insight_type,
        date_range_start=ai_insight.date_range_start,
        date_range_end=ai_insight.date_range_end,
        title=ai_insight.title,
        content=ai_insight.content,
        recommendations=ai_insight.recommendations,
        structured_data=ai_insight.structured_data,
        metrics_snapshot=ai_insight.metrics_snapshot,
        model_used=ai_insight.model_used,
        tokens_used=ai_insight.tokens_used,
        created_at=ai_insight.created_at,
        expires_at=ai_insight.expires_at,
        helpful=ai_insight.helpful,
        user_feedback=ai_insight.user_feedback
    )


@router.get("/insights", response_model=List[AIInsightResponse])
async def get_ai_insights(
    limit: int = Query(10, ge=1, le=50),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent AI insights (not expired)
    """
    result = await db.execute(
        select(AIInsight).where(
            and_(
                AIInsight.user_id == user_id,
                AIInsight.expires_at > datetime.utcnow()
            )
        ).order_by(AIInsight.created_at.desc()).limit(limit)
    )
    insights = result.scalars().all()

    return [
        AIInsightResponse(
            id=i.id,
            user_id=i.user_id,
            insight_type=i.insight_type,
            date_range_start=i.date_range_start,
            date_range_end=i.date_range_end,
            title=i.title,
            content=i.content,
            recommendations=i.recommendations,
            structured_data=i.structured_data,
            metrics_snapshot=i.metrics_snapshot,
            model_used=i.model_used,
            tokens_used=i.tokens_used,
            created_at=i.created_at,
            expires_at=i.expires_at,
            helpful=i.helpful,
            user_feedback=i.user_feedback
        )
        for i in insights
    ]


@router.patch("/insights/{insight_id}/feedback")
async def update_insight_feedback(
    insight_id: str,
    helpful: bool = Query(..., description="Was this insight helpful?"),
    feedback: Optional[str] = Query(None, description="Optional feedback text"),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update feedback for an AI insight
    """
    from uuid import UUID

    result = await db.execute(
        select(AIInsight).where(
            and_(
                AIInsight.id == UUID(insight_id),
                AIInsight.user_id == user_id
            )
        )
    )
    insight = result.scalar_one_or_none()

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )

    insight.helpful = helpful
    if feedback:
        insight.user_feedback = feedback

    await db.commit()
    await db.refresh(insight)

    return AIInsightResponse(
        id=insight.id,
        user_id=insight.user_id,
        insight_type=insight.insight_type,
        date_range_start=insight.date_range_start,
        date_range_end=insight.date_range_end,
        title=insight.title,
        content=insight.content,
        recommendations=insight.recommendations,
        structured_data=insight.structured_data,
        metrics_snapshot=insight.metrics_snapshot,
        model_used=insight.model_used,
        tokens_used=insight.tokens_used,
        created_at=insight.created_at,
        expires_at=insight.expires_at,
        helpful=insight.helpful,
        user_feedback=insight.user_feedback
    )


@router.delete("/insights/{insight_id}")
async def delete_insight(
    insight_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an AI insight
    """
    from uuid import UUID

    result = await db.execute(
        select(AIInsight).where(
            and_(
                AIInsight.id == UUID(insight_id),
                AIInsight.user_id == user_id
            )
        )
    )
    insight = result.scalar_one_or_none()

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )

    await db.delete(insight)
    await db.commit()

    return {"message": "Insight deleted successfully"}


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    selected_date: Optional[date] = Query(None, description="Date to display metrics for (defaults to most recent with data)"),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete dashboard data

    Returns summary metrics for a specific date, recent data, burnout score, and latest insight.
    If no date specified, defaults to most recent date with data.
    """
    # Default to most recent date with data if no date specified
    if not selected_date:
        # Find the most recent date with any health data or mood data
        latest_health_result = await db.execute(
            select(HealthMetric.date).where(
                HealthMetric.user_id == user_id
            ).order_by(HealthMetric.date.desc()).limit(1)
        )
        latest_health_date = latest_health_result.scalar_one_or_none()

        latest_mood_result = await db.execute(
            select(MoodRating.date).where(
                MoodRating.user_id == user_id
            ).order_by(MoodRating.date.desc()).limit(1)
        )
        latest_mood_date = latest_mood_result.scalar_one_or_none()

        # Use the most recent of health or mood data
        if latest_health_date and latest_mood_date:
            selected_date = max(latest_health_date, latest_mood_date)
        elif latest_health_date:
            selected_date = latest_health_date
        elif latest_mood_date:
            selected_date = latest_mood_date
        else:
            # No data at all, default to yesterday
            selected_date = date.today() - timedelta(days=1)
    # Get WHOOP connection for last_synced_at
    whoop_result = await db.execute(
        select(WHOOPConnection).where(WHOOPConnection.user_id == user_id)
    )
    whoop_connection = whoop_result.scalar_one_or_none()

    # Get latest health metrics (last 30 days for display)
    thirty_days_ago = date.today() - timedelta(days=30)

    health_result = await db.execute(
        select(HealthMetric).where(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.date >= thirty_days_ago
            )
        ).order_by(HealthMetric.date.asc())
    )
    health_metrics = list(health_result.scalars().all())

    # Get latest mood ratings (last 30 days)
    mood_result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date >= thirty_days_ago
            )
        ).order_by(MoodRating.date.asc())
    )
    mood_ratings = list(mood_result.scalars().all())

    # Get total count of all health metrics (for "Days Tracked" stat)
    total_health_count = await db.execute(
        select(func.count(HealthMetric.id)).where(
            HealthMetric.user_id == user_id
        )
    )
    total_days_tracked = total_health_count.scalar()

    # Get total count of all mood ratings
    total_mood_count = await db.execute(
        select(func.count(MoodRating.id)).where(
            MoodRating.user_id == user_id
        )
    )
    total_mood_entries = total_mood_count.scalar()

    # Get latest insight
    insight_result = await db.execute(
        select(AIInsight).where(
            and_(
                AIInsight.user_id == user_id,
                AIInsight.expires_at > datetime.utcnow()
            )
        ).order_by(AIInsight.created_at.desc()).limit(1)
    )
    latest_insight = insight_result.scalar_one_or_none()

    # Count pending sync jobs (placeholder - we'll implement later)
    pending_sync_jobs = 0

    # Get metrics for the selected date
    selected_metric_result = await db.execute(
        select(HealthMetric).where(
            and_(
                HealthMetric.user_id == user_id,
                HealthMetric.date == selected_date
            )
        )
    )
    selected_metric = selected_metric_result.scalar_one_or_none()

    # Get mood for the selected date
    selected_mood_result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date == selected_date
            )
        )
    )
    selected_mood = selected_mood_result.scalar_one_or_none()

    # Get burnout score for the selected date (or closest available)
    selected_burnout_result = await db.execute(
        select(BurnoutScore).where(
            and_(
                BurnoutScore.user_id == user_id,
                BurnoutScore.date <= selected_date
            )
        ).order_by(BurnoutScore.date.desc()).limit(1)
    )
    selected_burnout = selected_burnout_result.scalar_one_or_none()

    # Auto-calculate burnout if missing or stale for selected date
    should_calculate = False
    if not selected_burnout:
        should_calculate = True
        print(f"🔄 No burnout score found for {selected_date}, will auto-calculate")
    elif selected_burnout.calculated_at < datetime.now(timezone.utc) - timedelta(hours=24):
        should_calculate = True
        print(f"🔄 Burnout score is stale (>24h old), will recalculate")

    if should_calculate and (health_metrics or mood_ratings):
        try:
            # Calculate burnout automatically for selected date
            start_date_calc = selected_date - timedelta(days=14)  # Use 14 days before selected date

            # Fetch data for calculation
            health_calc_result = await db.execute(
                select(HealthMetric).where(
                    and_(
                        HealthMetric.user_id == user_id,
                        HealthMetric.date >= start_date_calc,
                        HealthMetric.date <= selected_date
                    )
                ).order_by(HealthMetric.date)
            )
            health_calc_metrics = health_calc_result.scalars().all()

            mood_calc_result = await db.execute(
                select(MoodRating).where(
                    and_(
                        MoodRating.user_id == user_id,
                        MoodRating.date >= start_date_calc,
                        MoodRating.date <= selected_date
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

                # Store burnout score for selected date
                new_burnout = BurnoutScore(
                    user_id=user_id,
                    date=selected_date,
                    overall_risk_score=risk_analysis["overall_risk_score"],
                    risk_factors=risk_analysis["risk_factors"],
                    confidence_score=risk_analysis["confidence_score"],
                    data_points_used=risk_analysis["data_points_used"]
                )

                db.add(new_burnout)
                await db.commit()
                await db.refresh(new_burnout)
                selected_burnout = new_burnout

                print(f"✅ Auto-calculated burnout for {selected_date}: {risk_analysis['overall_risk_score']}%")

        except Exception as e:
            # Don't fail dashboard if burnout calculation fails
            print(f"⚠️ Auto-calculation failed (non-critical): {e}")

    # Determine burnout trend for selected date
    burnout_trend = None
    if selected_burnout:
        # Get previous burnout score to compare
        prev_burnout_result = await db.execute(
            select(BurnoutScore).where(
                and_(
                    BurnoutScore.user_id == user_id,
                    BurnoutScore.date < selected_burnout.date
                )
            ).order_by(BurnoutScore.date.desc()).limit(1)
        )
        prev_burnout = prev_burnout_result.scalar_one_or_none()

        if prev_burnout:
            if selected_burnout.overall_risk_score < prev_burnout.overall_risk_score:
                burnout_trend = "improving"
            elif selected_burnout.overall_risk_score > prev_burnout.overall_risk_score:
                burnout_trend = "worsening"
            else:
                burnout_trend = "stable"

    metrics = DashboardMetrics(
        latest_recovery=selected_metric.recovery_score if selected_metric else None,
        latest_hrv=selected_metric.hrv if selected_metric else None,
        latest_resting_hr=selected_metric.resting_hr if selected_metric else None,
        latest_strain=selected_metric.day_strain if selected_metric else None,
        latest_sleep_quality=selected_metric.sleep_quality_score if selected_metric else None,
        latest_mood=selected_mood.rating if selected_mood else None,
        burnout_risk_score=selected_burnout.overall_risk_score if selected_burnout else None,
        burnout_trend=burnout_trend,
        days_tracked=total_days_tracked,  # Total across all time, not just recent
        mood_entries=total_mood_entries,  # Total mood entries
        last_sync=whoop_connection.last_synced_at if whoop_connection and whoop_connection.last_synced_at else None
    )

    # Convert to response schemas
    recent_health_data = [
        HealthMetricResponse(
            id=m.id,
            user_id=m.user_id,
            date=m.date,
            recovery_score=m.recovery_score,
            resting_hr=m.resting_hr,
            hrv=m.hrv,
            sleep_duration_minutes=m.sleep_duration_minutes,
            sleep_quality_score=m.sleep_quality_score,
            sleep_latency_minutes=m.sleep_latency_minutes,
            time_in_bed_minutes=m.time_in_bed_minutes,
            sleep_consistency_score=m.sleep_consistency_score,
            day_strain=m.day_strain,
            workout_count=m.workout_count,
            average_hr=m.average_hr,
            max_hr=m.max_hr,
            created_at=m.created_at,
            updated_at=m.updated_at
        )
        for m in health_metrics
    ]

    from app.schemas import MoodRatingResponse
    recent_moods = [
        MoodRatingResponse(
            id=m.id,
            user_id=m.user_id,
            date=m.date,
            rating=m.rating,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at
        )
        for m in mood_ratings
    ]

    selected_burnout_response = None
    if selected_burnout:
        selected_burnout_response = BurnoutScoreResponse(
            id=selected_burnout.id,
            user_id=selected_burnout.user_id,
            date=selected_burnout.date,
            overall_risk_score=selected_burnout.overall_risk_score,
            risk_factors=selected_burnout.risk_factors,
            confidence_score=selected_burnout.confidence_score,
            data_points_used=selected_burnout.data_points_used,
            calculated_at=selected_burnout.calculated_at
        )

    latest_insight_response = None
    if latest_insight:
        latest_insight_response = AIInsightResponse(
            id=latest_insight.id,
            user_id=latest_insight.user_id,
            insight_type=latest_insight.insight_type,
            date_range_start=latest_insight.date_range_start,
            date_range_end=latest_insight.date_range_end,
            title=latest_insight.title,
            content=latest_insight.content,
            recommendations=latest_insight.recommendations,
            structured_data=latest_insight.structured_data,
            metrics_snapshot=latest_insight.metrics_snapshot,
            model_used=latest_insight.model_used,
            tokens_used=latest_insight.tokens_used,
            created_at=latest_insight.created_at,
            expires_at=latest_insight.expires_at,
            helpful=latest_insight.helpful,
            user_feedback=latest_insight.user_feedback
        )

    return DashboardResponse(
        user_id=user_id,
        metrics=metrics,
        recent_health_data=recent_health_data,
        recent_moods=recent_moods,
        latest_burnout_score=selected_burnout_response,
        latest_insight=latest_insight_response,
        pending_sync_jobs=pending_sync_jobs
    )