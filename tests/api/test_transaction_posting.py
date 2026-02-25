import pytest
import uuid

@pytest.mark.asyncio
async def test_deposit_success_updates_balance_and_creates_tx(client):
    # signup/login
    await client.post("/auth/signup", json={"email": "dep@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "dep@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create account
    acc_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc_id = acc_res.json()["id"]

    # POST deposit 500
    dep_res = await client.post(f"/accounts/{acc_id}/transactions/deposit", headers=headers, json={"amount": 500})
    assert dep_res.status_code == 200
    dep_data = dep_res.json()
    assert dep_data["balance"] == 500
    assert dep_data["transaction"]["amount"] == 500
    assert dep_data["transaction"]["type"] == "deposit"

    # GET /accounts/{id} -> balance == 500
    acc_get = await client.get(f"/accounts/{acc_id}", headers=headers)
    assert acc_get.json()["balance"] == 500

    # GET /accounts/{id}/transactions/ -> contains one tx with amount 500 and type "deposit"
    tx_get = await client.get(f"/accounts/{acc_id}/transactions/", headers=headers)
    tx_list = tx_get.json()
    assert len(tx_list) == 1
    assert tx_list[0]["amount"] == 500
    assert tx_list[0]["type"] == "deposit"

@pytest.mark.asyncio
async def test_withdraw_success_updates_balance_and_creates_tx(client):
    await client.post("/auth/signup", json={"email": "withd@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "withd@test.com", "password": "securepw"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    acc_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc_id = acc_res.json()["id"]

    # deposit first
    await client.post(f"/accounts/{acc_id}/transactions/deposit", headers=headers, json={"amount": 1000})

    # then withdraw
    withd_res = await client.post(f"/accounts/{acc_id}/transactions/withdraw", headers=headers, json={"amount": 400})
    assert withd_res.status_code == 200
    withd_data = withd_res.json()
    assert withd_data["balance"] == 600
    assert withd_data["transaction"]["amount"] == -400
    assert withd_data["transaction"]["type"] == "withdrawal"

    # final balance correct
    acc_get = await client.get(f"/accounts/{acc_id}", headers=headers)
    assert acc_get.json()["balance"] == 600

    # tx list includes withdrawal with negative amount
    tx_get = await client.get(f"/accounts/{acc_id}/transactions/", headers=headers)
    tx_list = tx_get.json()
    assert len(tx_list) == 2
    types = [tx["type"] for tx in tx_list]
    assert "withdrawal" in types
    
    withd_tx = next(tx for tx in tx_list if tx["type"] == "withdrawal")
    assert withd_tx["amount"] == -400

@pytest.mark.asyncio
async def test_withdraw_insufficient_funds_400(client):
    await client.post("/auth/signup", json={"email": "poor@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "poor@test.com", "password": "securepw"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    acc_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc_id = acc_res.json()["id"]

    # withdraw from 0 balance
    withd_res = await client.post(f"/accounts/{acc_id}/transactions/withdraw", headers=headers, json={"amount": 100})
    assert withd_res.status_code == 400
    assert "Insufficient Funds" in withd_res.json()["detail"]

@pytest.mark.asyncio
async def test_post_tx_unauthorized_403(client):
    # user A
    await client.post("/auth/signup", json={"email": "userAa@test.com", "password": "securepw"})
    login_A = await client.post("/auth/login", data={"username": "userAa@test.com", "password": "securepw"})
    headers_A = {"Authorization": f"Bearer {login_A.json()['access_token']}"}

    acc_res = await client.post("/accounts/", headers=headers_A, params={"currency": "USD"})
    acc_id_A = acc_res.json()["id"]

    # user B
    await client.post("/auth/signup", json={"email": "userBb@test.com", "password": "securepw"})
    login_B = await client.post("/auth/login", data={"username": "userBb@test.com", "password": "securepw"})
    headers_B = {"Authorization": f"Bearer {login_B.json()['access_token']}"}

    # B attempts deposit on A's account
    dep_res = await client.post(f"/accounts/{acc_id_A}/transactions/deposit", headers=headers_B, json={"amount": 100})
    assert dep_res.status_code == 403
    assert "Not authorized" in dep_res.json()["detail"]

    # B attempts withdraw on A's account
    withd_res = await client.post(f"/accounts/{acc_id_A}/transactions/withdraw", headers=headers_B, json={"amount": 100})
    assert withd_res.status_code == 403
    assert "Not authorized" in withd_res.json()["detail"]

@pytest.mark.asyncio
async def test_post_tx_requires_auth_401(client):
    random_id = str(uuid.uuid4())
    dep_res = await client.post(f"/accounts/{random_id}/transactions/deposit", json={"amount": 100})
    assert dep_res.status_code == 401

    withd_res = await client.post(f"/accounts/{random_id}/transactions/withdraw", json={"amount": 100})
    assert withd_res.status_code == 401
