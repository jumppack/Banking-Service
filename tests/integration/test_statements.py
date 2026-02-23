import pytest

@pytest.mark.asyncio
async def test_get_statement(client):
    await client.post("/auth/signup", json={"email": "stmt_user@test.com", "password": "pw"})
    login_res = await client.post("/auth/login", data={"username": "stmt_user@test.com", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    acc_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc_id = acc_res.json()["id"]

    stmt_res = await client.get(f"/accounts/{acc_id}/statement/", headers=headers)
    assert stmt_res.status_code == 200
    stmt_data = stmt_res.json()
    assert stmt_data["account_id"] == acc_id
    assert "starting_balance" in stmt_data
    assert stmt_data["transaction_count"] == 0
