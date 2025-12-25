from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EvaraTDS Platform"
    API_V1_STR: str = "/api/v1"

    # ThingSpeak Configuration
    THINGSPEAK_CHANNEL_ID: str = "2713286"
    THINGSPEAK_READ_KEY: str = ""

    # Alert Thresholds
    TDS_ALERT_THRESHOLD: float = 150.0
    TEMP_ALERT_THRESHOLD: float = 35.0

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = ""

    # Alert System Settings
    ALERT_COOLDOWN_MINUTES: int = 15
    DATABASE_URL: str = "sqlite:///./alerts.db"

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:5173,https://your-app.vercel.app"

    class Config:
        env_file = ".env"


settings = Settings()

