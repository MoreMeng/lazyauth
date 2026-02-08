"""
Configuration settings for LazyAuth
"""

import os
import warnings
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # OAuth2 Provider Configuration
    oauth2_client_id: str = os.getenv("OAUTH2_CLIENT_ID", "")
    oauth2_client_secret: str = os.getenv("OAUTH2_CLIENT_SECRET", "")
    oauth2_authorization_url: str = os.getenv("OAUTH2_AUTHORIZATION_URL", "")
    oauth2_token_url: str = os.getenv("OAUTH2_TOKEN_URL", "")
    oauth2_user_info_url: str = os.getenv("OAUTH2_USER_INFO_URL", "")
    oauth2_redirect_uri: str = os.getenv("OAUTH2_REDIRECT_URI", "http://localhost:8000/auth/callback")
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "default-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))
    
    # Application Configuration
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    
    class Config:
        env_file = ".env"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Warn if using default secret key
        if self.jwt_secret_key == "default-secret-key-change-in-production":
            warnings.warn(
                "Using default JWT secret key! This is insecure for production. "
                "Please set JWT_SECRET_KEY in your .env file.",
                UserWarning,
                stacklevel=2
            )


settings = Settings()
