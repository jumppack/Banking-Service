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
