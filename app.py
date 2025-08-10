from flask import Flask, render_template, request
import requests
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
import socket

app = Flask(__name__)
tf = TimezoneFinder()

def get_user_ip():
    # Try to get user IP from headers (behind proxies)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

def get_timezone_from_ip(ip):
    # Use free IP geolocation API that requires no signup
    # Example: ip-api.com (limited but free, no key required)
    try:
        url = f"http://ip-api.com/json/{ip}"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data['status'] == 'success':
            return data['timezone']
        else:
            return None
    except:
        return None

def get_city_coords(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1,
    }
    headers = {
        "User-Agent": "timezone-comparison-app/1.0 (your_email@example.com)"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            return lat, lon
        else:
            return None
    except Exception as e:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    city = None
    city_time = None
    local_time = None
    time_diff = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")
        if not city:
            error = "Please enter a city name."
        else:
            coords = get_city_coords(city)
            if not coords:
                error = f"Could not find coordinates for city '{city}'."
            else:
                lat, lon = coords
                city_tz_name = tf.timezone_at(lat=lat, lng=lon)
                if not city_tz_name:
                    error = "Could not determine timezone for the city."
                else:
                    city_tz = pytz.timezone(city_tz_name)
                    city_time = datetime.now(city_tz)

                    # Get user local timezone
                    user_ip = get_user_ip()
                    user_tz_name = get_timezone_from_ip(user_ip)
                    if not user_tz_name:
                        user_tz_name = 'UTC'  # fallback
                    user_tz = pytz.timezone(user_tz_name)
                    local_time = datetime.now(user_tz)

                    # Calculate time difference in hours
                    diff = (city_time.utcoffset() - local_time.utcoffset()).total_seconds() / 3600
                    time_diff = diff

    return render_template("index.html", city=city, city_time=city_time, local_time=local_time, time_diff=time_diff, error=error)

if __name__ == "__main__":
    app.run(debug=True)
