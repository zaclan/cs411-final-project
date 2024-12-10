from flask import Flask, jsonify, request, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
import logging
from dotenv import load_dotenv
import os

from models.user_model import Users
from models.favourite_location import FavoriteLocation
import weather_api
from db import db
from config import ProductionConfig, TestConfig

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def create_app(config_class=TestConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables
        print("Tables created successfully!")
    

    # Helper function for user authentication
    def authenticate_user(request_data) -> Users:
        """
        Authenticates a user by verifying the provided username and password.

        Args:
            request_data (dict): Dictionary containing 'username' and 'password'.

        Returns:
            Users: The authenticated user object.

        Raises:
            Unauthorized: If authentication fails.
        """
        username = request_data.get('username')
        password = request_data.get('password')
        if not username or not password:
            logger.error("Username or password not provided.")
            raise Unauthorized("Username and password are required.")

        try:
            is_valid = Users.check_password(username, password)
            if not is_valid:
                logger.warning(f"Authentication failed for user '{username}'.")
                raise Unauthorized("Invalid username or password.")
            user = Users.query.filter_by(username=username).first()
            return user
        except ValueError as ve:
            logger.error(f"Authentication error: {ve}")
            raise Unauthorized(str(ve))
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            raise Unauthorized("Authentication failed due to an unexpected error.")



    ####################################################
    #
    # User Management Routes
    #
    ####################################################

    @app.route('/create-account', methods=['POST'])
    def create_account() -> Response:
        """
        Route to create a new user account.
        Expects 'username' and 'password' in the JSON body.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Invalid account creation payload.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            Users.create_user(username, password)
            logger.info(f"Account created successfully for user '{username}'.")
            return jsonify({"message": f"Account created successfully for user '{username}'."}), 201
        except ValueError as ve:
            logger.error(f"Account creation error: {ve}")
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error(f"Unexpected error during account creation: {e}")
            return jsonify({"error": "Internal server error."}), 500

    @app.route('/login', methods=['POST'])
    def login():
        """
        Route to authenticate a user.
        Expects 'username' and 'password' in the JSON body.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            logger.error("Invalid login payload.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        try:
            user = authenticate_user(data)
            logger.info(f"User '{user.username}' authenticated successfully.")
            return jsonify({"message": f"User '{user.username}' authenticated successfully."}), 200
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            return jsonify({"error": "Internal server error."}), 500

    @app.route('/update-password', methods=['POST'])
    def update_password():
        """
        Route to update a user's password.
        Expects 'username', 'current_password', and 'new_password' in the JSON body.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'current_password' not in data or 'new_password' not in data:
            logger.error("Invalid password update payload.")
            raise BadRequest("Invalid request payload. 'username', 'current_password', and 'new_password' are required.")

        username = data['username']
        current_password = data['current_password']
        new_password = data['new_password']

        # Authenticate user with current credentials
        try:
            user = authenticate_user({'username': username, 'password': current_password})
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during password update authentication: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Update password
        try:
            Users.update_password(username, new_password)
            logger.info(f"Password updated successfully for user '{username}'.")
            return jsonify({"message": f"Password updated successfully for user '{username}'."}), 200
        except ValueError as ve:
            logger.error(f"Password update error: {ve}")
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error(f"Unexpected error during password update: {e}")
            return jsonify({"error": "Internal server error."}), 500



    ####################################################
    #
    # Favorite Locations Management Routes
    #
    ####################################################

    @app.route('/api/favorites', methods=['POST'])
    def add_favorite_location():
        """
        Route to add a new favorite location for a user.
        Expects 'username', 'password', and 'location_name' in the JSON body.
        """
        data = request.get_json()
        if not data or 'location_name' not in data:
            logger.error("Invalid payload for adding favorite location.")
            raise BadRequest("Invalid request payload. 'location_name' is required.")

        location_name = data['location_name']

        # Authenticate user
        try:
            user = authenticate_user(data)
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during favorite location addition: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Fetch coordinates
        try:
            lat, lon = weather_api.get_coordinates(location_name)
        except ValueError as ve:
            logger.error(f"Error fetching coordinates: {ve}")
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error(f"Unexpected error fetching coordinates: {e}")
            return jsonify({"error": "Could not fetch coordinates for the provided location."}), 500

        try:
            new_favorite = FavoriteLocation.create_favorite(user_id=user.id, location_name=location_name, latitude=lat, longitude=lon)
            logger.info('Favorite location added: %s', location_name)
            return jsonify({
                "message": f"Favorite location '{location_name}' added successfully.",
                "favorite_location": {
                    "id": new_favorite.id,
                    "location_name": new_favorite.location_name,
                    "latitude": new_favorite.latitude,
                    "longitude": new_favorite.longitude
                }
            }), 201
        except:
            logger.error('Failed to add favorite location.')
            return jsonify({"error": "Internal server error."}), 500
            

    @app.route('/api/favorites', methods=['GET'])
    def get_all_favorites():
        """
        Route to retrieve all favorite locations for a user.
        Expects 'username' and 'password' as query parameters.
        """
        username = request.args.get('username')
        password = request.args.get('password')

        if not username or not password:
            logger.error("Missing 'username' or 'password' query parameters.")
            raise BadRequest("Missing 'username' or 'password' query parameters.")

        # Authenticate user
        try:
            user = authenticate_user({'username': username, 'password': password})
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during fetching all favorites: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Retrieve all favorites
        favorites = FavoriteLocation.query.filter_by(user_id=user.id).all()
        favorites_data = [{
            "id": fav.id,
            "location_name": fav.location_name,
            "latitude": fav.latitude,
            "longitude": fav.longitude
        } for fav in favorites]

        logger.info(f"Retrieved all favorites for user '{user.username}'.")
        return jsonify({"favorites": favorites_data}), 200


    @app.route('/api/favorites/weather', methods=['GET'])
    def get_all_favorites_with_weather():
        """
        Route to retrieve all favorite locations for a user along with their current weather.
        Expects 'username' and 'password' as query parameters.
        """
        username = request.args.get('username')
        password = request.args.get('password')

        if not username or not password:
            logger.error("Missing 'username' or 'password' query parameters.")
            raise BadRequest("Missing 'username' or 'password' query parameters.")

        # Authenticate user
        try:
            user = authenticate_user({'username': username, 'password': password})
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during fetching favorites with weather: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Retrieve all favorites
        favorites = FavoriteLocation.query.filter_by(user_id=user.id).all()
        if not favorites:
            logger.info(f"No favorite locations found for user '{user.username}'.")
            return jsonify({"favorites": []}), 200

        favorites_with_weather = []
        for fav in favorites:
            try:
                weather = weather_api.get_current_weather(fav.latitude, fav.longitude)
                favorites_with_weather.append({
                    "id": fav.id,
                    "location_name": fav.location_name,
                    "latitude": fav.latitude,
                    "longitude": fav.longitude,
                    "current_weather": weather['current_weather']
                })
            except Exception as e:
                logger.error(f"Error fetching weather for '{fav.location_name}': {e}")
                favorites_with_weather.append({
                    "id": fav.id,
                    "location_name": fav.location_name,
                    "latitude": fav.latitude,
                    "longitude": fav.longitude,
                    "current_weather": None,
                    "error": "Could not fetch weather data."
                })

        logger.info(f"Retrieved all favorites with weather for user '{user.username}'.")
        return jsonify({"favorites": favorites_with_weather}), 200


    @app.route('/api/favorites/<int:favorite_id>/weather', methods=['GET'])
    def get_weather_for_favorite(favorite_id):
        """
        Route to retrieve current weather for a specific favorite location.
        Expects 'username' and 'password' as query parameters.
        """
        username = request.args.get('username')
        password = request.args.get('password')

        if not username or not password:
            logger.error("Missing 'username' or 'password' query parameters.")
            raise BadRequest("Missing 'username' or 'password' query parameters.")

        # Authenticate user
        try:
            user = authenticate_user({'username': username, 'password': password})
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during fetching weather for favorite: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Retrieve the specific favorite location
        favorite = FavoriteLocation.query.filter_by(id=favorite_id, user_id=user.id).first()
        if not favorite:
            logger.error(f"Favorite location with ID '{favorite_id}' not found for user '{user.username}'.")
            raise NotFound(f"Favorite location with ID '{favorite_id}' not found.")

        # Fetch current weather
        try:
            weather = weather_api.get_current_weather(favorite.latitude, favorite.longitude)
            logger.info(f"Retrieved current weather for favorite location '{favorite.location_name}'.")
            return jsonify({
                "favorite_location": {
                    "id": favorite.id,
                    "location_name": favorite.location_name,
                    "latitude": favorite.latitude,
                    "longitude": favorite.longitude
                },
                "current_weather": weather['current_weather']
            }), 200
        except Exception as e:
            logger.error(f"Error fetching weather for favorite location '{favorite.location_name}': {e}")
            return jsonify({"error": "Could not fetch weather data."}), 500


    @app.route('/api/favorites/<int:favorite_id>/historical', methods=['GET'])
    def get_historical_weather_for_favorite(favorite_id):
        """
        Route to retrieve historical weather data for a specific favorite location.
        Expects 'username', 'password', 'start_date', and 'end_date' as query parameters.
        Dates should be in 'YYYY-MM-DD' format.
        """
        username = request.args.get('username')
        password = request.args.get('password')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not username or not password or not start_date or not end_date:
            logger.error("Missing required query parameters for historical weather.")
            raise BadRequest("Missing 'username', 'password', 'start_date', or 'end_date' query parameters.")

        # Authenticate user
        try:
            user = authenticate_user({'username': username, 'password': password})
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during fetching historical weather: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Retrieve the specific favorite location
        favorite = FavoriteLocation.query.filter_by(id=favorite_id, user_id=user.id).first()
        if not favorite:
            logger.error(f"Favorite location with ID '{favorite_id}' not found for user '{user.username}'.")
            raise NotFound(f"Favorite location with ID '{favorite_id}' not found.")

        # Fetch historical weather
        try:
            historical_weather = weather_api.get_historical_weather(favorite.latitude, favorite.longitude, start_date, end_date)
            logger.info(f"Retrieved historical weather for favorite location '{favorite.location_name}'.")
            return jsonify({
                "favorite_location": {
                    "id": favorite.id,
                    "location_name": favorite.location_name,
                    "latitude": favorite.latitude,
                    "longitude": favorite.longitude
                },
                "historical_weather": historical_weather['historical_weather']
            }), 200
        except ValueError as ve:
            logger.error(f"Historical weather request error: {ve}")
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error fetching historical weather for '{favorite.location_name}': {e}")
            return jsonify({"error": "Could not fetch historical weather data."}), 500


    @app.route('/api/favorites/<int:favorite_id>/forecast', methods=['GET'])
    def get_forecast_for_favorite(favorite_id):
        """
        Route to retrieve weather forecast for a specific favorite location.
        Expects 'username', 'password', and optional 'days' as query parameters.
        """
        username = request.args.get('username')
        password = request.args.get('password')
        days = request.args.get('days', default=7, type=int)

        if not username or not password:
            logger.error("Missing 'username' or 'password' query parameters.")
            raise BadRequest("Missing 'username' or 'password' query parameters.")

        # Authenticate user
        try:
            user = authenticate_user({'username': username, 'password': password})
        except Unauthorized as ue:
            return jsonify({"error": str(ue)}), 401
        except Exception as e:
            logger.error(f"Unexpected error during fetching forecast: {e}")
            return jsonify({"error": "Internal server error."}), 500

        # Retrieve the specific favorite location
        favorite = FavoriteLocation.query.filter_by(id=favorite_id, user_id=user.id).first()
        if not favorite:
            logger.error(f"Favorite location with ID '{favorite_id}' not found for user '{user.username}'.")
            raise NotFound(f"Favorite location with ID '{favorite_id}' not found.")

        # Fetch forecast
        try:
            forecast = weather_api.get_forecast(favorite.latitude, favorite.longitude, days)
            logger.info(f"Retrieved forecast for favorite location '{favorite.location_name}'.")
            return jsonify({
                "favorite_location": {
                    "id": favorite.id,
                    "location_name": favorite.location_name,
                    "latitude": favorite.latitude,
                    "longitude": favorite.longitude
                },
                "weather_forecast": forecast['daily_forecast']
            }), 200
        except ValueError as ve:
            logger.error(f"Forecast request error: {ve}")
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            logger.error(f"Error fetching forecast for '{favorite.location_name}': {e}")
            return jsonify({"error": "Could not fetch weather forecast data."}), 500
        
        
    ####################################################
    #
    # Healthchecks
    #
    ####################################################
    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        response = make_response(jsonify({"status": "healthy"}), 200)
        app.logger.debug(f"Health Check Response: {response.get_data(as_text=True)}") 
        return response  
    
    return app

####################################################
#
# Run the Flask Application
#
####################################################

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)