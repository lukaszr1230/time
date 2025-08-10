from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_city_time(city):
    # Use worldtimeapi to get time for the city
    url = f"http://worldtimeapi.org/api/timezone/{city}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("datetime", "Unknown time")
    else:
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
