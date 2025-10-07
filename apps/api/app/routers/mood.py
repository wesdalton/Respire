"""
Mood Rating API Routes
Track daily mood and notes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import MoodRating, HealthMetric, BurnoutScore
from app.schemas import (
    MoodRatingCreate,
    MoodRatingUpdate,
    MoodRatingResponse
)
from app.services.burnout_calculator import burnout_calculator


router = APIRouter(prefix="/mood", tags=["mood"])


async def recalculate_burnout(user_id: str, db: AsyncSession):
    """
    Helper function to recalculate burnout score after mood/health data changes
    """
    try:
        print(f"🔄 Recalculating burnout after data change...")

        # Get last 14 days for calculation
        calc_start_date = date.today() - timedelta(days=14)

        # Fetch health metrics
        health_result = await db.execute(
            select(HealthMetric).where(
                and_(
                    HealthMetric.user_id == user_id,
                    HealthMetric.date >= calc_start_date
                )
            ).order_by(HealthMetric.date)
        )
        health_metrics = health_result.scalars().all()

        # Fetch mood ratings
        mood_result = await db.execute(
            select(MoodRating).where(
                and_(
                    MoodRating.user_id == user_id,
                    MoodRating.date >= calc_start_date
                )
            ).order_by(MoodRating.date)
        )
        mood_ratings = mood_result.scalars().all()

        if not health_metrics and not mood_ratings:
            print("⚠️  Insufficient data for burnout calculation")
            return

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
            # Update existing score
            existing_burnout.overall_risk_score = risk_analysis["overall_risk_score"]
            existing_burnout.risk_factors = risk_analysis["risk_factors"]
            existing_burnout.confidence_score = risk_analysis["confidence_score"]
            existing_burnout.data_points_used = risk_analysis["data_points_used"]
            existing_burnout.calculated_at = datetime.utcnow()
        else:
            # Create new score
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

        print(f"✅ Burnout recalculated: {risk_analysis['overall_risk_score']}%")

    except Exception as e:
        # Don't fail the main operation if burnout calculation fails
        print(f"⚠️ Burnout recalculation failed (non-critical): {e}")


@router.post("/", response_model=MoodRatingResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_rating(
    mood: MoodRatingCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new mood rating for a specific date

    If a rating already exists for this date, it will return an error.
    Use PUT to update existing ratings.
    """
    # Check if mood rating already exists for this date
    result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date == mood.date
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mood rating already exists for {mood.date}. Use PUT to update."
        )

    # Create new mood rating
    new_mood = MoodRating(
        user_id=user_id,
        date=mood.date,
        rating=mood.rating,
        notes=mood.notes
    )

    db.add(new_mood)
    await db.commit()
    await db.refresh(new_mood)

    # Recalculate burnout after mood change
    await recalculate_burnout(user_id, db)

    return MoodRatingResponse(
        id=new_mood.id,
        user_id=new_mood.user_id,
        date=new_mood.date,
        rating=new_mood.rating,
        notes=new_mood.notes,
        created_at=new_mood.created_at,
        updated_at=new_mood.updated_at
    )


@router.get("/", response_model=List[MoodRatingResponse])
async def list_mood_ratings(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    limit: int = Query(30, ge=1, le=365, description="Maximum number of records"),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get mood ratings for authenticated user

    Returns mood ratings sorted by date (most recent first)
    """
    query = select(MoodRating).where(MoodRating.user_id == user_id)

    # Apply date filters
    if start_date:
        query = query.where(MoodRating.date >= start_date)
    if end_date:
        query = query.where(MoodRating.date <= end_date)

    # Order by date descending and limit
    query = query.order_by(MoodRating.date.desc()).limit(limit)

    result = await db.execute(query)
    moods = result.scalars().all()

    return [
        MoodRatingResponse(
            id=mood.id,
            user_id=mood.user_id,
            date=mood.date,
            rating=mood.rating,
            notes=mood.notes,
            created_at=mood.created_at,
            updated_at=mood.updated_at
        )
        for mood in moods
    ]


@router.get("/{mood_date}", response_model=MoodRatingResponse)
async def get_mood_rating_by_date(
    mood_date: date,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get mood rating for a specific date
    """
    result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date == mood_date
            )
        )
    )
    mood = result.scalar_one_or_none()

    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mood rating found for {mood_date}"
        )

    return MoodRatingResponse(
        id=mood.id,
        user_id=mood.user_id,
        date=mood.date,
        rating=mood.rating,
        notes=mood.notes,
        created_at=mood.created_at,
        updated_at=mood.updated_at
    )


