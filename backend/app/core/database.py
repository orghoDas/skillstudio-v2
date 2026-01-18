from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from typing import AsyncGenerator, Optional
import redis as redis_sync


# ============================================
# PostgreSQL (Neon) Configuration
# ============================================

# Create async engine for Neon
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before using
    pool_size=5,          # Optimized for serverless
    max_overflow=10,
    pool_recycle=300,     # Recycle connections every 5 minutes
    connect_args={
        "server_settings": {
            "application_name": "learning_platform",
            "jit": "off"  # Faster for serverless workloads
        }
    }
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


# ============================================
# Redis Configuration
# ============================================

_redis_client: Optional[redis_sync.Redis] = None


def get_redis() -> redis_sync.Redis:
    """
    Get Redis client (supports both local Redis and Upstash)
    """
    global _redis_client
    
    if _redis_client is None:
        if settings.REDIS_URL.startswith(('redis://', 'rediss://')):
            # Standard Redis connection
            _redis_client = redis_sync.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        else:
            # Upstash REST API
            from upstash_redis import Redis
            _redis_client = Redis(
                url=settings.REDIS_URL,
                token=settings.UPSTASH_REDIS_REST_TOKEN
            )
    
    return _redis_client


# ============================================
# Database Dependencies for FastAPI
# ============================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database session
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ============================================
# Utility Functions
# ============================================

async def init_db():
    """
    Initialize database - create all tables
    (Use Alembic for production)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections gracefully
    """
    await engine.dispose()