from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    secret_key: str
    allowed_origins: str = "http://localhost:3000"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # Database
    database_url: str
    database_sync_url: str

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Claude AI
    anthropic_api_key: str = ""

    # Vimeo
    vimeo_access_token: str = ""
    vimeo_allowed_domain: str = "moadon-hasportaim.co.il"

    # Payments
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    tranzila_terminal: str = ""
    payme_seller_id: str = ""

    # Notifications
    fcm_server_key: str = ""
    sendgrid_api_key: str = ""
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""

    # Storage (R2)
    r2_account_id: str = ""
    r2_access_key: str = ""
    r2_secret_key: str = ""
    r2_bucket: str = "moadon-media"
    r2_public_url: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
