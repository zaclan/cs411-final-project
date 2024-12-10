from dataclasses import asdict, dataclass
import logging
from typing import Any, List

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from db import db
from utils.logger import configure_logger

class FavoriteLocation(db.Model):
    __tablename__ = 'favorite_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    @classmethod
    def create_favorite(cls, location_name: str) -> None:
        """
        Create a new meal in the database.

        Args:
            meal (str): The name of the meal.
            cuisine (str): The type of cuisine (e.g., 'Italian', 'Mexican').
            price (float): The price of the meal. Must be a positive number.
            difficulty (str): The difficulty level of preparing the meal ('LOW', 'MED', 'HIGH').
            battles (int, optional): Initial number of battles for the meal. Defaults to 0.
            wins (int, optional): Initial number of wins for the meal. Defaults to 0.

        Raises:
            ValueError: If the price or difficulty level is invalid, or if a meal with the same name exists.
            IntegrityError: If there is a database error.
        """

        # Create and commit the new meal
        new_meal = cls(location_name=location_name)
        try:
            db.session.add(new_meal)
            db.session.commit()
            logger.info("favorite location successfully added to the database: %s", meal)
        except Exception as e:
            db.session.rollback()
            if isinstance(e, IntegrityError):
                logger.error("Duplicate meal name: %s", meal)
                raise ValueError(f"Meal with name '{meal}' already exists")
            else:
                logger.error("Database error: %s", str(e))
                raise