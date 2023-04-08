# import the module
import python_weather
import asyncio
import os
import datetime
from datetime import date, timedelta


async def get_current_weather(location):
    async with python_weather.Client() as client:
        weather = await client.get(location)
        return weather.current

async def get_weather_for_day(location, day):
    async with python_weather.Client() as client:
        weather = await client.get(location)
        for forecast in weather.forecasts:
            if forecast.date == day:
                return forecast
        return None

async def get_weather_in_days(location, days):
    target_day = date.today() + timedelta(days=days)
    return await get_weather_for_day(location, target_day)

async def get_sunrise_sunset(location):
    async with python_weather.Client() as client:
        weather = await client.get(location)
        today_forecast = weather.forecasts[0]
        return today_forecast.astronomy.sun_rise, today_forecast.astronomy.sun_set

async def get_wind_info(location):
    current_weather = await get_current_weather(location)
    return current_weather.wind_speed, current_weather.wind_direction

async def get_chance_of_precipitation(location):
    current_weather = await get_current_weather(location)
    return current_weather.precipitation

async def main():
    location = "New York"
    current_weather = await get_current_weather(location)
    print(current_weather)

# Run the async main function using asyncio.run()
#asyncio.run(main())


