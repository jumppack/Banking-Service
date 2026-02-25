import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_request_id_generated_if_missing(client):
    res = await client.get("/live")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers
    assert len(res.headers["X-Request-ID"]) > 0

@pytest.mark.asyncio
async def test_request_id_preserved_if_provided(client):
    custom_id = "my-custom-request-id-123"
    res = await client.get("/live", headers={"X-Request-ID": custom_id})
    assert res.status_code == 200
    assert res.headers.get("X-Request-ID") == custom_id

@pytest.mark.asyncio
async def test_error_id_returned_on_500():
    from app.main import app
    from fastapi.testclient import TestClient
    
    # Inject a temporary route that purposefully crashes
    @app.get("/test-crash-internal-500")
    async def crash_route_internal():
        raise RuntimeError("Simulated failure")
        
    # TestClient raises server exceptions by default. Set raise_server_exceptions=False 
    # to allow the application's exception handlers to execute and return the 500 response.
    with TestClient(app, raise_server_exceptions=False) as safe_client:
        res = safe_client.get("/test-crash-internal-500")
        
        # We expect our global exception handler to catch this and return a 500
        assert res.status_code == 500
        data = res.json()
        
        assert data["detail"] == "Internal Server Error"
        assert "error_id" in data
        assert "request_id" in data
        assert len(data["error_id"]) > 0
        
        # Ensure the response header also contains the request_id
        assert res.headers.get("X-Request-ID") == data["request_id"]
