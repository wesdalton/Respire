"""
Create dummy account with realistic WHOOP and mood data
Generates 3 months of data showing gradual burnout progression
"""
import asyncio
import random
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import os
from dotenv import load_dotenv
import httpx

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Import models
import sys
sys.path.append(os.path.dirname(__file__))
from app.models import HealthMetric, MoodRating

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/respire"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)


def generate_realistic_whoop_data(days: int = 90) -> list:
    """
    Generate realistic WHOOP data showing gradual burnout progression

    Timeline:
    - Days 0-30: Healthy, balanced training
    - Days 31-60: Increased training, declining recovery
    - Days 61-90: Burnout symptoms - low HRV, poor sleep, high strain
    """
    data = []
    start_date = date.today() - timedelta(days=days)

    for i in range(days):
        current_date = start_date + timedelta(days=i)

        # Calculate phase (0=healthy, 1=declining, 2=burnout)
        if i < 30:
            phase = 0  # Healthy phase
            recovery_base = 75
            hrv_base = 65
            sleep_quality_base = 80
            strain_base = 12
        elif i < 60:
            phase = 1  # Declining phase
            # Gradual decline
            progress = (i - 30) / 30
            recovery_base = 75 - (progress * 25)  # 75 -> 50
            hrv_base = 65 - (progress * 25)  # 65 -> 40
            sleep_quality_base = 80 - (progress * 25)  # 80 -> 55
            strain_base = 12 + (progress * 4)  # 12 -> 16
        else:
            phase = 2  # Burnout phase
            recovery_base = 45
            hrv_base = 35
            sleep_quality_base = 50
            strain_base = 17

        # Add daily variation
        recovery = max(10, min(100, int(recovery_base + random.gauss(0, 8))))
        hrv = max(20, min(100, recovery_base + random.gauss(0, 10)))
        resting_hr = int(60 - (recovery - 50) / 3)  # Lower recovery = higher HR
        sleep_quality = max(30, min(100, int(sleep_quality_base + random.gauss(0, 10))))
        sleep_duration = int((7.5 + random.gauss(0, 1)) * 60)  # 7.5 hours avg
        strain = max(5, min(21, strain_base + random.gauss(0, 2)))

        # Occasional rest days (every 7-10 days)
        if i % random.randint(7, 10) == 0:
            strain = random.uniform(3, 8)  # Very low strain on rest days

        # Sleep issues during burnout
        if phase == 2:
            # More variable sleep
            sleep_duration = int((6.5 + random.gauss(0, 1.5)) * 60)
            # Occasional insomnia nights
            if random.random() < 0.2:
                sleep_duration = int((5 + random.gauss(0, 0.5)) * 60)
                sleep_quality = random.randint(30, 50)

        data.append({
            "date": current_date,
            "recovery_score": recovery,
            "resting_hr": resting_hr,
            "hrv": hrv,
            "sleep_duration_minutes": sleep_duration,
            "sleep_quality_score": sleep_quality,
            "sleep_latency_minutes": random.randint(5, 25),
            "time_in_bed_minutes": sleep_duration + random.randint(10, 40),
            "day_strain": strain,
            "workout_count": 1 if strain > 10 else 0,
            "average_hr": int(120 + strain * 3),
            "max_hr": int(160 + strain * 2)
        })

    return data


def generate_realistic_mood_data(days: int = 90) -> list:
    """
    Generate realistic mood ratings correlating with burnout progression
    """
    data = []
    start_date = date.today() - timedelta(days=days)

    for i in range(days):
        current_date = start_date + timedelta(days=i)

        # Calculate mood based on phase
        if i < 30:
            # Healthy phase - generally good mood
            mood_base = 7.5
            variance = 1
        elif i < 60:
            # Declining phase - mood drops
            progress = (i - 30) / 30
            mood_base = 7.5 - (progress * 2.5)  # 7.5 -> 5
            variance = 1.5
        else:
            # Burnout phase - low mood with high variance
            mood_base = 4.5
            variance = 2

        mood = max(1, min(10, int(mood_base + random.gauss(0, variance))))

        # Generate notes based on mood
        notes_options = {
            range(1, 4): [
                "Feeling exhausted and overwhelmed",
                "Very low energy today",
                "Struggling to focus",
                "Just want to rest",
                "Feeling burnt out"
            ],
            range(4, 7): [
                "Okay day, nothing special",
                "A bit tired but managing",
                "Feeling meh",
                "Could be better",
                "Getting through the day"
            ],
            range(7, 11): [
                "Feeling good today!",
                "Great energy and motivation",
                "Really productive day",
                "Feeling strong",
                "Good workout, feeling energized"
            ]
        }

        notes = ""
        for mood_range, options in notes_options.items():
            if mood in mood_range:
                # 50% chance of adding notes
                if random.random() < 0.5:
                    notes = random.choice(options)
                break

        data.append({
            "date": current_date,
            "rating": mood,
            "notes": notes
        })

    return data


async def create_supabase_user(email: str, password: str):
    """Create user via Supabase Auth Admin API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/admin/users",
            headers={
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "apikey": SUPABASE_SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json={
                "email": email,
                "password": password,
                "email_confirm": True  # Auto-confirm email
            }
        )

        if response.status_code in [200, 201]:
            data = response.json()
            return data["id"]
        else:
            print(f"❌ Supabase user creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None


async def create_dummy_account():
    """Create dummy user and populate with data"""
    print("🚀 Creating dummy account with realistic data...")

    dummy_email = "demo@respire.app"
    dummy_password = "Demo123!"

    # Create user in Supabase Auth
    print(f"\n📝 Creating Supabase Auth user: {dummy_email}")
    dummy_user_id = await create_supabase_user(dummy_email, dummy_password)

    if not dummy_user_id:
        print("❌ Failed to create user. Exiting.")
        return

    print(f"   ✅ User created with ID: {dummy_user_id}")
    print(f"   🔑 Password: {dummy_password}")

    # Create engine and session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:

            # Generate data
            print("\n📊 Generating 90 days of data...")
            health_data = generate_realistic_whoop_data(90)
            mood_data = generate_realistic_mood_data(90)

            print(f"   Health metrics: {len(health_data)} records")
            print(f"   Mood ratings: {len(mood_data)} records")

            # Insert health metrics
            print("\n💾 Inserting health metrics...")
            for metric_data in health_data:
                metric = HealthMetric(
                    user_id=dummy_user_id,
                    **metric_data
                )
                session.add(metric)

            # Insert mood ratings
            print("💾 Inserting mood ratings...")
            for mood_item in mood_data:
                mood = MoodRating(
                    user_id=dummy_user_id,
                    **mood_item
                )
                session.add(mood)

            # Commit all data
            print("\n⏳ Committing to database...")
            await session.commit()

            print("\n✅ SUCCESS! Dummy account created with:")
            print(f"   📧 Email: {dummy_email}")
            print(f"   🔑 Password: Demo123!")
            print(f"   📊 {len(health_data)} health metrics")
            print(f"   😊 {len(mood_data)} mood ratings")
            print(f"   📅 Date range: {health_data[0]['date']} to {health_data[-1]['date']}")
            print("\n🎯 Data shows gradual burnout progression:")
            print("   Days 0-30: Healthy baseline")
            print("   Days 31-60: Declining recovery and mood")
            print("   Days 61-90: Burnout symptoms")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Respire - Dummy Data Generator")
    print("=" * 60)
    asyncio.run(create_dummy_account())
