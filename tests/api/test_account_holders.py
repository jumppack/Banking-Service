import pytest

@pytest.mark.asyncio
async def test_get_me_requires_auth(client):
    res = await client.get("/account-holders/me")
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_get_me_success(client):
    # Signup + login
    await client.post("/auth/signup", json={"email": "acc_holder1@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "acc_holder1@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    res = await client.get("/account-holders/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "acc_holder1@test.com"
    assert data["is_active"] is True
    assert "id" in data

@pytest.mark.asyncio
async def test_patch_me_update_email_success(client):
    # Signup + login
    await client.post("/auth/signup", json={"email": "acc_holder2@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "acc_holder2@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Patch email
    patch_res = await client.patch(
        "/account-holders/me",
        headers=headers,
        json={"email": "acc_holder2_new@test.com"}
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["email"] == "acc_holder2_new@test.com"
    
    # Verify old login fails
    old_login_res = await client.post("/auth/login", data={"username": "acc_holder2@test.com", "password": "securepw"})
    assert old_login_res.status_code == 401
    
    # Verify new login succeeds
    new_login_res = await client.post("/auth/login", data={"username": "acc_holder2_new@test.com", "password": "securepw"})
    assert "access_token" in new_login_res.json()

@pytest.mark.asyncio
async def test_patch_me_duplicate_email_fails(client):
    # Signup user A and user B
    await client.post("/auth/signup", json={"email": "userA@test.com", "password": "securepw"})
    await client.post("/auth/signup", json={"email": "userB@test.com", "password": "securepw"})
    
    # Login as User A
    login_res = await client.post("/auth/login", data={"username": "userA@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Patch User A email to User B's email
    patch_res = await client.patch(
        "/account-holders/me",
        headers=headers,
        json={"email": "userB@test.com"}
    )
    assert patch_res.status_code == 400
    assert patch_res.json()["detail"] == "User with this email already exists"

@pytest.mark.asyncio
async def test_patch_me_invalid_email_422(client):
    # Signup + login
    await client.post("/auth/signup", json={"email": "acc_holder3@test.com", "password": "securepw"})
    login_res = await client.post("/auth/login", data={"username": "acc_holder3@test.com", "password": "securepw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Patch with invalid email
    patch_res = await client.patch(
        "/account-holders/me",
        headers=headers,
        json={"email": "not-an-email"}
    )
    assert patch_res.status_code == 422
