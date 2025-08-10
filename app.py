from flask import Flask, render_template, request
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

app = Flask(__name__)
geolocator = Nominatim(user_agent="my_time_app")
tf = TimezoneFinder()

def get_city_time(city_name):
    try:
        location = geolocator.geocode(city_name)
        if not location:
            return None
        tz_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not tz_name:
            return None
        tz = pytz.timezone(tz_name)
        utc_now = datetime.utcnow()
        city_time = pytz.utc.localize(utc_now).astimezone(tz)
        return city_time.strftime("%d.%m.%Y, %H:%M:%S")
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    city_time = None
    city_name = None
    error = None
    if request.method == "POST":
        city_name = request.form.get("city")
        city_time = get_city_time(city_name)
        if city_time is None:
            error = f"Sorry, time for city '{city_name}' not found or could not be resolved."
    return render_template("index.html", city_time=city_time, city_name=city_name, error=error)

if __name__ == "__main__":
    app.run(debug=True)
