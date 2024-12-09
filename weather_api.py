import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "https://api.openweathermap.org/data/2.5/"

def get_current_weather(lat, lon):
    url = f"{BASE_URL}weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_forecast(lat, lon):
    url = f"{BASE_URL}forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_historical_weather(lat, lon, start, end):
    # OpenWeatherMap's One Call API requires a paid subscription for historical data
    url = f"{BASE_URL}onecall/timemachine?lat={lat}&lon={lon}&dt={start}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    response = get_current_weather(1,1)
    print(response)