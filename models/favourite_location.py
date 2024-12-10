from db import db
import logging
from typing import Any, List, Optional

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

class FavoriteLocation(db.Model):
    __tablename__ = 'favorite_locations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    def __post_init__(self):
        if not self.location_name:
            raise ValueError("Location name must be provided.")
        if not isinstance(self.latitude, float) or not isinstance(self.longitude, float):
            raise ValueError("Latitude and Longitude must be float values.")
    
    @classmethod
    def create_favorite(cls, user_id: int, location_name: str, latitude: float, longitude: float) -> 'FavoriteLocation':
        """
        Create a new favorite location for a user.

        Args:
            user_id (int): The ID of the user.
            location_name (str): The name of the location to add.
            latitude(float): The latitude of the location.
            longitude(float): The longitude of the location.

        Returns:
            FavoriteLocation: The newly created favorite location instance.

        Raises:
            ValueError: If the favorite location already exists or coordinates cannot be fetched.
            IntegrityError: If there's a database constraint violation.
        """
        logger.info(f"Attempting to add favorite location '{location_name}' for user ID '{user_id}'.")

        # Check if the favorite location already exists for the user
        existing_fav = cls.query.filter_by(user_id=user_id, location_name=location_name, latitude=latitude, longitude=longitude).first()
        if existing_fav:
            logger.warning(f"Favorite location '{location_name}' already exists for user ID '{user_id}'.")
            raise ValueError(f"Favorite location '{location_name}' already exists.")

        # Create and add the new favorite location
        new_fav = cls(
            user_id=user_id,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude
        )
        try:
            db.session.add(new_fav)
            db.session.commit()
            logger.info(f"Favorite location '{location_name}' added successfully for user ID '{user_id}'.")
            return new_fav
        except IntegrityError as ie:
            db.session.rollback()
            logger.error(f"Database IntegrityError while adding favorite location '{location_name}': {ie}")
            raise ValueError(f"Favorite location '{location_name}' could not be added due to a database error.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error while adding favorite location '{location_name}': {e}")
            raise ValueError("An unexpected error occurred while adding the favorite location.")

    @classmethod
    def get_all_favorites(cls, user_id: int) -> List['FavoriteLocation']:
        """
        Retrieve all favorite locations for a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[FavoriteLocation]: A list of the user's favorite locations.
        """
        logger.info(f"Retrieving all favorite locations for user ID '{user_id}'.")
        favorites = cls.query.filter_by(user_id=user_id).all()
        logger.debug(f"Found {len(favorites)} favorite locations for user ID '{user_id}'.")
        return favorites
    

    @classmethod
    def get_historical_weather(cls, favorite_id: int, user_id: int, start_date: str, end_date: str) -> tuple:
        """
        Retrieve the latitude and longitude for a specific favorite location.

        Args:
            favorite_id (int): The ID of the favorite location.
            user_id (int): The ID of the user.
            start_date (str): The start date for historical weather in 'YYYY-MM-DD' format.
            end_date (str): The end date for historical weather in 'YYYY-MM-DD' format.

        Returns:
            tuple: A tuple containing latitude, longitude, start_date, and end_date.

        Raises:
            ValueError: If the favorite location is not found.
        """
        # Retrieve the specific favorite location
        favorite = cls.query.filter_by(id=favorite_id, user_id=user_id).first()
        if not favorite:
            logger.error(f"Favorite location with ID '{favorite_id}' not found for user ID '{user_id}'.")
            raise ValueError(f"Favorite location with ID '{favorite_id}' not found.")
        
        logger.info(f"Retrieved favorite location '{favorite.location_name}' with coordinates: ({favorite.latitude}, {favorite.longitude}).")

        # Return the coordinates and dates
        return (favorite.latitude, favorite.longitude, start_date, end_date)
