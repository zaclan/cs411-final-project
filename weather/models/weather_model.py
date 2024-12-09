import requests
import logging

logger = logging.getLogger(__name__)

class Weather:
    def __init__(self, city: str, api_key: str):
        self.city = city
        self.api_key = api_key

    def fetch_weather(self):
        """Fetch weather data from OpenWeather API based on city."""
        # URL to get geo-location data for the city (latitude and longitude)
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={self.city}&limit=5&appid={self.api_key}"
        
        try:
            # Get latitude and longitude for the city
            geo_response = requests.get(geo_url)
            geo_response.raise_for_status()  # Raise exception for bad responses
            geo_data = geo_response.json()

            if not geo_data:
                logger.error("City not found: %s", self.city)
                return {"error": "City not found"}

            # Extract latitude and longitude
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

            # Fetch weather forecast data using lat and lon
            forecast_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()  # Raise exception for bad responses
            forecast_data = forecast_response.json()

            return forecast_data

        except requests.exceptions.RequestException as e:
            logger.error("Error fetching weather data: %s", e)
            return {"error": "Failed to fetch weather data"}