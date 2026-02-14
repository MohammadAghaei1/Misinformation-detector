import os
import pytest
from backend.main import app 
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

# Verifies that the API root endpoint is reachable and returns a 200 status code
@pytest.mark.asyncio
async def test_health_check():
    "Test if the API is reachable using the new ASGITransport"
    # Use ASGITransport for newer versions of httpx
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

# Tests the misinformation detection logic by verifying the AI's JSON response structure
@pytest.mark.asyncio
async def test_model_prediction():
    """
    Test the core misinformation detection logic without writing to the physical database.
    """
    # prevent test data from being stored
    with patch("backend.main.append_record") as mocked_storage:
        transport = ASGITransport(app=app)
        
        # Define the payload (test data) to be sent to the prediction endpoint
        test_data = {
            "text": "test", 
            "user_id": 1
        }
        
        # Initialize an asynchronous client to perform the HTTP POST request
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Send the test data to the /predict endpoint and wait for the response
            response = await ac.post("/predict", json=test_data)
        
        # Verify that the server responded with a 200 OK status code
        assert response.status_code == 200
        
        # Check that the response JSON contains the expected AI analysis keys
        assert "label" in response.json()
        assert "confidence" in response.json()
        
        # Verify that the backend attempted to save the record exactly once, 
        mocked_storage.assert_called_once()

# Ensures that essential environment variables, like the model ID, are properly configured        
def test_env_vars():
    "Verify that essential environment variables are available"
    assert os.getenv("HF_MODEL") is not None