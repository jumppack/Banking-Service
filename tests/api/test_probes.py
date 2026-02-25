import pytest

@pytest.mark.asyncio
async def test_liveness_probe(client):
    res = await client.get("/live")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_readiness_probe(client):
    res = await client.get("/ready")
    assert res.status_code == 200
    assert res.json() == {"status": "ready"}

@pytest.mark.asyncio
async def test_health_check_alias(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ready"}
