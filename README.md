# weather_api
weather api proxy

using [openweathernap](https://openweathermap.org/ ) api

API:

[POST]
```
/content/api/v1/integration/weather
{
    "token", # secret token to use proxy
    "location":"Lviv", # some location (city, country) 
    "date": "20-02-2023", # optional, date for forecast, within next 4 days
}
```