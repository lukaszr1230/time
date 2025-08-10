from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

def get_city_time(city):
    url = f"https://worldtimeapi.org/api/timezone/{city}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            dt_str = data.get("datetime")
            if dt_str:
                # Parse datetime string and format it nicely
                dt = datetime.fromisoformat(dt_str[:-6])  # remove timezone offset for simplicity
                return dt.strftime("%d.%m.%Y, %H:%M:%S")
            else:
                return "Unknown time"
        else:
            return "Could not get time"
    except requests.RequestException as e:
        return f"Error: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    city_time = None
    city_name = None
    if request.method == "POST":
        city_name = request.form.get("city")
        city_time = get_city_time(city_name)
    return render_template("index.html", city_time=city_time, city_name=city_name)

if __name__ == "__main__":
    app.run(debug=True)
