"""Modular client for current weather from Open-Meteo or OpenWeatherMap."""
import os
from dataclasses import dataclass
from typing import Optional
import requests

class WeatherError(Exception):
    """Expected error suitable for display to the user."""

@dataclass
class WeatherReport:
    city: str
    country: str
    temperature_c: float
    humidity_percent: Optional[int]
    wind_kmh: float
    condition: str
    observed_at: str
    provider: str

class WeatherAPIClient:
    GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST = "https://api.open-meteo.com/v1/forecast"
    OPENWEATHER = "https://api.openweathermap.org/data/2.5/weather"
    TIMEOUT = 8

    def __init__(self, session=None):
        self.session = session or requests.Session()

    def get_current_weather(self, city, provider="open-meteo"):
        city = (city or "").strip()
        if not city:
            raise WeatherError("Please enter a city name.")
        if provider == "open-meteo":
            return self._open_meteo(city)
        if provider == "openweathermap":
            return self._openweathermap(city)
        raise WeatherError("Unsupported weather provider.")

    def _json(self, url, params):
        try:
            response = self.session.get(url, params=params, timeout=self.TIMEOUT)
        except requests.Timeout as exc:
            raise WeatherError("The weather service took too long to respond. Please try again.") from exc
        except requests.ConnectionError as exc:
            raise WeatherError("Unable to connect. Check your internet connection and try again.") from exc
        except requests.RequestException as exc:
            raise WeatherError("A network error occurred. Please try again later.") from exc
        if response.status_code == 404:
            raise WeatherError("The city or weather resource was not found. Check the city name.")
        if response.status_code in (401, 403):
            raise WeatherError("The API key is missing, invalid, or not authorized. Check provider configuration.")
        if response.status_code == 429:
            raise WeatherError("The weather service is receiving too many requests. Please wait and try again.")
        if response.status_code >= 500:
            raise WeatherError("The weather service is temporarily unavailable. Please try again later.")
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            raise WeatherError("The weather service rejected the request. Check the city and provider settings.") from exc
        except ValueError as exc:
            raise WeatherError("The weather service returned an unreadable response.") from exc

    def _open_meteo(self, city):
        data = self._json(self.GEOCODING, {"name": city, "count": 1, "language": "en", "format": "json"})
        locations = data.get("results") or []
        if not locations:
            raise WeatherError(f"Couldn't find '{city}'. Check spelling or try a nearby city.")
        loc = locations[0]
        params = {
            "latitude": loc["latitude"], "longitude": loc["longitude"],
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        payload = self._json(self.FORECAST, params)
        current = payload.get("current")
        if not isinstance(current, dict):
            raise WeatherError("Current conditions were not returned. Please try again.")
        try:
            return WeatherReport(
                city=loc.get("name", city), country=loc.get("country", ""),
                temperature_c=float(current["temperature_2m"]),
                humidity_percent=int(current["relative_humidity_2m"]) if current.get("relative_humidity_2m") is not None else None,
                wind_kmh=float(current["wind_speed_10m"]),
                condition=self._condition(int(current["weather_code"])),
                observed_at=str(current.get("time", "Not provided")), provider="Open-Meteo"
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherError("The weather response was missing expected measurements.") from exc

    def _openweathermap(self, city):
        key = os.environ.get("OPENWEATHER_API_KEY", "").strip()
        if not key:
            raise WeatherError("OpenWeatherMap needs an API key. Set OPENWEATHER_API_KEY, or select Open-Meteo which needs no key.")
        data = self._json(self.OPENWEATHER, {"q": city, "appid": key, "units": "metric"})
        try:
            return WeatherReport(
                city=data.get("name", city), country=data.get("sys", {}).get("country", ""),
                temperature_c=float(data["main"]["temp"]),
                humidity_percent=int(data["main"]["humidity"]) if data["main"].get("humidity") is not None else None,
                wind_kmh=float(data["wind"]["speed"]) * 3.6,
                condition=str(data["weather"][0].get("description", "Conditions unavailable")).capitalize(),
                observed_at="Current observation", provider="OpenWeatherMap"
            )
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise WeatherError("The weather response was missing expected measurements.") from exc

    @staticmethod
    def _condition(code):
        if code == 0: return "Clear sky"
        if code in (1, 2, 3): return {1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast"}[code]
        if code in (45, 48): return "Fog"
        if code in (51,53,55,56,57): return "Drizzle"
        if code in (61,63,65,66,67): return "Rain"
        if code in (71,73,75,77): return "Snow"
        if code in (80,81,82): return "Rain showers"
        if code in (85,86): return "Snow showers"
        if code in (95,96,99): return "Thunderstorm"
        return "Conditions unavailable"
