import pytest

@pytest.mark.asyncio
async def test_create_and_get_cards(client):
    await client.post("/auth/signup", json={"email": "card_user@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "card_user@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    acc_res = await client.post("/accounts/", headers=headers, params={"currency": "USD"})
    acc_id = acc_res.json()["id"]

    card_res = await client.post("/cards/", headers=headers, json={"account_id": acc_id})
    assert card_res.status_code == 201
    assert "card_number" in card_res.json()

    get_cards_res = await client.get("/cards/", headers=headers)
    assert get_cards_res.status_code == 200
    assert len(get_cards_res.json()) > 0
    assert get_cards_res.json()[0]["account_id"] == acc_id

@pytest.mark.asyncio
async def test_create_card_invalid_account(client):
    await client.post("/auth/signup", json={"email": "card_fail@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "card_fail@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    import uuid
    card_res = await client.post("/cards/", headers=headers, json={"account_id": str(uuid.uuid4())})
    assert card_res.status_code == 404
