"""
OAuth2 authentication implementation
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from jose import JWTError, jwt

from .config import settings
from .models import User, Token, OAuth2Token

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory session storage (for demo purposes)
# In production, use Redis or similar
# Sessions expire after 10 minutes
sessions: Dict[str, tuple[str, datetime]] = {}


def cleanup_expired_sessions():
    """Remove expired sessions from memory"""
    current_time = datetime.now(timezone.utc)
    expired = [
        state for state, (status, timestamp) in sessions.items()
        if (current_time - timestamp).total_seconds() > 600  # 10 minutes
    ]
    for state in expired:
        del sessions[state]


def create_jwt_token(user: User) -> Token:
    """Create JWT token for authenticated user"""
    expires_delta = timedelta(minutes=settings.jwt_expiration_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "provider": user.provider,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return Token(
        access_token=encoded_jwt,
        token_type="bearer",
        expires_in=settings.jwt_expiration_minutes * 60
    )


def verify_jwt_token(token: str) -> Optional[User]:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        return User(
            id=user_id,
            email=payload.get("email"),
            name=payload.get("name"),
            provider=payload.get("provider", "unknown")
        )
    except JWTError:
        return None


async def get_current_user(request: Request) -> User:
    """Dependency to get current authenticated user"""
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        user = verify_jwt_token(token)
        if user:
            return user
    
    # Check cookie
    token = request.cookies.get("access_token")
    if token:
        user = verify_jwt_token(token)
        if user:
            return user
    
    raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("/login")
async def login():
    """Initiate OAuth2 login flow"""
    # Clean up expired sessions
    cleanup_expired_sessions()
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    sessions[state] = ("pending", datetime.now(timezone.utc))
    
    # Build authorization URL
    params = {
        "client_id": settings.oauth2_client_id,
        "redirect_uri": settings.oauth2_redirect_uri,
        "response_type": "code",
        "state": state,
        "scope": "openid profile email"
    }
    
    auth_url = f"{settings.oauth2_authorization_url}?{urlencode(params)}"
    
    return {
        "authorization_url": auth_url,
        "state": state,
        "message": "Redirect user to authorization_url to complete login"
    }


@router.get("/callback")
async def auth_callback(code: str, state: str, response: Response):
    """Handle OAuth2 callback"""
    # Verify state to prevent CSRF
    if state not in sessions:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del sessions[state]
    
    # Exchange authorization code for access token
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(
                settings.oauth2_token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.oauth2_redirect_uri,
                    "client_id": settings.oauth2_client_id,
                    "client_secret": settings.oauth2_client_secret,
                }
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            oauth_token = OAuth2Token(**token_data)
            
            # Get user info from provider
            user_info_response = await client.get(
                settings.oauth2_user_info_url,
                headers={"Authorization": f"Bearer {oauth_token.access_token}"}
            )
            user_info_response.raise_for_status()
            user_data = user_info_response.json()
            
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to authenticate with provider: {str(e)}"
            )
    
    # Create user object from provider data
    user = User(
        id=user_data.get("id") or user_data.get("sub", "unknown"),
        email=user_data.get("email"),
        name=user_data.get("name") or user_data.get("display_name"),
        provider="oauth2",
        provider_data=user_data
    )
    
    # Create JWT token for our application
    token = create_jwt_token(user)
    
    # Set cookie
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=token.expires_in,
        samesite="lax",
        secure=True  # Only send over HTTPS
    )
    
    return {
        "message": "Authentication successful",
        "user": user,
        "token": token
    }


@router.get("/me")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.post("/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/status")
async def auth_status(request: Request):
    """Check authentication status"""
    try:
        user = await get_current_user(request)
        return {
            "authenticated": True,
            "user": user
        }
    except HTTPException:
        return {
            "authenticated": False,
            "user": None
        }
