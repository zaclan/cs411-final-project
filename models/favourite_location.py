from db import db
import logging
from typing import Any, List, Optional
from datetime import datetime, date

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
        if location_name == None or location_name == "":
            logger.warning(f"Invalid city name.")
            raise ValueError("Invalid city name.")        
        
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
    def get_current_weather(cls, favorite_id: int, user_id: int) -> tuple: 
        """
        Retrieve the latitude and longitude for a specific favorite location.

        Args:
            favorite_id (int): The ID of the favorite location.
            user_id (int): The ID of the user.

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
        return (favorite.latitude, favorite.longitude)
    

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
        
        # Validate and parse dates
        try:
            start_date_check, end_date_check = validate_dates(start_date, end_date)
        except ValueError as ve:
            logger.error(f"Date validation error: {ve}")
            raise ValueError(str(ve))
        
        logger.info(f"Retrieved favorite location '{favorite.location_name}' with coordinates: ({favorite.latitude}, {favorite.longitude}).")

        # Return the coordinates and dates
        return (favorite.latitude, favorite.longitude, start_date, end_date)
    
    @classmethod
    def get_forecast_details(cls, favorite_id: int, user_id: int) -> dict:
        """
        Retrieve details for fetching a weather forecast for a specific favorite location.

        Args:
            favorite_id (int): The ID of the favorite location.
            user_id (int): The ID of the user.

        Returns:
            dict: A dictionary containing the favorite location's details.

        Raises:
            ValueError: If the favorite location is not found.
        """
        favorite = cls.query.filter_by(id=favorite_id, user_id=user_id).first()
        if not favorite:
            logger.error(f"Favorite location with ID '{favorite_id}' not found for user ID '{user_id}'.")
            raise ValueError(f"Favorite location with ID '{favorite_id}' not found.")
        
        logger.info(f"Favorite location '{favorite.location_name}' found with coordinates ({favorite.latitude}, {favorite.longitude}).")
        return (favorite.id, favorite.location_name, favorite.latitude, favorite.longitude)

    
    
def validate_dates(start_date_str: str, end_date_str: str) -> tuple:
    """
    Helper method that alidates and parses start and end dates.
    
    Args:
        start_date_str (str): Start date in 'YYYY-MM-DD' format.
        end_date_str (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
        tuple: Parsed start and end dates as datetime.date objects.
    
    Raises:
        ValueError: If date formats are incorrect or logical inconsistencies are found.
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. Start date must be in 'YYYY-MM-DD' format.")
    
    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Invalid date format. End date must be in 'YYYY-MM-DD' format.")
    
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")
    
    # Optional: Check if dates are within a reasonable range
    today = date.today()
    if end_date > today:
        raise ValueError("End date cannot be in the future.")
    
    # Optional: Check how far back historical data is available
    earliest_date = date(1900, 1, 1)  # Example: Adjust based on API capabilities
    if start_date < earliest_date:
        raise ValueError(f"Start date cannot be before {earliest_date.isoformat()}.")
    
    return start_date, end_date
