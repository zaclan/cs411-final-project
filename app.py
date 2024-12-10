from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from werkzeug.exceptions import BadRequest, Unauthorized
# from flask_cors import CORS

from config import ProductionConfig
from meal_max.db import db


# Load environment variables from .env file
load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

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
        return make_response(jsonify({'status': 'healthy'}), 200)

   
    ##########################################################
    #
    # Weather
    #
    ##########################################################

    # Route to add a favorite city
    @app.route('/api/add_fav', methods=['POST'])
    def add_fav():
        city = request.json.get('city')  # Getting the city from the JSON payload

        if not city:
            return jsonify({"error": "City name is required."}), 400

        try:
            favorite = add_fav(city)
            return jsonify(favorite), 200

        except ValueError as ve:
            logger.error(f"Error adding favorite: {ve}")
            return jsonify({"error": str(ve)}), 400

        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return jsonify({"error": "Internal server error"}), 500

        
    # Route to get favorite cities with weather data
    @app.route('/api/get_favs', methods=['GET'])
    def get_favs():
        try:
            favorites = get_favs()

            # Return the list of favorite cities and their weather data
            return jsonify(favorites), 200

        except Exception as e:
            logger.error(f"Error fetching favorites: {e}")
            return jsonify({"error": "Internal server error"}), 500




if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
