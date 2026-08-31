import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
from datetime import datetime

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")


def load_api_key(path: str = "api-key.txt") -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


API_KEY = load_api_key()

ICON_MAP = {
    "01": "☀️", "02": "🌤️", "03": "⛅", "04": "☁️",
    "09": "🌦️", "10": "🌧️", "11": "⛈️", "13": "❄️", "50": "🌫️",
}

# Gradient per weather family, used for the hero banner background
GRADIENTS = {
    "01": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",   # clear
    "02": "linear-gradient(135deg, #56ccf2 0%, #a0d8ef 100%)",   # few clouds
    "03": "linear-gradient(135deg, #757f9a 0%, #d7dde8 100%)",   # scattered clouds
    "04": "linear-gradient(135deg, #636fa4 0%, #e8cbc0 100%)",   # broken clouds
    "09": "linear-gradient(135deg, #4b6cb7 0%, #182848 100%)",   # shower rain
    "10": "linear-gradient(135deg, #3a6073 0%, #16222a 100%)",   # rain
    "11": "linear-gradient(135deg, #232526 0%, #414345 100%)",   # thunderstorm
    "13": "linear-gradient(135deg, #83a4d4 0%, #b6fbff 100%)",   # snow
    "50": "linear-gradient(135deg, #606c88 0%, #3f4c6b 100%)",   # mist
}


def owm_icon(code: str) -> str:
    return ICON_MAP.get(code[:2], "❓")


def gradient_for(code: str) -> str:
    return GRADIENTS.get(code[:2], GRADIENTS["01"])


# ---------- Custom styling ----------

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    .stApp {
        background: #0f1115;
    }

    .block-container {
        padding-top: 1.5rem;
        max-width: 1100px;
    }

    /* Hero banner */
    .hero {
        border-radius: 20px;
        padding: 2.2rem 2.5rem;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }
    .hero .place {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.9;
        margin-bottom: 0.2rem;
    }
    .hero .temp {
        font-size: 4.2rem;
        font-weight: 700;
        line-height: 1.05;
    }
    .hero .desc {
        font-size: 1.3rem;
        font-weight: 500;
        opacity: 0.95;
    }
    .hero .icon {
        font-size: 4.5rem;
    }
    .hero .updated {
        font-size: 0.8rem;
        opacity: 0.75;
        margin-top: 0.6rem;
    }

    /* Glass stat cards */
    .stat-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        text-align: center;
        backdrop-filter: blur(6px);
    }
    .stat-card .label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9aa4b2;
        margin-bottom: 0.35rem;
    }
    .stat-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f0f2f5;
    }

    /* Section headers */
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e6e9ef;
        margin: 1.6rem 0 0.8rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Forecast day cards */
    .day-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1rem 0.5rem;
        text-align: center;
        transition: transform 0.15s ease, background 0.15s ease;
    }
    .day-card:hover {
        background: rgba(255,255,255,0.09);
        transform: translateY(-3px);
    }
    .day-card .dow {
        font-weight: 700;
        color: #f0f2f5;
        margin-bottom: 0.15rem;
    }
    .day-card .emoji {
        font-size: 1.9rem;
        margin: 0.15rem 0;
    }
    .day-card .cond {
        font-size: 0.72rem;
        color: #9aa4b2;
        min-height: 2.1em;
        margin-bottom: 0.4rem;
    }
    .day-card .hi {
        color: #f0f2f5;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .day-card .lo {
        color: #9aa4b2;
        font-size: 0.9rem;
    }
    .day-card .pop {
        color: #6cb6ff;
        font-size: 0.75rem;
        margin-top: 0.3rem;
    }

    footer.custom-footer {
        text-align: center;
        color: #6b7280;
        font-size: 0.8rem;
        margin-top: 2.5rem;
        padding-bottom: 1rem;
    }

    section[data-testid="stSidebar"] {
        background: #14161c;
    }

    /* Map card wrapper */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.03);
        padding: 0.4rem 0.4rem 0.9rem 0.4rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }
    .map-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e6e9ef;
        padding: 0.7rem 0.9rem 0.2rem 0.9rem;
    }
    .map-subtitle {
        font-size: 0.82rem;
        color: #9aa4b2;
        padding: 0 0.9rem 0.6rem 0.9rem;
    }
    .legend-row {
        display: flex;
        gap: 1.2rem;
        flex-wrap: wrap;
        padding: 0.6rem 0.9rem 0.2rem 0.9rem;
        font-size: 0.78rem;
        color: #9aa4b2;
    }
    .legend-chip {
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ---------- API calls ----------

@st.cache_data(ttl=600)
def geocode(city_name: str):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city_name, "limit": 5, "appid": API_KEY}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=600)
def get_current(lat: float, lon: float, unit: str):
    units = "imperial" if unit == "°F" else "metric"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": units}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=600)
