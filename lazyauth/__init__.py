"""
LazyAuth - Simple OAuth2 Authentication System
"""

from .auth import router as auth_router
from .config import settings
from .models import User, Token

__version__ = "0.1.0"
__all__ = ["auth_router", "settings", "User", "Token"]
