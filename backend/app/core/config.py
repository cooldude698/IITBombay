"""
VERIACT — Application Configuration & Environment Settings
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VERIACT"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # HMAC Cryptographic Key for Execution Tokens (30s TTL)
    HMAC_SECRET_KEY: str = os.getenv("HMAC_SECRET_KEY", "veriact_hmac_secret_2026_super_secure_key")
    EXECUTION_TOKEN_TTL_SECONDS: int = 30
    
    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///veriact_enterprise.db")
    
    # Verification Latency Timeouts (ms)
    FAST_TIER_TIMEOUT_MS: int = 200
    STRONG_TIER_TIMEOUT_MS: int = 1000
    DEEP_TIER_TIMEOUT_MS: int = 2500
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