def get_forecast(lat: float, lon: float, unit: str):
    """5-day / 3-hour forecast (free tier)."""
    units = "imperial" if unit == "°F" else "metric"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": units}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


# ---------- Sidebar ----------

st.sidebar.markdown("## 🌤️ Weather Dashboard")
st.sidebar.caption("Powered by OpenWeatherMap")
st.sidebar.divider()

if not API_KEY:
    st.sidebar.error("No API key found. Add your key to api-key.txt")

city_input = st.sidebar.text_input("City", value="Rawalpindi", placeholder="e.g. London")
unit = st.sidebar.radio("Temperature unit", ["°C", "°F"], horizontal=True)
search = st.sidebar.button("🔍 Search", use_container_width=True, type="primary")

if "selected_place" not in st.session_state:
    st.session_state.selected_place = None

if search or st.session_state.selected_place is None:
    if city_input.strip() and API_KEY:
        try:
            results = geocode(city_input.strip())
        except Exception as e:
            st.sidebar.error(f"Geocoding failed: {e}")
            results = []

        if results:
            options = {
                f"{r['name']}, {r.get('state', '')}, {r['country']}".replace(", ,", ",")
                : r
                for r in results
            }
            choice = st.sidebar.selectbox("Match found", list(options.keys()))
            st.session_state.selected_place = options[choice]
        else:
            st.sidebar.warning("No matching city found. Try a different name.")

place = st.session_state.selected_place

# ---------- Main ----------

if not API_KEY:
    st.title("🌤️ Weather Dashboard")
    st.warning(
        "Add your OpenWeatherMap API key to `api-key.txt` (just the key, "
        "nothing else) to get started."
    )
    st.stop()

# ---------- Rawalpindi 3D map ----------

RAWALPINDI_SPOTS = [
    {"name": "Saddar",          "lat": 33.5980, "lon": 73.0489, "height": 900},
    {"name": "Committee Chowk", "lat": 33.5975, "lon": 73.0428, "height": 1100},
    {"name": "Raja Bazaar",     "lat": 33.6005, "lon": 73.0475, "height": 850},
    {"name": "Satellite Town",  "lat": 33.6255, "lon": 73.0480, "height": 700},
    {"name": "Westridge",       "lat": 33.5730, "lon": 73.0210, "height": 650},
    {"name": "Chaklala Cantt",  "lat": 33.5807, "lon": 73.0951, "height": 800},
    {"name": "Bahria Town",     "lat": 33.5074, "lon": 73.1000, "height": 1200},
    {"name": "Gulzar-e-Quaid",  "lat": 33.6120, "lon": 73.0570, "height": 750},
    {"name": "Rawat",           "lat": 33.4123, "lon": 73.2137, "height": 600},
]


def height_color(h):
    if h < 750:
        return [46, 204, 164, 220]   # teal — lower marker
    elif h < 1000:
        return [79, 172, 254, 220]   # blue — mid marker
    else:
        return [155, 109, 255, 220]  # purple — tall marker


def halo_color(h):
    r, g, b, _ = height_color(h)
    return [r, g, b, 60]


