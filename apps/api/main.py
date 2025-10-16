"""
Respire API - FastAPI Backend
Production-ready health analytics platform
"""
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from app.database import init_db, close_db, engine
from app.routers import whoop, auth, mood, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    print("🚀 Starting Respire API...")
    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")

    yield

    # Shutdown
    print("🛑 Shutting down Respire API...")
    await close_db()
    print("✅ Database connections closed")


app = FastAPI(
    title="Respire API",
    description="AI-powered burnout prevention platform using WHOOP data",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "https://*.vercel.app",
        "https://tryrespire.ai",
        "https://app.tryrespire.ai",
        "https://www.tryrespire.ai",
        # Legacy domains (if needed during migration)
        "https://www.respire.cloud",
        "https://respire.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(whoop.router)
app.include_router(mood.router)
app.include_router(health.router)

# Mount static files for uploads
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Respire API",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Fast health check for Railway monitoring"""
    # Simple check - just return OK if API is responding
    # Railway health checks happen frequently, so we don't test DB every time
    return {
        "status": "healthy",
        "checks": {
            "api": "ok",
        }
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with database connection test"""
    db_status = "ok"
    try:
        # Test database connection
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "checks": {
            "api": "ok",
            "database": db_status,
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)