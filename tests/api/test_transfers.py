import pytest

@pytest.mark.asyncio
async def test_transfer_endpoint(client):
    # Step 1: Create User 1 & Account
    await client.post("/auth/signup", json={"email": "user1@test.com", "password": "pw"})
    login1 = await client.post("/auth/login", data={"username": "user1@test.com", "password": "pw"})
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    acc1_res = await client.post("/accounts/", headers=headers1, params={"currency": "USD"})
    acc1_id = acc1_res.json()["id"]

    # Step 2: Create User 2 & Account
    await client.post("/auth/signup", json={"email": "user2@test.com", "password": "pw"})
    login2 = await client.post("/auth/login", data={"username": "user2@test.com", "password": "pw"})
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    acc2_res = await client.post("/accounts/", headers=headers2, params={"currency": "USD"})
    acc2_id = acc2_res.json()["id"]

    # Step 3: Hack - Attempt to perform transfer AS User 1, but FROM User 2's account (IDOR Testing)
    transfer_res = await client.post("/transfers/", headers=headers1, json={
        "from_account_id": acc2_id,
        "to_identifier": "user1@test.com",
        "amount": 500
    })
    
    assert transfer_res.status_code == 403
    assert transfer_res.json()["detail"] == "Not authorized to transfer from this account"

@pytest.mark.asyncio
async def test_transfer_unauthenticated(client):
    """
    Test 401 Unauthorized rejection when attempting a transfer without a Bearer token.
    (Negative/False Negative Test)
    """
    transfer_res = await client.post("/transfers/", json={
        "from_account_id": "00000000-0000-0000-0000-000000000000",
        "to_identifier": "nobody@test.com",
        "amount": 500
    })
    
    assert transfer_res.status_code == 401
    assert transfer_res.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_transfer_invalid_email(client):
    """
    Test 404 Not Found rejection when targeting a non-existent counterparty email.
    (Boundary/Negative Test)
    """
    # Create valid user 1
    await client.post("/auth/signup", json={"email": "valid1@test.com", "password": "pw"})
    login1 = await client.post("/auth/login", data={"username": "valid1@test.com", "password": "pw"})
    headers = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    acc_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    
    transfer_res = await client.post("/transfers/", headers=headers, json={
        "from_account_id": acc_res.json()["id"],
        "to_identifier": "this_email_does_not_exist@vacuum.com",
        "amount": 500
    })
    
    assert transfer_res.status_code == 404
    assert "Destination user not found" in transfer_res.json()["detail"]

@pytest.mark.asyncio
async def test_transfer_insufficient_funds_integration(client):
    """
    Test 400 Bad Request (Overdraft Protection) preventing transferring more than available.
    Ensures the business logic exception violently bubbles up through the router cleanly.
    """
    await client.post("/auth/signup", json={"email": "poor_user@test.com", "password": "pw"})
    login1 = await client.post("/auth/login", data={"username": "poor_user@test.com", "password": "pw"})
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    acc1_res = await client.post("/accounts/", headers=headers1, params={"currency": "USD"})

    await client.post("/auth/signup", json={"email": "receiver@test.com", "password": "pw"})
    login2 = await client.post("/auth/login", data={"username": "receiver@test.com", "password": "pw"})
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    await client.post("/accounts/", headers=headers2, params={"currency": "USD"})
    
    # Attempt to transfer $5.00 but starting balance is $0.00
    transfer_res = await client.post("/transfers/", headers=headers1, json={
        "from_account_id": acc1_res.json()["id"],
        "to_identifier": "receiver@test.com",
        "amount": 500
    })
    
    assert transfer_res.status_code == 400
    assert "Insufficient Funds" in transfer_res.json()["detail"]
