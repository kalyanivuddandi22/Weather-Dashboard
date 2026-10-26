# SkyCast Weather Dashboard — CodeNova Task 4

A real-time browser-based weather dashboard built with Python, Flask, Requests, HTML, and CSS. It fetches current weather from a public API and displays city, temperature, humidity, wind speed, and atmospheric conditions.

## Requirements covered
- Free public API integration: Open-Meteo by default, no API key required.
- Optional OpenWeatherMap provider with credentials read from `OPENWEATHER_API_KEY`.
- Modular API client class (`WeatherAPIClient`) in `weather_client.py`.
- Friendly errors for unknown cities, timeouts, network failures, HTTP errors, missing/invalid API credentials, rate limits, and malformed responses.
- Dependency declaration, configuration guide, and test plan.

## Run on Windows PowerShell
1. Extract the project ZIP.
2. Open PowerShell in the project folder.
3. (Recommended) create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Start the website:
   ```powershell
   python app.py
   ```
6. Open `http://127.0.0.1:5002` in your browser. Keep the PowerShell window open while using it. Press `Ctrl+C` to stop.
7. Search for a city such as `Vijayawada`, `London`, or `Tokyo`; leave Open-Meteo selected.

## Optional OpenWeatherMap API key
Open-Meteo works without credentials. To use OpenWeatherMap, obtain a key from https://openweathermap.org/api and set it in the current PowerShell session:
```powershell
$env:OPENWEATHER_API_KEY = "paste_your_key_here"
python app.py
```
Choose OpenWeatherMap in the site. Never put keys in source files, screenshots, or GitHub. If no key is set, the app shows guidance and can still use Open-Meteo. Optional Flask secret:
```powershell
$env:FLASK_SECRET_KEY = "replace_with_a_long_random_value"
```

## How it works
1. `app.py` validates form input and renders the website.
2. `WeatherAPIClient` searches the Open-Meteo geocoding endpoint for city coordinates.
3. It requests current weather for those coordinates and parses JSON into a `WeatherReport` dataclass.
4. Flask renders human-readable metrics.
5. Expected network/API errors become friendly messages instead of uncaught tracebacks.

## Test checklist
- Successful query: `Vijayawada`.
- Invalid city: `NoSuchCity987654`; expect a not-found message.
- Empty city: expect input validation.
- Missing key: choose OpenWeatherMap without setting `OPENWEATHER_API_KEY`; expect clear guidance.
- Invalid key: set an invalid test value; expect a credential message. Do not share real keys.
- Network failure: temporarily disconnect from the internet, submit a city, then reconnect; expect a connection message.
- Timeout handling is implemented with an 8-second request timeout; reliable timeout testing can use a mocked/controlled test.

## Project structure
```text
weather_dashboard_task4/
├── app.py
├── weather_client.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   └── index.html
└── static/
    └── style.css
```

## Safety and limitations
- The Flask development server is bound to `127.0.0.1`, so this is a local real-time project, not a publicly hosted deployment.
- Live results require internet access and the selected API service to be available.
- Do not commit `.env` files, API keys, or passwords.
- This dashboard is informational and does not replace official severe-weather alerts.

## API services
- Open-Meteo: https://open-meteo.com/
- Open-Meteo geocoding: https://geocoding-api.open-meteo.com/
- OpenWeatherMap: https://openweathermap.org/api
