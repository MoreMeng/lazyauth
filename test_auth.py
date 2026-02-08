"""
Simple tests for LazyAuth authentication system
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "lazyauth"
    print("✅ Health check test passed")


def test_home_page():
    """Test home page loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert "LazyAuth" in response.text
    print("✅ Home page test passed")


def test_login_endpoint():
    """Test login endpoint returns authorization URL"""
    response = client.get("/auth/login")
    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "state" in data
    assert "message" in data
    print("✅ Login endpoint test passed")


def test_auth_status_not_authenticated():
    """Test auth status when not authenticated"""
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False
    assert data["user"] is None
    print("✅ Auth status (not authenticated) test passed")


def test_protected_route_requires_auth():
    """Test that protected routes require authentication"""
    response = client.get("/protected")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    print("✅ Protected route authorization test passed")


def test_me_endpoint_requires_auth():
    """Test that /auth/me requires authentication"""
    response = client.get("/auth/me")
    assert response.status_code == 401
    print("✅ Me endpoint authorization test passed")


def test_logout_endpoint():
    """Test logout endpoint"""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    print("✅ Logout endpoint test passed")


if __name__ == "__main__":
    print("Running LazyAuth Tests...\n")
    
    test_health_check()
    test_home_page()
    test_login_endpoint()
    test_auth_status_not_authenticated()
    test_protected_route_requires_auth()
    test_me_endpoint_requires_auth()
    test_logout_endpoint()
    
    print("\n✅ All tests passed!")
