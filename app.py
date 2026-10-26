import os
from flask import Flask, render_template, request
from weather_client import WeatherAPIClient, WeatherError

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "local-development-only")
client = WeatherAPIClient()

@app.route("/", methods=["GET", "POST"])
def index():
    weather = error = None
    city = ""
    provider = "open-meteo"
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        provider = request.form.get("provider", "open-meteo").strip().lower()
        if not city:
            error = "Please enter a city name."
        elif len(city) > 100:
            error = "Please enter a city name shorter than 100 characters."
        elif provider not in {"open-meteo", "openweathermap"}:
            error = "Please select a supported weather provider."
        else:
            try:
                weather = client.get_current_weather(city, provider)
            except WeatherError as exc:
                error = str(exc)
            except Exception:
                error = "Something unexpected happened. Please try again."
    return render_template("index.html", weather=weather, error=error, city=city, provider=provider)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False)
