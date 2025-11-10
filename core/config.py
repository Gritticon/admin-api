"""
Application Configuration
Centralized configuration management using environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    DB_USERNAME: str = "admin"
    DB_PASSWORD: str = "sy7LADkeGFtBxy8"
    DB_HOST: str = "shopos-db.cj8uqe0gmqvq.ap-south-1.rds.amazonaws.com"
    APP_DATABASE: str = "pos"
    ADMIN_DATABASE: str = "posAdmin"
    
    # Application Configuration
    APP_NAME: str = "Admin Server API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Update Service Configuration
    UPDATE_SERVICE_URL: str = "https://updates.gritticon.com/api/update/send_update"
    
    # CORS Configuration (comma-separated string, will be split)
    CORS_ORIGINS: str = "*"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    def get_cors_origins(self) -> list:
        """Split CORS origins string into list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def app_database_url(self) -> str:
        """Construct application database connection URL."""
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.APP_DATABASE}"
    
    @property
    def admin_database_url(self) -> str:
        """Construct admin database connection URL."""
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.ADMIN_DATABASE}"


# Global settings instance
settings = Settings()

