import python_weather
import asyncio
import datetime
from datetime import date, timedelta, datetime
import openai
import re
from datetime import date
import calendar

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

async def get_current_weather(location, units=python_weather.IMPERIAL):
    async with python_weather.Client(units) as client:
        weather = await client.get(location)
        return weather.current

async def get_weather_for_day(location, day, units=python_weather.IMPERIAL):
    forecast_results = []
    hourly_results = []
    day = datetime.strptime(day, "%Y-%m-%d").date()
    async with python_weather.Client(units) as client:
        weather = await client.get(location)
        for forecast in weather.forecasts:
            forecast_results.append(forecast)
            for hourly in forecast.hourly:
               hourly_results.append(hourly)
    return forecast_results + hourly_results

async def get_weather_in_x_days(location, days):
    target_day = date.today() + timedelta(days=days)
    return await get_weather_for_day(location, target_day)

async def get_sunrise_sunset(location, units=python_weather.IMPERIAL):
    async with python_weather.Client(units) as client:
        weather = await client.get(location)
        today_forecast = list(weather.forecasts)
        return today_forecast

async def get_wind_info(location):
    current_weather = await get_current_weather(location)
    return current_weather.wind_speed, current_weather.wind_direction

async def get_chance_of_precipitation(location):
    current_weather = await get_current_weather(location)
    return current_weather.precipitation

async def run_functions(function_list):
    results = await asyncio.gather(*function_list)
    return results

def convert_date_strings_to_objects(function_list_str):
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    def replace_date(match):
        date_string = match.group(0)
        date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
        return f"{date_object}"
    function_list_str_with_dates = re.sub(date_pattern, replace_date, function_list_str)
    return function_list_str_with_dates

def raw_weather_agent(prompt):
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You take a user's request about weather and call a function to get the relavent information. \
                    You have access to the following functions: [get_current_weather(location), get_weather_for_day(location, day), \
                 get_sunrise_sunset(location), get_wind_info(location), get_chance_of_precipitation(location)]. \
                    The 'day' argument must be in the format YYYY-MM-DD. \
                    If the user requests metric units, add the argument 'units=None' to the function, this is only applicable to \
                    the 'get_weather' functions. Reply only with a list containing the function and arguemnt. You may call more than one function if necessary." 
                    },
                    {"role":"user", "content": prompt + "User's location: San Mateo. " + "Today's date is: " + str(date.today()) + ". It is: " + str(calendar.day_name[date.today().weekday()])},
                    ] 
        )
    reply_content = completion.choices[0].message.content
    function_list_str_with_dates = convert_date_strings_to_objects(reply_content)
    function_list_clean = eval(function_list_str_with_dates)
    weather = asyncio.run(run_functions(function_list_clean))
    return prompt + ", " + str(weather)

def weather_summary_agent(prompt):
    completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You receive a list. The first element is a user's query about the weather. \
                     The other elements contain weather information that can help answer the question. Respond with a concise \
                     answer that uses the provided context to clearly answer the user's question. Convert 24 hour time to 12 hour time \
                     unless otherwise specified." 
                    },
                    {"role":"user", "content": prompt},
                    ] 
        )
    reply_content = completion.choices[0].message.content
    return reply_content

def weather_agent(prompt):
    query = raw_weather_agent(prompt)
    response = weather_summary_agent(query)
    return response