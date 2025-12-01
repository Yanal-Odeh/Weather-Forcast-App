from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Function to get coordinates from city name using geocoding API
def get_coordinates(city):
    try:
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        response = requests.get(geocoding_url)
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            return {
                'latitude': result['latitude'],
                'longitude': result['longitude'],
                'city_name': result['name']
            }
        else:
            return None
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None

# Function to get weather data
def get_weather_data(latitude, longitude):
    try:
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        response = requests.get(weather_url)
        data = response.json()
        
        if 'current_weather' in data:
            return data['current_weather']
        else:
            return None
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return None

@app.route('/weather', methods=['POST'])
def weather():
    data = request.get_json()
    city = data.get('city', '')
    
    if not city:
        return jsonify({'error': 'City name is required'}), 400
    
    # Get coordinates for the city
    coords = get_coordinates(city)
    
    if not coords:
        return jsonify({'error': 'City not found. Please check the spelling.'}), 404
    
    # Get weather data
    weather_data = get_weather_data(coords['latitude'], coords['longitude'])
    
    if not weather_data:
        return jsonify({'error': 'Weather data not available'}), 500
    
    # Return weather information
    response = {
        'city': coords['city_name'],
        'temperature': weather_data['temperature'],
        'windSpeed': weather_data['windspeed'],
        'windDirection': weather_data['winddirection'],
        'time': weather_data['time']
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)