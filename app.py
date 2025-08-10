from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz
from tzlocal import get_localzone

app = Flask(__name__)

def get_city_timezone(city):
    """Get the timezone for a given city using Nominatim + worldtimeapi."""
    try:
        # Step 1: Geocode city name to lat/lon
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {"q": city, "format": "json", "limit": 1}
        geo_headers = {"User-Agent": "time-comparison-app"}
        geo_response = requests.get(geo_url, params=geo_params, headers=geo_headers)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            return None, f"City '{city}' not found."

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Step 2: Get timezone from lat/lon
        time_url = f"https://worldtimeapi.org/api/timezone"
        tz_response = requests.get(time_url)
        tz_response.raise_for_status()
        all_timezones = tz_response.json()

        # Find matching timezone by location (simplified - we use nearest guess)
        tz_lookup_url = f"https://worldtimeapi.org/api/ip"
        tz_lookup_response = requests.get(f"https://worldtimeapi.org/api/timezone/Etc/UTC")
        tz_lookup_response.raise_for_status()

        # Better approach: directly query time for given lat/lon using timeapi
        tz_by_latlon = f"https://timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lon}"
        tz_info_response = requests.get(tz_by_latlon)
        if tz_info_response.status_code == 200:
            tz_info = tz_info_response.json()
            return tz_info.get("timeZone"), None
        else:
            return None, "Could not find timezone for location."

    except Exception as e:
        return None, f"Error: {e}"

def get_time_for_timezone(tz_name):
    """Fetch current time for a given timezone using worldtimeapi.org."""
    try:
        url = f"https://worldtimeapi.org/api/timezone/{tz_name}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["datetime"]
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    city_time = None
    local_time = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            tz_name, error = get_city_timezone(city)
            if tz_name:
                # Get city time
                city_time_str = get_time_for_timezone(tz_name)
                if city_time_str:
                    city_time = datetime.fromisoformat(city_time_str.replace("Z", "+00:00"))

                # Get local time (server's time zone)
                local_tz = get_localzone()
                local_time = datetime.now(local_tz)
        else:
            error = "Please enter a city name."

    return render_template("index.html", city_time=city_time, local_time=local_time, error=error)

if __name__ == "__main__":
    app.run(debug=True)
