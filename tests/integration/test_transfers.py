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
        "to_account_id": acc1_id,
        "amount": 500
    })
    
    assert transfer_res.status_code == 403
    assert transfer_res.json()["detail"] == "Not authorized to transfer from this account"
