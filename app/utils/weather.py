import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "hourly": (
            "precipitation_probability,"
            "precipitation,"
            "weather_code"
        ),
        "forecast_days": 3,
        "timezone": "Asia/Kolkata",
    }

    try:
        response = requests.get(
            WEATHER_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print("Weather API Error:", error)
        return None


def get_location_coordinates(location_name):
    params = {
        "name": location_name,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        response = requests.get(
            GEOCODING_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results")

        if not results:
            return None

        location = results[0]

        return {
            "name": location.get("name"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "country": location.get("country"),
            "admin1": location.get("admin1"),
        }

    except requests.RequestException as error:
        print("Location API Error:", error)
        return None


def get_weather_by_location(location_name):
    location = get_location_coordinates(location_name)

    if not location:
        return None

    weather = get_weather(
        location["latitude"],
        location["longitude"]
    )

    if not weather:
        return None

    return {
        "location": location,
        "weather": weather
    }