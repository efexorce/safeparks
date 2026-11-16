from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeParks - Akıllı Park Güvenlik Sistemi"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "safeparks"
    POSTGRES_PASSWORD: str = "safeparks_secure_pass"
    POSTGRES_DB: str = "safeparks"
    DATABASE_URL: Optional[str] = None

    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    MAX_CAMERAS: int = 10000
    DEFAULT_RETENTION_DAYS: int = 15

    HIGH_QUALITY_BITRATE_MBPS: float = 3.0
    LOW_QUALITY_BITRATE_MBPS: float = 0.8
    HIGH_QUALITY_FPS: int = 25
    LOW_QUALITY_FPS: int = 5
    AI_ANALYSIS_FPS: int = 5
    HIGH_QUALITY_RESOLUTION: str = "1080p"
    LOW_QUALITY_RESOLUTION: str = "480p"

    DAILY_DATA_LIMIT_GB: float = 13.5
    MONTHLY_DATA_LIMIT_GB: float = 400.0

    ALERT_MAX_LATENCY_SECONDS: float = 2.0
    ENERGY_SAVE_THRESHOLD_PERCENT: float = 40.0

    SOLAR_DAYTIME_RATIO: float = 0.70

    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ALERT_EMAIL_RECIPIENTS: str = ""

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )


settings = Settings()
