import datetime as dt
import json

import requests
from flask import Flask, jsonify, request
from weather_dto import Weather

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

def get_all_weather(location: str) -> dict:
    url = app.config["API_URL"]
    payload = {
        "q":location, 
        "appid":app.config["OPENWEATHER_API_KEY"], 
        "lang":"ua", 
        "units":"metric"
    }
    response = requests.get(url, params=payload)
    return json.loads(response.text)

def map_source(weather: dict, weather_date: dt.date) -> dict:
    filtered_details = [
        weather for weather 
        in weather['list'] 
        if dt.datetime.fromtimestamp(weather['dt']).date()==weather_date
    ]
    mapped_details = [
        {
            "forecast_datetime": weather['dt'],
            "temp":round(weather['main']['temp']),
            "humidity":weather['main']['humidity'],
            "feels_like":round(weather['main']['feels_like']),
            "weather":weather['weather'][0]['description'],
            "wind_speed": weather['wind']['speed']
        } for weather in filtered_details
    ]
    return {
        "location_name": weather['city']['name'],
        "weather_details": mapped_details
    }

def get_forecast(location: str, weather_date: dt.date) -> Weather:
    all_weather = get_all_weather(location)
    weather = Weather.validate(map_source(all_weather, weather_date))
    return weather

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2 Yankin: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/weather",
    methods=["POST"],
)
def weather_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if not (token:=json_data.get("token")):
        raise InvalidUsage("token is required", status_code=400)
    if token != app.config["API_TOKEN"]:
        raise InvalidUsage("wrong API token", status_code=403)

    if not (location:=json_data.get("location")):
        raise InvalidUsage("location is required", status_code=400)
    weather_date = json_data.get("date",dt.datetime.now().strftime("%d-%m-%Y"))
    weather_date = dt.datetime.strptime(weather_date, "%d-%m-%Y").date()
    if (dt.datetime.now().date()+dt.timedelta(days=5))<weather_date or weather_date<dt.datetime.now().date():
        raise InvalidUsage("weather date should be within current day or next 4 days", status_code=400)
    weather = get_forecast(location, weather_date)

    end_dt = dt.datetime.now()

    result = {
        "request_duration": str(end_dt - start_dt),
        "weather": weather.dict(),
    }
    return result