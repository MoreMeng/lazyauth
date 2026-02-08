# lazyauth

🔐 **LazyAuth** - Simple OAuth2 Authentication System

A lightweight, easy-to-use authentication system that supports OAuth2 provider login without requiring a database. User data comes directly from the OAuth2 provider API.

## Features

- ✅ OAuth2 authentication flow
- ✅ Provider ID-based login
- ✅ No database required - uses data from provider API
- ✅ JWT token generation for session management
- ✅ Protected route examples
- ✅ Simple integration with FastAPI
- ✅ Ready-to-use example application

## Installation

```bash
# Clone the repository
git clone https://github.com/MoreMeng/lazyauth.git
cd lazyauth

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure your OAuth2 provider:
```env
# OAuth2 Provider Configuration
OAUTH2_CLIENT_ID=your_client_id
OAUTH2_CLIENT_SECRET=your_client_secret
OAUTH2_AUTHORIZATION_URL=https://provider.com/oauth/authorize
OAUTH2_TOKEN_URL=https://provider.com/oauth/token
OAUTH2_USER_INFO_URL=https://provider.com/api/user
OAUTH2_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Common OAuth2 Providers

#### Google
```env
OAUTH2_AUTHORIZATION_URL=https://accounts.google.com/o/oauth2/v2/auth
OAUTH2_TOKEN_URL=https://oauth2.googleapis.com/token
OAUTH2_USER_INFO_URL=https://www.googleapis.com/oauth2/v2/userinfo
```

#### GitHub
```env
OAUTH2_AUTHORIZATION_URL=https://github.com/login/oauth/authorize
OAUTH2_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH2_USER_INFO_URL=https://api.github.com/user
```

#### Microsoft
```env
OAUTH2_AUTHORIZATION_URL=https://login.microsoftonline.com/common/oauth2/v2.0/authorize
OAUTH2_TOKEN_URL=https://login.microsoftonline.com/common/oauth2/v2.0/token
OAUTH2_USER_INFO_URL=https://graph.microsoft.com/v1.0/me
```

## Usage

### Running the Application

```bash
# Run the example application
python main.py
```

The application will start on `http://localhost:8000`

### API Endpoints

- **GET /** - Home page with login interface
- **GET /auth/login** - Initiate OAuth2 login flow
- **GET /auth/callback** - OAuth2 callback handler
- **GET /auth/me** - Get current user profile (protected)
- **GET /auth/status** - Check authentication status
- **POST /auth/logout** - Logout user
- **GET /protected** - Example protected endpoint

### Example Usage in Your Application

```python
from fastapi import FastAPI, Depends
from lazyauth import auth_router
from lazyauth.auth import get_current_user
from lazyauth.models import User

app = FastAPI()

# Include authentication routes
app.include_router(auth_router)

# Create a protected route
@app.get("/api/data")
async def get_data(current_user: User = Depends(get_current_user)):
    return {
        "message": "Protected data",
        "user": current_user
    }
```

### Authentication Flow

1. **User initiates login**: Navigate to `/auth/login`
2. **System generates state**: Creates CSRF protection token
3. **Redirect to provider**: User is redirected to OAuth2 provider
4. **User authorizes**: User grants permission on provider site
5. **Callback received**: Provider redirects back to `/auth/callback`
6. **Exchange code**: System exchanges authorization code for access token
7. **Fetch user data**: System retrieves user info from provider API
8. **Generate JWT**: System creates JWT token for session
9. **User authenticated**: JWT token stored in cookie

### Using the API

#### Check Authentication Status
```bash
curl http://localhost:8000/auth/status
```

#### Access Protected Resource
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/protected
```

## Security Features

- ✅ CSRF protection with state parameter
- ✅ JWT token-based sessions
- ✅ HTTP-only cookies
- ✅ Token expiration
- ✅ Secure token verification

## Development

### Project Structure

```
lazyauth/
├── lazyauth/
│   ├── __init__.py      # Package initialization
│   ├── auth.py          # OAuth2 authentication logic
│   ├── config.py        # Configuration settings
│   └── models.py        # Data models
├── main.py              # Example application
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment configuration
└── README.md           # This file
```

### Testing

You can test the authentication flow using the included web interface or via API calls:

```bash
# Start the server
python main.py

# Open browser
open http://localhost:8000
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Author

MoreMeng

## Acknowledgments

This project implements a simple OAuth2 authentication system based on standard OAuth2 best practices, designed to be easy to integrate and use without requiring database setup.