"""
Example FastAPI application using LazyAuth
"""

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse

from lazyauth import auth_router, settings
from lazyauth.auth import get_current_user
from lazyauth.models import User

app = FastAPI(
    title="LazyAuth Example",
    description="Simple OAuth2 Authentication System",
    version="0.1.0"
)

# Include authentication routes
app.include_router(auth_router)


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with login button"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LazyAuth - Simple OAuth2 Authentication</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 5px;
                cursor: pointer;
                border: none;
                font-size: 16px;
            }
            .btn:hover {
                background-color: #45a049;
            }
            .btn-secondary {
                background-color: #008CBA;
            }
            .btn-secondary:hover {
                background-color: #007399;
            }
            .info {
                background-color: #e7f3fe;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
            }
            .user-info {
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 20px 0;
            }
            pre {
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 LazyAuth - Simple OAuth2 Authentication</h1>
            
            <div class="info">
                <h3>Welcome to LazyAuth!</h3>
                <p>This is a simple authentication system using OAuth2 with provider ID.</p>
                <p>No database required - user data comes directly from the OAuth2 provider API.</p>
            </div>
            
            <div id="auth-section">
                <h2>Authentication</h2>
                <button class="btn" onclick="login()">🚀 Login with OAuth2</button>
                <button class="btn btn-secondary" onclick="checkStatus()">📊 Check Status</button>
                <button class="btn" onclick="logout()" style="background-color: #f44336;">🚪 Logout</button>
            </div>
            
            <div id="status-section" style="display: none;">
                <h2>Status</h2>
                <div id="status-content"></div>
            </div>
            
            <div class="info">
                <h3>📚 API Endpoints:</h3>
                <ul>
                    <li><strong>GET /auth/login</strong> - Initiate OAuth2 login flow</li>
                    <li><strong>GET /auth/callback</strong> - OAuth2 callback handler</li>
                    <li><strong>GET /auth/me</strong> - Get current user profile (protected)</li>
                    <li><strong>GET /auth/status</strong> - Check authentication status</li>
                    <li><strong>POST /auth/logout</strong> - Logout</li>
                    <li><strong>GET /protected</strong> - Example protected endpoint</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>🛠️ Setup Instructions:</h3>
                <ol>
                    <li>Copy <code>.env.example</code> to <code>.env</code></li>
                    <li>Configure your OAuth2 provider credentials</li>
                    <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
                    <li>Run the application: <code>python main.py</code></li>
                </ol>
            </div>
        </div>
        
        <script>
            async function login() {
                try {
                    const response = await fetch('/auth/login');
                    const data = await response.json();
                    if (data.authorization_url) {
                        // In a real application, redirect to the authorization URL
                        alert('Authorization URL: ' + data.authorization_url + '\\n\\nNote: Configure your OAuth2 provider first in .env file');
                        // window.location.href = data.authorization_url;
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function checkStatus() {
                try {
                    const response = await fetch('/auth/status');
                    const data = await response.json();
                    const statusDiv = document.getElementById('status-content');
                    
                    if (data.authenticated) {
                        statusDiv.innerHTML = `
                            <div class="user-info">
                                <h3>✅ Authenticated</h3>
                                <pre>${JSON.stringify(data.user, null, 2)}</pre>
                            </div>
                        `;
                    } else {
                        statusDiv.innerHTML = `
                            <div class="info">
                                <h3>❌ Not Authenticated</h3>
                                <p>Please login to access protected resources.</p>
                            </div>
                        `;
                    }
                    
                    document.getElementById('status-section').style.display = 'block';
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
            
            async function logout() {
                try {
                    const response = await fetch('/auth/logout', {
                        method: 'POST'
                    });
                    const data = await response.json();
                    alert(data.message);
                    document.getElementById('status-section').style.display = 'none';
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route that requires authentication"""
    return {
        "message": "This is a protected resource",
        "user": current_user,
        "access_granted": True
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "lazyauth",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port
    )
