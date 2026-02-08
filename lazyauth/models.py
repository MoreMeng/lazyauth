"""
Data models for LazyAuth
"""

from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    """User model from OAuth2 provider"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    provider: str
    provider_data: dict = {}


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class OAuth2Token(BaseModel):
    """OAuth2 token from provider"""
    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
