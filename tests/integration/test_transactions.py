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