spots_df = pd.DataFrame(RAWALPINDI_SPOTS)
spots_df["color"] = spots_df["height"].apply(height_color)
spots_df["halo"] = spots_df["height"].apply(halo_color)

map_card = st.container(border=True)
with map_card:
    st.markdown('<div class="map-title">🗺️ Rawalpindi in 3D</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="map-subtitle">Click any marker to pull up the current weather for that spot.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="legend-row">
        <div class="legend-chip"><span class="legend-dot" style="background:#2ecca4;"></span>Neighborhood</div>
        <div class="legend-chip"><span class="legend-dot" style="background:#4facfe;"></span>Town</div>
        <div class="legend-chip"><span class="legend-dot" style="background:#9b6dff;"></span>Cantonment / suburb</div>
    </div>
    """, unsafe_allow_html=True)

    halo_layer = pdk.Layer(
        "ScatterplotLayer",
        id="rwp-halo",
        data=spots_df,
        get_position=["lon", "lat"],
        get_radius=600,
        get_fill_color="halo",
        stroked=False,
        pickable=False,
    )

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        id="rwp-points",
        data=spots_df,
        get_position=["lon", "lat"],
        get_radius=230,
        get_fill_color="color",
        get_line_color=[255, 255, 255, 230],
        line_width_min_pixels=2,
        stroked=True,
        pickable=True,
        auto_highlight=True,
    )

    label_layer = pdk.Layer(
        "TextLayer",
        id="rwp-labels",
        data=spots_df,
        get_position=["lon", "lat"],
        get_text="name",
        get_size=14,
        get_color=[240, 242, 245, 230],
        get_pixel_offset=[0, -28],
        billboard=True,
    )

    view_state = pdk.ViewState(
        latitude=33.578,
        longitude=73.05,
        zoom=11.2,
        pitch=45,
        bearing=-15,
    )

    deck = pdk.Deck(
        layers=[halo_layer, point_layer, label_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}\nClick for current weather"},
    )

    map_event = st.pydeck_chart(
        deck,
        on_select="rerun",
        selection_mode="single-object",
        use_container_width=True,
        height=480,
        key="rwp_3d_map",
    )

    selected_spot = None
    if map_event and map_event.selection:
        objects = map_event.selection.get("objects", {})
        picked = objects.get("rwp-points")
        if picked:
            selected_spot = picked[0]

    if selected_spot:
        try:
            spot_weather = get_current(selected_spot["lat"], selected_spot["lon"], unit)
            spot_desc = spot_weather["weather"][0]["description"].title()
            spot_icon = owm_icon(spot_weather["weather"][0]["icon"])

            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.markdown(f"""
            <div class="stat-card">
                <div class="label">📍 {selected_spot['name']}</div>
                <div class="value">{spot_icon} {spot_desc}</div>
            </div>""", unsafe_allow_html=True)
            mc2.markdown(f"""
            <div class="stat-card">
                <div class="label">Temperature</div>
                <div class="value">{spot_weather['main']['temp']}{unit}</div>
            </div>""", unsafe_allow_html=True)
            mc3.markdown(f"""
            <div class="stat-card">
                <div class="label">Feels Like</div>
                <div class="value">{spot_weather['main']['feels_like']}{unit}</div>
            </div>""", unsafe_allow_html=True)
            mc4.markdown(f"""
            <div class="stat-card">
                <div class="label">Humidity</div>
                <div class="value">{spot_weather['main']['humidity']}%</div>
            </div>""", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Could not fetch weather for {selected_spot['name']}: {e}")
    else:
        st.caption("👆 Click any column above to see the weather at that spot in Rawalpindi.")

st.divider()

if not place:
    st.title("🌤️ Weather Dashboard")
    st.info("Enter a city in the sidebar and click **Search** to get started.")
    st.stop()

lat, lon = place["lat"], place["lon"]
label = f"{place['name']}, {place.get('state', '')}, {place['country']}".replace(", ,", ",")

try:
    current = get_current(lat, lon, unit)
    forecast = get_forecast(lat, lon, unit)
except Exception as e:
    st.error(f"Could not fetch weather data: {e}")
    st.stop()

desc = current["weather"][0]["description"].title()
icon_code = current["weather"][0]["icon"]
icon = owm_icon(icon_code)
bg = gradient_for(icon_code)
wind_unit_label = "mph" if unit == "°F" else "m/s"

# --- Hero banner ---
st.markdown(f"""
<div class="hero" style="background:{bg};">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
        <div>
            <div class="place">📍 {label}</div>
            <div class="temp">{current['main']['temp']}{unit}</div>
            <div class="desc">{desc} · feels like {current['main']['feels_like']}{unit}</div>
            <div class="updated">Last updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="icon">{icon}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Stat cards ---
s1, s2, s3, s4 = st.columns(4)
stats = [
    (s1, "Feels Like", f"{current['main']['feels_like']}{unit}"),
    (s2, "Humidity", f"{current['main']['humidity']}%"),
    (s3, "Wind Speed", f"{current['wind']['speed']} {wind_unit_label}"),
    (s4, "Pressure", f"{current['main']['pressure']} hPa"),
]
for col, label_, value in stats:
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="label">{label_}</div>
            <div class="value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Forecast data (3-hour steps, 5 days) ---
rows = []
for item in forecast["list"]:
    rows.append({
        "time": pd.to_datetime(item["dt"], unit="s"),
        "temp": item["main"]["temp"],
        "pop": item.get("pop", 0) * 100,  # probability of precipitation
        "icon": item["weather"][0]["icon"],
        "desc": item["weather"][0]["description"].title(),
    })
fc_df = pd.DataFrame(rows)

# --- Next 24 hours chart ---
st.markdown('<div class="section-title">📈 Next 24 Hours</div>', unsafe_allow_html=True)
next24 = fc_df.head(8).set_index("time")  # 8 x 3-hour steps = 24h

hc1, hc2 = st.columns(2)
with hc1:
    st.caption(f"Temperature ({unit})")
    st.line_chart(next24["temp"], color="#4facfe")
with hc2:
    st.caption("Chance of precipitation (%)")
    st.bar_chart(next24["pop"], color="#6cb6ff")

# --- 5-day forecast (using the midday reading for each day) ---
st.markdown('<div class="section-title">📅 5-Day Forecast</div>', unsafe_allow_html=True)
fc_df["date"] = fc_df["time"].dt.date
daily_summary = (
    fc_df.groupby("date")
    .agg(temp_max=("temp", "max"), temp_min=("temp", "min"), pop_max=("pop", "max"))
    .reset_index()
    .head(5)
)
# grab a representative icon/desc per day (closest to midday)
icons_by_day = {}
for date, group in fc_df.groupby("date"):
    group = group.copy()
    group["hour_diff"] = (group["time"].dt.hour - 12).abs()
    best = group.sort_values("hour_diff").iloc[0]
    icons_by_day[date] = (best["icon"], best["desc"])

cols = st.columns(len(daily_summary))
for i, col in enumerate(cols):
    row = daily_summary.iloc[i]
    d_icon, d_desc = icons_by_day[row["date"]]
    with col:
        st.markdown(f"""
        <div class="day-card">
            <div class="dow">{row['date'].strftime('%a')}</div>
            <div class="emoji">{owm_icon(d_icon)}</div>
            <div class="cond">{d_desc}</div>
            <div class="hi">⬆️ {round(row['temp_max'], 1)}{unit}</div>
            <div class="lo">⬇️ {round(row['temp_min'], 1)}{unit}</div>
            <div class="pop">☔ {round(row['pop_max'])}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(
    '<footer class="custom-footer">Data provided by '
    '<a href="https://openweathermap.org" style="color:#6cb6ff;">OpenWeatherMap</a></footer>',
    unsafe_allow_html=True,
)