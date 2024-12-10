import os
import requests
import logging
from dotenv import load_dotenv

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


load_dotenv()

logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org"

@dataclass
class Weather:
    city: str
    lat: float
    lon: float   

    def __post_init__(self):
        if self.lat < -90 or self.lat > 90:
            raise ValueError("latitude must be between -90 and 90.")
            
        if self.lon < -180 or self.lon > 180:
            raise ValueError("longitude must be between -180 and 180.")


def get_coordinates(city: str):
    url =f"{BASE_URL}/geo/1.0/direct?q={city}&limit=5&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    lat, lon = data[0]["lat"], data[0]["lon"]
    return lat, lon

def get_current_weather(lat, lon):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "showers", "snowfall", "wind_speed_10m"]
    }
    responses = openmeteo.weather_api(url, params=params)

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]  # Assuming single location response

        # Extract current weather data
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_precipitation = current.Variables(2).Value()
        current_rain = current.Variables(3).Value()
        current_showers = current.Variables(4).Value()
        current_snowfall = current.Variables(5).Value()
        current_wind_speed_10m = current.Variables(6).Value()

        # Structure the data into a dictionary
        weather_data = {
            "coordinates": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude()
            },
            "elevation": response.Elevation(),
            "timezone": response.Timezone(),
            "utc_offset_seconds": response.UtcOffsetSeconds(),
            "current_weather": {
                "time": current.Time(),
                "temperature": current_temperature_2m,
                "humidity": current_relative_humidity_2m,
                "windspeed": current_wind_speed_10m,
                "precipitation": current_precipitation,
            }
        }

        logger.info(f"Successfully fetched current weather for ({lat}, {lon})")
        return weather_data

    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise
    

def get_forecast(lat, lon, days=7):
    if (days > 16):
        logger.error("Maximum number of days possible is 16.")
        return {"error" : "Forecast days exceeded."}
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "daylight_duration", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max"],
        "timezone": "auto",
        "forecast_days": days
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(6).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(7).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max

    daily_dataframe = pd.DataFrame(data = daily_data)
    print(daily_dataframe)

def get_historical_weather(lat, lon, start: str, end: str):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "daylight_duration", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max"],
	    "timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(4).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(5).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(6).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(7).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["precipitation_sum"] = daily_precipitation_sum
    daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max

    daily_dataframe = pd.DataFrame(data = daily_data)
    return daily_dataframe



def add_fav(city: str) -> None:
    """
    Adds a city and its weather data to the favorites table in the database.

    Args:
        city (str): The name of the city to be added.
    """
    try:
        # Fetch coordinates and weather data
        lat, lon = get_coordinates(city)
        weather_data = get_current_weather(lat, lon)

        # Insert data into the database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO weather (
                    city, lat, lon, elevation, timezone, utc_offset_seconds, 
                    time, temperature, humidity, windspeed, precipitation
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                city,
                weather_data["coordinates"]["latitude"],
                weather_data["coordinates"]["longitude"],
                weather_data["elevation"],
                weather_data["timezone"],
                weather_data["utc_offset_seconds"],
                weather_data["current_weather"]["time"],
                weather_data["current_weather"]["temperature"],
                weather_data["current_weather"]["humidity"],
                weather_data["current_weather"]["windspeed"],
                weather_data["current_weather"]["precipitation"]
            ))
            conn.commit()

        logger.info(f"City '{city}' with current weather data added to the database.")

    except sqlite3.IntegrityError:
        logger.error(f"City '{city}' is already in the favorites.")
        raise ValueError(f"City '{city}' already exists in the favorites.")

    except Exception as e:
        logger.error(f"Failed to add city '{city}': {str(e)}")
        raise


def get_favs() -> list[dict]:
    """
    Retrieves the list of favorite cities along with their weather data.

    Returns:
        list[dict]: A list of dictionaries, each containing weather details of the favorite cities.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT city, lat, lon, elevation, timezone, utc_offset_seconds, 
                       time, temperature, humidity, windspeed, precipitation
                FROM weather
            """)
            rows = cursor.fetchall()

        favorites = []
        for row in rows:
            favorites.append({
                "city": row[0],
                "coordinates": {
                    "latitude": row[1],
                    "longitude": row[2]
                },
                "elevation": row[3],
                "timezone": row[4],
                "utc_offset_seconds": row[5],
                "current_weather": {
                    "time": row[6],
                    "temperature": row[7],
                    "humidity": row[8],
                    "windspeed": row[9],
                    "precipitation": row[10]
                }
            })

        logger.info("Favorite cities retrieved successfully.")
        return favorites

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise


if __name__ == "__main__":
    lat, lon = get_coordinates('london')
    print(lat, lon)
    response = get_historical_weather(lat, lon, "2024-11-24", "2024-12-07")
    print(response)
    current = get_current_weather(lat, lon)
    print(current)
    forecase = get_forecast(lat, lon)
    print(forecase)
    favorites = add_fav('london')
    print(favorite)
    favorites = add_fav('london')
    print(favorite)
    list = get_favs()
    print(get_favs)
	
	


