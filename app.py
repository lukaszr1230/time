from flask import Flask, render_template, request
from datetime import datetime
import pytz

app = Flask(__name__)

def get_city_time(city_timezone):
    try:
        # Check if the timezone exists in pytz
        tz = pytz.timezone(city_timezone)
    except pytz.UnknownTimeZoneError:
        return "Invalid timezone"

    # Get current UTC time
    utc_now = datetime.utcnow()

    # Localize UTC time to the requested timezone
    city_time = pytz.utc.localize(utc_now).astimezone(tz)

    # Format the time nicely
    return city_time.strftime("%d.%m.%Y, %H:%M:%S")

@app.route("/", methods=["GET", "POST"])
def index():
    city_time = None
    city_name = None
    error = None
    if request.method == "POST":
        city_name = request.form.get("city")
        city_time = get_city_time(city_name)
        if city_time == "Invalid timezone":
            error = "Please enter a valid timezone (e.g. Europe/Berlin)"
            city_time = None
    return render_template("index.html", city_time=city_time, city_name=city_name, error=error)

if __name__ == "__main__":
    app.run(debug=True)
