import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get("city")
    units = request.args.get("units")

    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        'appid' : {API_KEY},
        # the city, and the units (metric or imperial).
        'q': {city}, 
        'units': {units} 

        # See the documentation here: https://openweathermap.org/current

    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    # pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now(),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json ['main']['temp'],
        'humidity': result_json ['main']['humidity'],
        'wind_speed': result_json ['wind']['speed'], 
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!

    params1 = { 
        'appid': {API_KEY}, 
        'q': {city1}, 
        'units': {units}
    }

    params2 = { 
        'appid': {API_KEY}, 
        'q': {city2}, 
        'units': {units}
    }

    result1 = requests.get(API_URL, params=params1).json()
    result2 = requests.get(API_URL, params=params2).json()


    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    city1_info = {
        'date': datetime.now(),
        'city': result1['name'],
        'description': result1['weather'][0]['description'],
        'temp': result1 ['main']['temp'],
        'humidity': result1 ['main']['humidity'],
        'wind_speed': result1 ['wind']['speed'], 
        'sunrise': datetime.fromtimestamp(result1['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result1['sys']['sunset']),
        'units_letter': get_letter_for_units(units),
        'timezone': datetime.fromtimestamp(result1['timezone']),
    }

    city2_info = { 
        'date': datetime.now(),
        'city': result2['name'],
        'description': result2['weather'][0]['description'],
        'temp': result2 ['main']['temp'],
        'humidity': result2['main']['humidity'],
        'wind_speed': result2 ['wind']['speed'], 
        'sunrise': datetime.fromtimestamp(result2['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result2['sys']['sunset']),
        'units_letter': get_letter_for_units(units),
        'timezone': datetime.fromtimestamp(result2['timezone']),
    }

    # temperture difference 
    if city1_info['temp'] > city2_info['temp']: 
        warmer_or_colder = 'warmer'
        temp_difference = round(city1_info['temp'] - city2_info['temp'], 2)
    else: 
        warmer_or_colder = 'colder'
        temp_difference = round(city2_info['temp'] - city1_info['temp'], 2)
    
    # humidity difference 
    if city1_info['humidity'] > city2_info['humidity']: 
        humidity_greater_or_less = 'greater'
        humidity_difference = city1_info['humidity'] - city2_info['humidity'] 
    else: 
        humidity_greater_or_less = 'less'
        humidity_difference = city2_info['humidity'] - city1_info['humidity']

    # wind difference 
    if city1_info['wind_speed'] > city2_info['wind_speed']: 
        wind_greater_or_less = 'greater'
        wind_differece = round(city1_info['wind_speed'] - city2_info['wind_speed'], 2)
    else: 
        wind_greater_or_less = 'less'
        wind_differece = city2_info['wind_speed'] - city1_info['wind_speed']

    # sunset difference
    if city1_info['sunset'] > city2_info['sunset']: 
        sunset_difference =  city1_info['sunset'] - city2_info['sunset']
        sunset_earlier_or_later = 'later'
    else: 
        sunset_difference = city2_info['sunset'] - city1_info['sunset']

        sunset_earlier_or_later = 'earlier'


    context = { 

        'date': datetime.now(),
        'city1': result1['name'], 
        'city2': result2['name'],
        'units_letter': get_letter_for_units(units),
        'warmer_or_colder': warmer_or_colder, 
        'temp_difference': temp_difference, 
        'humidity_greater_or_less': humidity_greater_or_less, 
        'humidity_difference': humidity_difference, 
        'wind_greater_or_less': wind_greater_or_less, 
        'wind_difference': wind_differece, 
        'sunset_earlier_or_later': sunset_earlier_or_later, 
        'sunset_difference': sunset_difference

    }


    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
