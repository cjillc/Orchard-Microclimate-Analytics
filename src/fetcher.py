import os
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

CWA_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"


def _parse_float(value, default=None):
    try:
        num = float(value)
        return default if num <= -90 else num
    except (TypeError, ValueError):
        return default


def fetch_realtime_weather(station_id: str) -> dict:
    api_key = os.getenv("CWA_API_KEY", "").strip()
    if not api_key or api_key == "your_cwa_api_key_here":
        return get_fallback_weather(station_id)

    params = {
        "Authorization": api_key,
        "StationId": station_id,
    }

    try:
        response = requests.get(CWA_API_URL, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
        stations = payload.get("records", {}).get("Station", [])
        if not stations:
            return get_fallback_weather(station_id)

        station = stations[0]
        weather = station.get("WeatherElement", {})
        daily_extreme = weather.get("DailyExtreme", {})
        daily_high = daily_extreme.get("DailyHigh", {}).get("TemperatureInfo", {})
        daily_low = daily_extreme.get("DailyLow", {}).get("TemperatureInfo", {})

        air_temp = _parse_float(weather.get("AirTemperature"), 22.0)
        max_temp = _parse_float(daily_high.get("AirTemperature"), air_temp + 4.5)
        min_temp = _parse_float(daily_low.get("AirTemperature"), air_temp - 4.5)
        precipitation = _parse_float(weather.get("Now", {}).get("Precipitation"), 0.0)
        humidity = _parse_float(weather.get("RelativeHumidity"), 75.0)
        obs_time = station.get("ObsTime", {}).get("DateTime", datetime.now().isoformat())

        return {
            "station_id": station.get("StationId", station_id),
            "station_name": station.get("StationName", ""),
            "obs_time": obs_time,
            "air_temp": air_temp,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "daily_rain": precipitation,
            "humidity": humidity,
            "source": "CWA Open Data API (即時觀測)",
        }
    except Exception:
        return get_fallback_weather(station_id)


def get_fallback_weather(station_id: str) -> dict:
    mock_data = {
        "C0F9I0": ("東勢", 23.4, 28.6, 16.2, 42.5, 78.0),
        "C0F9O0": ("新社", 22.5, 27.4, 15.8, 48.0, 81.0),
        "C0F861": ("梨山", 16.2, 22.5, 9.8, 65.0, 84.0),
        "C0F9U0": ("霧峰", 24.1, 29.2, 17.5, 12.0, 70.0),
        "C0E750": ("卓蘭", 23.0, 28.1, 16.0, 39.5, 76.0),
    }
    name, temp, tmax, tmin, rain, rh = mock_data.get(
        station_id, ("東勢", 23.4, 28.6, 16.2, 42.5, 78.0)
    )
    return {
        "station_id": station_id,
        "station_name": name,
        "obs_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "air_temp": temp,
        "max_temp": tmax,
        "min_temp": tmin,
        "daily_rain": rain,
        "humidity": rh,
        "source": "離線測試基準模擬資料 (請於 .env 設定 CWA_API_KEY 啟用即時連線)",
    }