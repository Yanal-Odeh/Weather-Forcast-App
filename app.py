from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Database setup
def init_db():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS city_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT UNIQUE NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Function to check if city is in cache
def get_cached_coordinates(city):
    try:
        conn = sqlite3.connect('weather.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT latitude, longitude, city_name 
            FROM city_cache 
            WHERE LOWER(city_name) = LOWER(?)
        ''', (city,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print(f"Using cached coordinates for {city}")
            return {
                'latitude': result[0],
                'longitude': result[1],
                'city_name': result[2]
            }
        return None
    except Exception as e:
        print(f"Cache lookup error: {e}")
        return None

# Function to save coordinates to cache
def save_to_cache(city_name, latitude, longitude):
    try:
        conn = sqlite3.connect('weather.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO city_cache (city_name, latitude, longitude)
            VALUES (?, ?, ?)
        ''', (city_name, latitude, longitude))
        conn.commit()
        conn.close()
        print(f"Saved {city_name} to cache")
    except Exception as e:
        print(f"Cache save error: {e}")

# Function to get coordinates from city name using geocoding API
def get_coordinates(city):
    # First, check the cache
    cached = get_cached_coordinates(city)
    if cached:
        return cached
    
    # If not in cache, fetch from API
    try:
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        response = requests.get(geocoding_url)
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            coords = {
                'latitude': result['latitude'],
                'longitude': result['longitude'],
                'city_name': result['name']
            }
            # Save to cache for future use
            save_to_cache(coords['city_name'], coords['latitude'], coords['longitude'])
            return coords
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
    
    # Get coordinates for the city (from cache or API)
    coords = get_coordinates(city)
    
    if not coords:
        return jsonify({'error': 'City not found. Please check the spelling.'}), 404
    
    # Get weather data (always fresh from API)
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