# tests/test_favorite_locations.py

import pytest
from unittest.mock import patch
from models.user_model import Users
from models.favourite_location import FavoriteLocation


def test_add_favorite_location_success(client, session):
    """
    Test adding a favorite location with valid data.
    """
    # Create and login user
    Users.create_user("testuser", "password123")

    # Mock the get_coordinates function
    with patch('weather_api.get_coordinates') as mock_get_coordinates:
        mock_get_coordinates.return_value = (40.7128, -74.0060)  # New York coordinates

        payload = {
            "username": "testuser",
            "password": "password123",
            "location_name": "New York"
        }
        response = client.post('/api/favorites', json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert "message" in data
        assert data["message"] == "Favorite location 'New York' added successfully."
        assert "favorite_location" in data
        assert data["favorite_location"]["location_name"] == "New York"

        # Verify in the database
        favorite = FavoriteLocation.query.filter_by(location_name="New York").first()
        assert favorite is not None
        assert favorite.latitude == 40.7128
        assert favorite.longitude == -74.0060

def test_add_favorite_location_duplicate(client, session):
    """
    Test adding a favorite location that already exists for the user.
    """
    # Create and login user
    new_user = Users.create_user("testuser", "password123")
    
    # Add the favorite location once
    FavoriteLocation.create_favorite(new_user.id, "New York", 40.7128, -74.0060)
    
    # Attempt to add the same location again
    with pytest.raises(ValueError, match="Favorite location 'New York' already exists."):
        # Attempt to create a duplicate meal
        FavoriteLocation.create_favorite(new_user.id, "New York", 40.7128, -74.0060)
        session.rollback()  # Rollback the transaction to clean up

def test_add_favorite_location_invalid_credentials(client, session):
    """
    Test adding a favorite location with invalid user credentials.
    """
    # Create user
    Users.create_user("testuser", "password123")

    payload = {
        "username": "testuser",
        "password": "wrongpassword",
        "location_name": "New York"
    }
    response = client.post('/api/favorites', json=payload)
    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data
    assert '401 Unauthorized: Authentication failed due to an unexpected error.' in data["error"]

def test_add_favorite_location_missing_fields(client):
    """
    Test adding a favorite location with missing fields.
    """
    payload = {
        "username": "testuser",
        "password": "password123"
        # Missing 'location_name'
    }
    response = client.post('/api/favorites', json=payload)
    data = response.get_json()
    
    assert response.status_code == 400

def test_add_favorite_location_external_api_failure(client, session):
    """
    Test adding a favorite location when external API fails to provide coordinates.
    """
    # Create and login user
    Users.create_user("testuser", "password123")

    # Mock the get_coordinates function to raise an exception
    with patch('weather_api.get_coordinates') as mock_get_coordinates:
        mock_get_coordinates.side_effect = Exception("External API error")

        payload = {
            "username": "testuser",
            "password": "password123",
            "location_name": "InvalidCity"
        }
        response = client.post('/api/favorites', json=payload)
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Could not fetch coordinates for the provided location." in data["error"]