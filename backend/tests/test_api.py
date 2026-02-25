"""
Basic API tests for the music similarity application.

To run: pytest tests/
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test that the health check endpoint works"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


def test_hello_endpoint():
    """Test the basic hello endpoint"""
    response = client.get("/api/hello")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Hello from FastAPI!"


def test_search_missing_fields():
    """Test search with missing required fields"""
    response = client.post("/api/search", json={})
    assert response.status_code == 422  # Validation error


def test_search_empty_fields():
    """Test search with empty strings"""
    response = client.post("/api/search", json={"artist": "", "title": ""})
    assert response.status_code == 400


def test_search_nonexistent_song():
    """Test search for a song that doesn't exist"""
    response = client.post(
        "/api/search",
        json={"artist": "NonexistentArtist123", "title": "NonexistentSong456"}
    )
    # Should return 404 if song not found
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


# TODO: Add test with actual song data once database is populated
# def test_search_valid_song():
#     """Test search with a real song from the database"""
#     response = client.post(
#         "/api/search",
#         json={"artist": "Real Artist", "title": "Real Song"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "success"
#     assert "songs" in data
#     assert len(data["songs"]) > 0
