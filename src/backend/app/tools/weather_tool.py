import requests

from src.backend.app.config.settings import (
    settings
)


# =========================================================
# WEATHER TOOL
# =========================================================

class WeatherTool:

    def __init__(self):

        self.api_key = (
            settings.OPENWEATHER_API_KEY
        )

        self.current_url = (
            settings.OPENWEATHER_CURRENT_URL
        )

        self.forecast_url = (
            settings.OPENWEATHER_FORECAST_URL
        )

        self.geocoding_url = (
            settings.OPENWEATHER_GEOCODING_URL
        )

    # =====================================================
    # GEOCODE CITY
    # =====================================================

    def geocode_city(
        self,
        city: str
    ):

        print("\n===== GEOCODING =====\n")

        response = requests.get(

            self.geocoding_url,

            params={

                "q": city,

                "limit": 1,

                "appid": self.api_key
            },

            timeout=20
        )

        print(response.url)

        if response.status_code != 200:

            print(response.text)

            return None

        data = response.json()

        print("\n===== GEOCODING RESULT =====\n")

        print(data)

        if not data:

            return None

        return {

            "lat": data[0]["lat"],

            "lon": data[0]["lon"]
        }

    # =====================================================
    # CURRENT WEATHER
    # =====================================================

    def get_current_weather(
        self,
        city: str
    ):

        print("\n===== CURRENT WEATHER =====\n")

        response = requests.get(

            self.current_url,

            params={

                "q": city,

                "appid": self.api_key,

                "units": "metric"
            },

            timeout=20
        )

        print(response.url)

        if response.status_code != 200:

            print("\n===== RAW API ERROR =====\n")

            print(response.text)

            return {

                "success": False,

                "error":
                f"API failed: {response.status_code}"
            }

        data = response.json()

        print("\n===== RAW CURRENT WEATHER =====\n")

        print(data)

        return {

            "success": True,

            "type": "current",

            "weather": {

                "city":
                data["name"],

                "temperature":
                data["main"]["temp"],

                "feels_like":
                data["main"]["feels_like"],

                "humidity":
                data["main"]["humidity"],

                "description":
                data["weather"][0]["description"],

                "wind_speed":
                data["wind"]["speed"]
            }
        }

    # =====================================================
    # FORECAST WEATHER
    # =====================================================

    def get_forecast_weather(
        self,
        city: str
    ):

        print("\n===== FORECAST WEATHER =====\n")

        response = requests.get(

            self.forecast_url,

            params={

                "q": city,

                "appid": self.api_key,

                "units": "metric"
            },

            timeout=20
        )

        print(response.url)

        if response.status_code != 200:

            print("\n===== RAW API ERROR =====\n")

            print(response.text)

            return {

                "success": False,

                "error":
                f"API failed: {response.status_code}"
            }

        data = response.json()

        print("\n===== RAW FORECAST DATA =====\n")

        print(data)

        return {

            "success": True,

            "data": data
        }

    # =====================================================
    # MAIN WEATHER REASONING
    # =====================================================

    def get_weather_by_query(

        self,

        city: str,

        weather_type: str,

        forecast_days: int = 0,

        forecast_hours: int = 0
    ):

        # =================================================
        # CURRENT
        # =================================================

        if weather_type == "current":

            return self.get_current_weather(
                city
            )

        # =================================================
        # FORECAST
        # =================================================

        forecast_result = self.get_forecast_weather(
            city
        )

        if not forecast_result["success"]:

            return forecast_result

        data = forecast_result["data"]

        # =================================================
        # DAILY
        # =================================================

        if weather_type == "daily":

            forecast = []

            daily_entries = data["list"]

            used_dates = set()

            for item in daily_entries:

                date = item[
                    "dt_txt"
                ].split(" ")[0]

                if date in used_dates:

                    continue

                used_dates.add(date)

                forecast.append({

                    "datetime":
                    item["dt_txt"],

                    "temperature":
                    item["main"]["temp"],

                    "humidity":
                    item["main"]["humidity"],

                    "description":
                    item["weather"][0]["description"]
                })

                if len(forecast) >= forecast_days:

                    break

            return {

                "success": True,

                "type": "daily",

                "forecast":
                forecast
            }

        # =================================================
        # HOURLY
        # =================================================

        elif weather_type == "hourly":

            forecast = []

            for item in data["list"][
                :forecast_hours
            ]:

                forecast.append({

                    "datetime":
                    item["dt_txt"],

                    "temperature":
                    item["main"]["temp"],

                    "humidity":
                    item["main"]["humidity"],

                    "description":
                    item["weather"][0]["description"]
                })

            return {

                "success": True,

                "type": "hourly",

                "forecast":
                forecast
            }

        # =================================================
        # FALLBACK
        # =================================================

        return {

            "success": False,

            "error":
            "Unsupported weather type."
        }


# =========================================================
# GLOBAL SINGLETON
# =========================================================

weather_tool = WeatherTool()