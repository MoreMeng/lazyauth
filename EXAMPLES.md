# LazyAuth Usage Examples

## Quick Start

### 1. Installation and Setup

```bash
# Clone the repository
git clone https://github.com/MoreMeng/lazyauth.git
cd lazyauth

# Install dependencies
pip install -r requirements.txt

# Configure your OAuth2 provider
cp .env.example .env
# Edit .env with your OAuth2 provider credentials
```

### 2. Running the Example Application

```bash
# Start the server
python main.py
```

The application will be available at `http://localhost:8000`

## Integration Examples

### Example 1: Basic Integration

```python
from fastapi import FastAPI, Depends
from lazyauth import auth_router
from lazyauth.auth import get_current_user
from lazyauth.models import User

app = FastAPI()

# Include authentication routes
app.include_router(auth_router)

# Create a protected endpoint
@app.get("/api/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }
```

### Example 2: Using with Google OAuth2

1. Create OAuth2 credentials at https://console.cloud.google.com/
2. Configure your `.env`:

```env
OAUTH2_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
OAUTH2_CLIENT_SECRET=your-google-client-secret
OAUTH2_AUTHORIZATION_URL=https://accounts.google.com/o/oauth2/v2/auth
OAUTH2_TOKEN_URL=https://oauth2.googleapis.com/token
OAUTH2_USER_INFO_URL=https://www.googleapis.com/oauth2/v2/userinfo
OAUTH2_REDIRECT_URI=http://localhost:8000/auth/callback

JWT_SECRET_KEY=your-random-secret-key-here
```

3. Add authorized redirect URI in Google Console: `http://localhost:8000/auth/callback`

### Example 3: Using with GitHub OAuth2

1. Create OAuth App at https://github.com/settings/developers
2. Configure your `.env`:

```env
OAUTH2_CLIENT_ID=your-github-client-id
OAUTH2_CLIENT_SECRET=your-github-client-secret
OAUTH2_AUTHORIZATION_URL=https://github.com/login/oauth/authorize
OAUTH2_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH2_USER_INFO_URL=https://api.github.com/user
OAUTH2_REDIRECT_URI=http://localhost:8000/auth/callback

JWT_SECRET_KEY=your-random-secret-key-here
```

3. Set callback URL in GitHub OAuth App settings: `http://localhost:8000/auth/callback`

### Example 4: Custom Protected Routes

```python
from fastapi import APIRouter, Depends
from lazyauth.auth import get_current_user
from lazyauth.models import User

router = APIRouter()

@router.get("/admin/users")
async def list_users(current_user: User = Depends(get_current_user)):
    # Only authenticated users can access this endpoint
    return {"message": "Admin users list", "admin": current_user.email}

@router.post("/api/data")
async def create_data(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    # Create data for authenticated user
    return {
        "message": "Data created",
        "user_id": current_user.id,
        "data": data
    }
```

## API Usage Examples

### Using cURL

```bash
# 1. Initiate login flow
curl http://localhost:8000/auth/login

# 2. After authentication, use the JWT token
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/auth/me

# 3. Access protected resources
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/protected

# 4. Check authentication status
curl http://localhost:8000/auth/status \
     --cookie "access_token=YOUR_JWT_TOKEN"

# 5. Logout
curl -X POST http://localhost:8000/auth/logout \
     --cookie "access_token=YOUR_JWT_TOKEN"
```

### Using Python requests

```python
import requests

# 1. Get authorization URL
response = requests.get("http://localhost:8000/auth/login")
auth_data = response.json()
print(f"Go to: {auth_data['authorization_url']}")

# 2. After callback, you'll have a JWT token in cookies
# Use it to make authenticated requests
session = requests.Session()

# 3. Access protected resources
response = session.get(
    "http://localhost:8000/protected",
    headers={"Authorization": f"Bearer {jwt_token}"}
)
print(response.json())

# 4. Get user profile
response = session.get(
    "http://localhost:8000/auth/me",
    headers={"Authorization": f"Bearer {jwt_token}"}
)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
// 1. Check authentication status
fetch('/auth/status')
  .then(response => response.json())
  .then(data => {
    if (data.authenticated) {
      console.log('User:', data.user);
    } else {
      console.log('Not authenticated');
    }
  });

// 2. Initiate login
fetch('/auth/login')
  .then(response => response.json())
  .then(data => {
    // Redirect to OAuth2 provider
    window.location.href = data.authorization_url;
  });

// 3. Access protected resource
fetch('/protected', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
  .then(response => response.json())
  .then(data => console.log(data));

// 4. Logout
fetch('/auth/logout', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => console.log(data.message));
```

## Production Deployment

### Security Checklist

1. **Set strong JWT secret**:
   ```env
   JWT_SECRET_KEY=$(openssl rand -base64 32)
   ```

2. **Use HTTPS in production**:
   - The `secure=True` cookie flag requires HTTPS
   - Update redirect URI to use https://

3. **Configure proper CORS**:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Use production session storage**:
   - Replace in-memory sessions with Redis or similar
   - Implement proper session cleanup

5. **Set proper token expiration**:
   ```env
   JWT_EXPIRATION_MINUTES=15  # Shorter for production
   ```

## Troubleshooting

### Issue: "Using default JWT secret key" warning
**Solution**: Set `JWT_SECRET_KEY` in your `.env` file

### Issue: OAuth2 callback fails
**Solution**: Check that redirect URI matches exactly in both `.env` and OAuth provider settings

### Issue: Cookies not working
**Solution**: In development, you may need to disable `secure=True` flag or use HTTPS

### Issue: User data not retrieved
**Solution**: Verify `OAUTH2_USER_INFO_URL` is correct for your provider and scopes include user data access

## Support

For issues and questions, please open an issue on GitHub: https://github.com/MoreMeng/lazyauth/issues