@router.put("/{mood_date}", response_model=MoodRatingResponse)
async def update_mood_rating(
    mood_date: date,
    update: MoodRatingUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update existing mood rating for a specific date
    """
    print(f"📝 Updating mood for date: {mood_date}")
    print(f"   Update data: rating={update.rating}, notes={update.notes}")

    result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date == mood_date
            )
        )
    )
    mood = result.scalar_one_or_none()

    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mood rating found for {mood_date}"
        )

    # Update fields if provided
    if update.rating is not None:
        mood.rating = update.rating
    if update.notes is not None:
        mood.notes = update.notes

    mood.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(mood)

    # Recalculate burnout after mood change
    await recalculate_burnout(user_id, db)

    return MoodRatingResponse(
        id=mood.id,
        user_id=mood.user_id,
        date=mood.date,
        rating=mood.rating,
        notes=mood.notes,
        created_at=mood.created_at,
        updated_at=mood.updated_at
    )


@router.delete("/{mood_date}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood_rating(
    mood_date: date,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete mood rating for a specific date
    """
    result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date == mood_date
            )
        )
    )
    mood = result.scalar_one_or_none()

    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No mood rating found for {mood_date}"
        )

    await db.delete(mood)
    await db.commit()

    # Recalculate burnout after mood deletion
    await recalculate_burnout(user_id, db)

    return None


@router.get("/stats/summary")
async def get_mood_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get mood statistics and trends
    """
    from datetime import timedelta
    from statistics import mean, median

    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(MoodRating).where(
            and_(
                MoodRating.user_id == user_id,
                MoodRating.date >= start_date
            )
        ).order_by(MoodRating.date)
    )
    moods = result.scalars().all()

    if not moods:
        return {
            "period_days": days,
            "data_points": 0,
            "message": "No mood data available for this period"
        }

    ratings = [m.rating for m in moods]

    # Calculate statistics
    avg_mood = mean(ratings)
    median_mood = median(ratings)

    # Count by mood level
    low_moods = sum(1 for r in ratings if r <= 4)  # 1-4 = low
    mid_moods = sum(1 for r in ratings if 5 <= r <= 7)  # 5-7 = moderate
    high_moods = sum(1 for r in ratings if r >= 8)  # 8-10 = high

    # Calculate trend (simple linear)
    if len(ratings) > 1:
        first_half = ratings[:len(ratings)//2]
        second_half = ratings[len(ratings)//2:]
        trend = "improving" if mean(second_half) > mean(first_half) else "declining"
    else:
        trend = "insufficient_data"

    # Find best and worst days
    best_day = max(moods, key=lambda m: m.rating)
    worst_day = min(moods, key=lambda m: m.rating)

    return {
        "period_days": days,
        "data_points": len(moods),
        "statistics": {
            "average": round(avg_mood, 1),
            "median": median_mood,
            "highest": max(ratings),
            "lowest": min(ratings)
        },
        "distribution": {
            "low_mood_days": low_moods,
            "moderate_mood_days": mid_moods,
            "high_mood_days": high_moods
        },
        "trend": trend,
        "best_day": {
            "date": best_day.date.isoformat(),
            "rating": best_day.rating,
            "notes": best_day.notes
        },
        "worst_day": {
            "date": worst_day.date.isoformat(),
            "rating": worst_day.rating,
            "notes": worst_day.notes
        }
    }