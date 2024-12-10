
from db import db
import logging

logger = logging.getLogger(__name__)

class FavoriteLocation(db.Model):
    __tablename__ = 'favorite_locations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    def __init__(self, user_id: int, location_name: str, latitude: float, longitude: float):
        self.user_id = user_id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
