from datetime import datetime
from pydantic import BaseModel
from typing import List

class WeatherDetails(BaseModel):
    forecast_datetime: datetime
    feels_like: int
    humidity: int
    temp: int
    weather: str
    wind_speed: float

class Weather(BaseModel):
    location_name: str
    weather_details: List[WeatherDetails]
