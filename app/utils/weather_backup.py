import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def get_coordinates(location):
    """
    Convert a location name into latitude and longitude.
    Example:
        Vrindavan -> latitude, longitude
        Delhi -> latitude, longitude
        Agra -> latitude, longitude
    """

    params = {
        "name": location,
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

        place = results[0]

        return {
            "name": place.get("name"),
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude"),
            "country": place.get("country"),
            "admin1": place.get("admin1"),
        }

    except requests.RequestException as error:
        print("Geocoding API Error:", error)
        return None


def get_weather(latitude, longitude):
    """
    Get weather using latitude and longitude.
    """

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
            "precipitation"
        ),

        "forecast_days": 3,

        "timezone": "auto",
    }

    try:

        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        print("Weather API Error:", error)

        return None


def get_weather_by_location(location):
    """
    Get weather for any location.

    Example:
        get_weather_by_location("Vrindavan")
        get_weather_by_location("Delhi")
        get_weather_by_location("Agra")
    """

    coordinates = get_coordinates(location)

    if not coordinates:
        return None

    weather = get_weather(
        coordinates["latitude"],
        coordinates["longitude"]
    )

    if not weather:
        return None

    return {
        "location": coordinates,
        "weather": weather
    }