from pydantic import BaseSettings
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Redis Configuration
    REDIS_URL: str
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application
    APP_NAME: str = "Learning Platform"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance to avoid reading .env multiple times
    """
    return Settings()


settings = get_settings()