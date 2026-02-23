import pytest

@pytest.mark.asyncio
async def test_get_transactions(client):
    await client.post("/auth/signup", json={"email": "tx_user@test.com", "password": "pw"})
    login_res = await client.post("/auth/login", data={"username": "tx_user@test.com", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    acc1_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc1_id = acc1_res.json()["id"]

    # Verify transactions list is empty initially
    tx_res = await client.get(f"/accounts/{acc1_id}/transactions/", headers=headers)
    assert tx_res.status_code == 200
    assert isinstance(tx_res.json(), list)
    assert len(tx_res.json()) == 0

@pytest.mark.asyncio
async def test_get_transactions_absurd_limit(client):
    await client.post("/auth/signup", json={"email": "tx_limit@test.com", "password": "pw"})
    login_res = await client.post("/auth/login", data={"username": "tx_limit@test.com", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    acc1_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc1_id = acc1_res.json()["id"]

    # Send limit of 1000000
    tx_res = await client.get(f"/accounts/{acc1_id}/transactions/", headers=headers, params={"limit": 1000000})
    assert tx_res.status_code == 200
    assert isinstance(tx_res.json(), list)

@pytest.mark.asyncio
async def test_get_transactions_unauthorized(client):
    await client.post("/auth/signup", json={"email": "tx_fail@test.com", "password": "pw"})
    login_res = await client.post("/auth/login", data={"username": "tx_fail@test.com", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    import uuid
    tx_res = await client.get(f"/accounts/{uuid.uuid4()}/transactions/", headers=headers)
    assert tx_res.status_code == 404
