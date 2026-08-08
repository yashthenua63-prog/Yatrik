def get_weather_alert(weather_data):

    if not weather_data:
        return {
            "level": "unknown",
            "icon": "❓",
            "title": "Weather Unavailable",
            "message": "Live weather information is currently unavailable.",
            "recommendation": "Please check the weather again before travelling."
        }

    weather = weather_data.get("weather", {})
    current = weather.get("current", {})
    hourly = weather.get("hourly", {})

    temperature = current.get("temperature_2m")
    precipitation = current.get("precipitation", 0)
    weather_code = current.get("weather_code")
    wind_speed = current.get("wind_speed_10m", 0)

    precipitation_probability = 0

    probabilities = hourly.get("precipitation_probability", [])

    if probabilities:
        precipitation_probability = max(probabilities[:6])

    # -----------------------------------------
    # SEVERE WEATHER
    # -----------------------------------------

    severe_codes = {
        95, 96, 99
    }

    if (
        weather_code in severe_codes
        or wind_speed >= 50
        or precipitation_probability >= 90
    ):
        return {
            "level": "danger",
            "icon": "🚨",
            "title": "Severe Weather Alert",
            "message": "Severe weather conditions may affect your travel plans.",
            "recommendation": "Avoid unnecessary travel and check conditions before visiting temples."
        }

    # -----------------------------------------
    # HEAVY RAIN / THUNDERSTORM
    # -----------------------------------------

    if (
        precipitation_probability >= 70
        or precipitation >= 5
        or weather_code in {65, 66, 67, 80, 81, 82}
    ):
        return {
            "level": "warning",
            "icon": "🌧️",
            "title": "Weather Alert",
            "message": "Rain is likely in this area.",
            "recommendation": "Carry an umbrella and plan your temple visit accordingly."
        }

    # -----------------------------------------
    # MODERATE RAIN
    # -----------------------------------------

    if (
        precipitation_probability >= 40
        or precipitation > 0
        or weather_code in {51, 53, 55, 61, 63, 71, 73, 75}
    ):
        return {
            "level": "caution",
            "icon": "🌦️",
            "title": "Weather Caution",
            "message": "There is a chance of rain in the coming hours.",
            "recommendation": "Keep an umbrella with you and monitor the weather."
        }

    # -----------------------------------------
    # VERY HOT
    # -----------------------------------------

    if temperature is not None and temperature >= 40:
        return {
            "level": "warning",
            "icon": "🥵",
            "title": "High Temperature Alert",
            "message": "The temperature is very high.",
            "recommendation": "Avoid travelling during peak afternoon hours and stay hydrated."
        }

    # -----------------------------------------
    # SAFE
    # -----------------------------------------

    return {
        "level": "safe",
        "icon": "☀️",
        "title": "Good Weather for Travel",
        "message": "No major weather disruption is expected.",
        "recommendation": "Good time to explore nearby temples and places."
    }