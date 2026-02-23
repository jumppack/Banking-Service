import pytest

@pytest.mark.asyncio
async def test_signup_and_login(client):
    # Test Signup
    response = await client.post(
        "/auth/signup",
        json={"email": "newuser@test.com", "password": "securepassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@test.com"

    # Test Login
    login_response = await client.post(
        "/auth/login",
        data={"username": "newuser@test.com", "password": "securepassword"}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    # Setup user
    await client.post(
        "/auth/signup",
        json={"email": "wrongpass@test.com", "password": "securepassword"}
    )
    
    # Attempt bad login
    login_response = await client.post(
        "/auth/login",
        data={"username": "wrongpass@test.com", "password": "badpassword"}
    )
    assert login_response.status_code == 401

@pytest.mark.asyncio
async def test_access_with_invalid_jwt(client):
    headers = {"Authorization": "Bearer invalid.token.value"}
    import uuid
    random_id = uuid.uuid4()
    # Try fetching a protected route
    response = await client.get(f"/accounts/{random_id}", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.asyncio
async def test_access_with_expired_jwt(client):
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.core.security import SECRET_KEY, ALGORITHM
    
    # Create an artificially expired token
    expire = datetime.now(timezone.utc) - timedelta(minutes=15)
    to_encode = {"sub": "expired_user", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    headers = {"Authorization": f"Bearer {encoded_jwt}"}
    import uuid
    random_id = uuid.uuid4()
    response = await client.get(f"/accounts/{random_id}", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
