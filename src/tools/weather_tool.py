from langchain.tools import tool
import requests
import os


@tool
def get_current_weather(location_name: str) -> dict:
    """Get current weather for a city"""

    api_key = os.getenv("WEATHER_API_KEY")

    url = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": location_name,
        "appid": api_key,
        "units": "metric"
    }

    res = requests.get(url, params=params)

    if res.status_code != 200:
        return {"error": "Weather not available"}

    data = res.json()

    return {
        "location": location_name,
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }