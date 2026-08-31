# 🌤️ Weather Dashboard

A simple, interactive weather dashboard built with [Streamlit](https://streamlit.io) and the [OpenWeatherMap API](https://openweathermap.org/api).

Search any city to see current conditions, an hourly forecast for the next 24 hours, and a 5-day outlook.

## Features

- 🔍 City search with geocoding (handles multiple matches, e.g. Springfield, USA)
- 🌡️ Current temperature, "feels like", humidity, and wind speed
- 📈 Hourly temperature and precipitation-probability charts (next 24h)
- 📅 5-day forecast with daily highs/lows and rain chance
- 🔄 Toggle between °C and °F

## Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- [OpenWeatherMap API](https://openweathermap.org/api) — weather & geocoding data
- [pandas](https://pandas.pydata.org) — data handling for charts

## Getting Started

### Prerequisites

- Python 3.9+
- A free API key from [OpenWeatherMap](https://home.openweathermap.org/api_keys)

### Installation

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Add your API key

Create a file named `api-key.txt` in the project root containing just your key:

```
your_openweathermap_api_key_here
```

> ⚠️ `api-key.txt` is listed in `.gitignore` and should never be committed. Newly generated OpenWeatherMap keys can take up to a couple of hours to activate.

### Run locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploying to Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, and `.gitignore` to a **public** GitHub repo (do **not** commit `api-key.txt`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. **Create app** → **Deploy a public app from GitHub** → select this repo/branch → set main file to `app.py`.
4. In **App settings → Secrets**, add:
   ```
   OWM_API_KEY = "your_openweathermap_api_key_here"
   ```
5. Update `app.py` to read the key via `st.secrets["OWM_API_KEY"]` instead of `api-key.txt` (Streamlit Cloud's filesystem is ephemeral, so a local text file won't persist there).
6. Click **Deploy**.

## Project Structure

```
.
├── app.py             # Main Streamlit app
├── requirements.txt   # Python dependencies
├── api-key.txt         # Your API key (gitignored, not committed)
├── .gitignore
└── README.md
```

## License

MIT — feel free to use and modify.
