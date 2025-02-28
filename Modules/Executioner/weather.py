import python_weather
import asyncio
import os

class Weather():
    def __init__(self):
        pass
    async def get(self) -> dict:
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get('Chapecó')

            results = {
                'temperature': f"{weather.temperature}°C",
                'daily forecast': f"{weather.daily_forecasts}",
                'feels_like': f"{weather.feels_like}",
                'description': f"{weather.description}",
                'precipitation': f"{weather.precipitation}",
                'humidity': f"{weather.humidity}%",  # Relative humidity if provided
                'wind_speed': f"{weather.wind_speed} km/h",  # If wind speed is separate
                'wind_direction': f"{weather.wind_direction}",  # Direction of the wind
                'observation_time': f"{weather.datetime}",  # Time of the observation/update
                'pressure': f"{weather.pressure}",
                'uv': f"{weather.ultraviolet}"
            }
            return results

