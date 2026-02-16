"""Weather Search Tool — fetches a 7-day forecast via Open-Meteo (free, no API key)."""

import requests
from langchain_core.tools import tool


@tool
def get_weather_forecast(city: str) -> str:
    """
    Get a 7-day weather forecast for a given city.

    Args:
        city: Name of the city (e.g. 'Paris', 'Goa', 'Tokyo').

    Returns:
        A formatted string with daily temperature, precipitation, and wind speed.
    """
    try:
        # Step 1: Geocode the city name to lat/lon
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_resp = requests.get(geo_url, params={"name": city, "count": 1}, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if not geo_data.get("results"):
            return f"Could not find location data for '{city}'."

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        resolved_name = location.get("name", city)
        country = location.get("country", "")

        # Step 2: Fetch 7-day forecast
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,weathercode",
            "timezone": "auto",
            "forecast_days": 7,
        }
        weather_resp = requests.get(weather_url, params=weather_params, timeout=10)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        daily = weather_data.get("daily", {})
        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("windspeed_10m_max", [])
        codes = daily.get("weathercode", [])

        # Weather code descriptions (WMO standard)
        wmo_descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
        }

        lines = [f"📍 7-Day Weather Forecast for {resolved_name}, {country}\n"]
        for i, date in enumerate(dates):
            code = codes[i] if i < len(codes) else 0
            desc = wmo_descriptions.get(code, "Unknown")
            lines.append(
                f"  {date}: {desc} | "
                f"🌡 {temp_min[i]}°C – {temp_max[i]}°C | "
                f"🌧 Precip: {precip[i]} mm | "
                f"💨 Wind: {wind[i]} km/h"
            )

        return "\n".join(lines)

    except requests.RequestException as e:
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"Unexpected error in weather tool: {e}"


# Export tool list for the agent
weather_tools = [get_weather_forecast]
