# tests/test_favorite_locations.py

import pytest
from unittest.mock import patch
from models.user_model import Users
from models.favourite_location import FavoriteLocation
from sqlalchemy.exc import IntegrityError


##########################################################
# Add
##########################################################


def test_add_favorite_location_success(client, session):
    """
    Test adding a favorite location with valid data.
    """
    # Create and login user
    user = Users.create_user("testuser", "password123")

    # Mock the get_coordinates function
    with patch('weather_api.get_coordinates') as mock_get_coordinates:
        mock_get_coordinates.return_value = (40.7128, -74.0060)  # New York coordinates

        # Attempt to create a favorite location
        fav = FavoriteLocation.create_favorite(user_id=user.id, location_name="New York", latitude=40.7128, longitude=-74.0060)
        
        # Assertions
        assert fav.id is not None
        assert fav.user_id == user.id
        assert fav.location_name == "New York"
        assert fav.latitude == 40.7128
        assert fav.longitude == -74.0060

def test_add_favorite_location_duplicate(client, session):
    """
    Test adding a favorite location that already exists for the user.
    """
    # Create and login user
    user = Users.create_user("testuser", "password123")
    
    with patch('weather_api.get_coordinates') as mock_get_coordinates:
        mock_get_coordinates.return_value = (34.0522, -118.2437)  # Coordinates for Los Angeles
        
        # Create first favorite
        FavoriteLocation.create_favorite(user_id=user.id, location_name="Los Angeles", latitude=34.0522, longitude=-118.2437)
        
        # Attempt to create duplicate
        with pytest.raises(ValueError) as exc_info:
            FavoriteLocation.create_favorite(user_id=user.id, location_name="Los Angeles", latitude=34.0522, longitude=-118.2437)
        assert "already exists" in str(exc_info.value)



def test_create_favorite_invalid_coordinates(session):
    """
    Test creating a favorite location when fetching coordinates fails.
    """
    user = Users.create_user("testuser", "password123")
    
    with patch('weather_api.get_coordinates') as mock_get_coordinates:
        mock_get_coordinates.side_effect = ValueError("Invalid city name.")
        
        with pytest.raises(ValueError) as exc_info:
            FavoriteLocation.create_favorite(user_id=user.id, location_name="", latitude=0.0, longitude=0.0)
        assert "Invalid city name." in str(exc_info.value)
        

##########################################################
# Get
##########################################################

def test_get_all_favorites(session):
    """
    Test retrieving all favorite locations for a user.
    """
    user = Users.create_user("testuser", "password123")

    # Create multiple favorites
    with patch('weather_api.get_coordinates') as mock_get_coordinates:
        mock_get_coordinates.side_effect = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437)  # Los Angeles
        ]
        FavoriteLocation.create_favorite(user.id, "New York", 40.7128, -74.0060)
        FavoriteLocation.create_favorite(user.id, "Los Angeles", 34.0522, -118.2437 )

    favorites = FavoriteLocation.get_all_favorites(user.id)
    assert len(favorites) == 2
    assert favorites[0].location_name == "New York"
    assert favorites[1].location_name == "Los Angeles"


def test_get_all_favorites_with_weather_success(session):
    """
    Test retrieving all favorite locations with current weather data.
    """
    user = Users.create_user("testuser", "password123")

    with patch('weather_api.get_coordinates') as mock_get_coordinates, \
         patch('weather_api.get_current_weather') as mock_get_current_weather:
        
        mock_get_coordinates.side_effect = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437)  # Los Angeles
        ]
        mock_get_current_weather.side_effect = [
            {"current_weather": "Sunny"},
            {"current_weather": "Cloudy"}
        ]

        FavoriteLocation.create_favorite(user.id, "New York", 40.7128, -74.0060)
        FavoriteLocation.create_favorite(user.id, "Los Angeles", 34.0522, -118.2437 )

    favorites_with_weather = FavoriteLocation.get_all_favorites(user.id)
    assert len(favorites_with_weather) == 2
    assert favorites_with_weather[0]["location_name"] == "New York"
    assert favorites_with_weather[0]["current_weather"] == "Sunny"
    assert favorites_with_weather[1]["location_name"] == "Los Angeles"
    assert favorites_with_weather[1]["current_weather"] == "Cloudy"