from flask import Flask, render_template, request
import requests

app = Flask(__name__)

import requests

def get_city_time(city):
    url = f"https://worldtimeapi.org/api/timezone/{city}"
    try:
        resp = requests.get(url, timeout=5)  # add timeout
        resp.raise_for_status()  # raise error on bad status codes
        data = resp.json()
        return data.get("datetime", "Unknown time")
    except requests.exceptions.RequestException as e:
        # log error if you want, then return friendly message
        print(f"Error fetching time: {e}")
        return "Could not get time"

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
