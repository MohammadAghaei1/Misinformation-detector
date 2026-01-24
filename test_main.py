import pytest
from httpx import AsyncClient
import os
# Import your FastAPI app from the backend folder
from backend.main import app 

@pytest.mark.asyncio
async def test_health_check():
    """Test if the API is reachable and returns a 200 status code"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_model_prediction():
    """Test the core logic: Check if the fake news detection endpoint works"""
    # Adjust the JSON payload based on your actual API structure
    test_data = {"text": "This is a sample news for testing purpose."}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Assuming your endpoint is /predict
        response = await ac.post("/predict", json=test_data)
    
    assert response.status_code == 200
    # Ensure the response contains the expected keys
    assert "label" in response.json()
    assert "confidence" in response.json()

def test_env_vars():
    """Verify that essential environment variables are loaded"""
    # This ensures your HuggingFace models can be fetched correctly
    assert os.getenv("HF_MODEL") is not None