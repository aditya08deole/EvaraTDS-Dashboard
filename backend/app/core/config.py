from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "EvaraTDS Platform"
    API_V1_STR: str = "/api/v1"

    # ThingSpeak Configuration
    THINGSPEAK_CHANNEL_ID: str = "2713286"
    # ThingSpeak Read API Key (public channels - safe to share)
    THINGSPEAK_READ_KEY: str = "EHEK3A1XD48TY98B"

    # Alert Thresholds
    TDS_ALERT_THRESHOLD: float = 150.0
    TEMP_ALERT_THRESHOLD: float = 35.0

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALERT_CHAT_ID: str = ""  # Chat ID where alerts are sent
    TELEGRAM_GROUP_INVITE_LINK: str = "https://t.me/+K2URmImZb9tmMDc9"  # Group invite link

    # Alert System Settings
    ALERT_COOLDOWN_MINUTES: int = 15

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:5173,https://your-app.vercel.app"

    class Config:
        env_file = ".env"


settings = Settings()

