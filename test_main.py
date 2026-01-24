import pytest
from httpx import AsyncClient, ASGITransport
import os
# Importing your FastAPI app
from backend.main import app 

@pytest.mark.asyncio
async def test_health_check():

    "Test if the API is reachable using the new ASGITransport"
    # Use ASGITransport for newer versions of httpx
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_model_prediction():

    "Test the core logic of the misinformation detector"
    transport = ASGITransport(app=app)
    test_data = {"text": "This is a sample news for testing purpose."}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Update this path if your endpoint is different (e.g., /predict)
        response = await ac.post("/predict", json=test_data)
    
    assert response.status_code == 200
    assert "label" in response.json()
    assert "confidence" in response.json()

def test_env_vars():
    
    "Verify that essential environment variables are available"
    assert os.getenv("HF_MODEL") is not None