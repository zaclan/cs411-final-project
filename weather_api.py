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
    
    
    try:
        responses = openmeteo.weather_api(url, params=params)
        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        dates = pd.to_datetime(daily.Time(), unit="s", utc=True)
        daily_data = {
            "date": dates,
            "temperature_2m_max": daily.Variables(0).ValuesAsNumpy().tolist(),
            "temperature_2m_min": daily.Variables(1).ValuesAsNumpy().tolist(),
            "apparent_temperature_max": daily.Variables(2).ValuesAsNumpy().tolist(),
            "apparent_temperature_min": daily.Variables(3).ValuesAsNumpy().tolist(),
            "daylight_duration": daily.Variables(4).ValuesAsNumpy().tolist(),
            "precipitation_sum": daily.Variables(5).ValuesAsNumpy().tolist(),
            "precipitation_probability_max": daily.Variables(6).ValuesAsNumpy().tolist(),
            "wind_speed_10m_max": daily.Variables(7).ValuesAsNumpy().tolist()
        }
        
        forecast_dataframe = pd.DataFrame(data=daily_data)
        
        # Convert DataFrame to dictionary for JSON serialization
        forecast_data = forecast_dataframe.to_dict(orient='records')
        
        structured_data = {
            "coordinates": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude()
            },
            "elevation": response.Elevation(),
            "timezone": response.Timezone(),
            "utc_offset_seconds": response.UtcOffsetSeconds(),
            "daily_forecast": forecast_data
        }

        logger.info(f"Successfully fetched forecast for ({lat}, {lon}) for {days} days")
        return structured_data

    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        raise

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
    
    try: 
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        
        # Extract daily forecast data
        daily = response.Daily()
        dates = pd.to_datetime(daily.Time(), unit="s", utc=True)
        daily_data = {
            "date": dates,
            "temperature_2m_max": daily.Variables(0).ValuesAsNumpy().tolist(),
            "temperature_2m_min": daily.Variables(1).ValuesAsNumpy().tolist(),
            "apparent_temperature_max": daily.Variables(2).ValuesAsNumpy().tolist(),
            "apparent_temperature_min": daily.Variables(3).ValuesAsNumpy().tolist(),
            "daylight_duration": daily.Variables(4).ValuesAsNumpy().tolist(),
            "precipitation_sum": daily.Variables(5).ValuesAsNumpy().tolist(),
            "precipitation_probability_max": daily.Variables(6).ValuesAsNumpy().tolist(),
            "wind_speed_10m_max": daily.Variables(7).ValuesAsNumpy().tolist()
        }
        
        historical_dataframe = pd.DataFrame(data=daily_data)

        # Convert DataFrame to dictionary for JSON serialization
        historical_data = historical_dataframe.to_dict(orient='records')

        structured_data = {
            "coordinates": {
                "latitude": response.Latitude(),
                "longitude": response.Longitude()
            },
            "elevation": response.Elevation(),
            "timezone": response.Timezone(),
            "utc_offset_seconds": response.UtcOffsetSeconds(),
            "historical_weather": historical_data
        }

        logger.info(f"Successfully fetched historical weather for ({lat}, {lon}) from {start} to {end}")
        return structured_data

    except Exception as e:
        logger.error(f"Error fetching historical weather: {e}")
        raise


if __name__ == "__main__":
    lat, lon = get_coordinates('london')
    print(lat, lon)
    response = get_historical_weather(lat, lon, "2024-11-24", "2024-12-07")
    #print(response)
    current = get_current_weather(lat, lon)
    #print(current)
    forecase = get_forecast(lat, lon)
    print(forecase)
    