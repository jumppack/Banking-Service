import pytest
import uuid
from app.services.account_service import AccountService
from unittest.mock import patch

@pytest.mark.asyncio
async def test_account_creation_collision_retry(client, session):
    # Register/Login
    await client.post("/auth/signup", json={"email": "collide@test.com", "password": "securepw"})
    login = await client.post("/auth/login", data={"username": "collide@test.com", "password": "securepw"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # First, test standard creation works
    with patch('app.services.account_service.AccountService._generate_account_number') as mock_gen:
        # Pre-program the mock to return exactly the same string for the first two attempts, 
        # then a new stream of strings.
        collision_number = "COLLIDE123"
        unique_number = "UNIQUE4567"
        
        # When creating the first account, it pulls COLLIDE123
        # When creating the second account, it pulls COLLIDE123 (fails natively), then UNIQUE4567 (succeeds)
        mock_gen.side_effect = [collision_number, collision_number, unique_number]
        
        # Attempt 1 -> Generates "COLLIDE123" -> Succeeds (First item in side_effect)
        res1 = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
        assert res1.status_code == 201
        assert res1.json()["account_number"] == collision_number
        
        # Attempt 2 -> Generates "COLLIDE123" -> Fails Constraint -> Retries -> "UNIQUE4567" -> Succeeds
        res2 = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
        assert res2.status_code == 201
        assert res2.json()["account_number"] == unique_number

    # Verify both accounts exist for the user
    res_list = await client.get("/accounts/me", headers=headers)
    assert len(res_list.json()) == 2
