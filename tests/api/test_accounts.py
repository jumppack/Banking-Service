import pytest

@pytest.mark.asyncio
async def test_create_and_get_account(client):
    # Step 1: Create user
    await client.post("/auth/signup", json={"email": "acc_user@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "acc_user@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create account
    create_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    assert create_res.status_code == 201
    acc_id = create_res.json()["id"]

    # Step 3: Get account
    get_res = await client.get(f"/accounts/{acc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == acc_id

@pytest.mark.asyncio
async def test_get_account_unauthorized(client):
    # Setup poor user
    await client.post("/auth/signup", json={"email": "acc_user2@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "acc_user2@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    import uuid
    random_id = str(uuid.uuid4())
    get_res = await client.get(f"/accounts/{random_id}", headers=headers)
    # Should be 404 since it doesn't exist, if it existed but belonged to someone else it would be 403
    assert get_res.status_code == 404
