from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

def get_timezone(city):
    # Use geonames API for timezone (free, requires signup, but let's use another free API below)
    # Instead, use http://worldtimeapi.org/api/timezone and filter by city name
    
    # Fetch all timezones and try to find matching city
    # worldtimeapi timezones example: Europe/Warsaw, America/New_York
    
    url = "http://worldtimeapi.org/api/timezone"
    try:
        res = requests.get(url)
        res.raise_for_status()
        timezones = res.json()  # list of timezone strings
        
        # Try to find timezone containing city name (case insensitive)
        city_lower = city.lower()
        matched = [tz for tz in timezones if city_lower in tz.lower()]
        if matched:
            return matched[0]  # return first matched timezone
        
        return None
    except Exception as e:
        print("Error fetching timezones:", e)
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    city_time = None
    error = None
    city = ""
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            timezone_str = get_timezone(city)
            if timezone_str:
                tz = pytz.timezone(timezone_str)
                city_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            else:
                error = "City not found or timezone unavailable."
        else:
            error = "Please enter a city name."
    return render_template("index.html", city_time=city_time, error=error, city=city)

@app.route("/compare-time", methods=["POST"])
def compare_time():
    data = request.json
    city = data.get("city")
    user_time_str = data.get("user_time")  # in ISO format string
    
    timezone_str = get_timezone(city)
    if not timezone_str:
        return jsonify({"error": "City not found or timezone unavailable."})
    
    city_tz = pytz.timezone(timezone_str)
    city_now = datetime.now(city_tz)
    
    try:
        user_time = datetime.fromisoformat(user_time_str)
    except Exception:
        return jsonify({"error": "Invalid user time format."})
    
    # Calculate difference in seconds
    diff_sec = abs((city_now - user_time).total_seconds())
    hours = int(diff_sec // 3600)
    minutes = int((diff_sec % 3600) // 60)
    
    return jsonify({
        "city_time": city_now.strftime("%Y-%m-%d %H:%M:%S"),
        "time_difference": f"{hours} hours, {minutes} minutes"
    })

if __name__ == "__main__":
    app.run(debug=True)
