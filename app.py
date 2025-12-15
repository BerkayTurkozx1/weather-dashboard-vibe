import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

import plotly.express as px

# --- Constants & Helpers ----------------------------------------------------
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def geocode_city(name, max_results=1):
    params = {"name": name, "count": max_results}
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "results" not in data or not data["results"]:
        return None
    return data["results"][0]  # first match

@st.cache_data(show_spinner=False)
def fetch_weather(lat, lon, timezone="auto", hourly_vars=None):
    if hourly_vars is None:
        hourly_vars = [
            "temperature_2m",
            "relativehumidity_2m",
            "apparent_temperature",
            "windspeed_10m",
            "weathercode",
        ]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": ",".join(hourly_vars),
        "timezone": timezone,
    }
    r = requests.get(WEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def get_current_humidity_from_hourly(current_time_str, hourly_df):
    # Parse current time and hourly times as pandas datetimes
    current_time = pd.to_datetime(current_time_str)
    hourly_df = hourly_df.copy()
    hourly_df["time"] = pd.to_datetime(hourly_df["time"])
    # exact match
    match = hourly_df[hourly_df["time"] == current_time]
    if not match.empty and "relativehumidity_2m" in match.columns:
        return float(match.iloc[0]["relativehumidity_2m"])
    # fallback to nearest hour
    hourly_df["diff"] = (hourly_df["time"] - current_time).abs()
    nearest = hourly_df.sort_values("diff").iloc[0]
    if "relativehumidity_2m" in nearest:
        return float(nearest["relativehumidity_2m"])
    return None

# --- Streamlit App ---------------------------------------------------------
st.set_page_config(page_title="Weather App", layout="wide")
st.title("Weather App")

# Initialize search history
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns([3, 1])

with col1:
    city_input = st.text_input("Search city (name or town)", value="", placeholder="e.g. Istanbul")
    search = st.button("Search")

with col2:
    st.write("Search History")
    for i, item in enumerate(reversed(st.session_state.history[-10:])):
        if st.button(item, key=f"hist_{i}"):
            city_input = item
            # emulate search by setting a flag in session_state
            st.session_state._search_from_history = item

# If user pressed history button, set city_input from session state
if "_search_from_history" in st.session_state:
    city_input = st.session_state.pop("_search_from_history")

if search and city_input.strip():
    with st.spinner("Looking up location..."):
        try:
            geo = geocode_city(city_input.strip())
            if not geo:
                st.error("Location not found.")
                st.stop()
        except Exception as e:
            st.error(f"Geocoding failed: {e}")
            st.stop()

    lat = geo["latitude"]
    lon = geo["longitude"]
    name = geo.get("name", city_input.strip())
    country = geo.get("country", "")
    display_name = f"{name}, {country}" if country else name

    # update history
    if display_name not in st.session_state.history:
        st.session_state.history.append(display_name)

    with st.spinner("Fetching weather..."):
        try:
            data = fetch_weather(lat, lon, timezone="auto")
        except Exception as e:
            st.error(f"Weather API error: {e}")
            st.stop()

    # Build hourly DataFrame
    hourly = data.get("hourly", {})
    hourly_df = pd.DataFrame(hourly) if hourly else pd.DataFrame()
    if not hourly_df.empty:
        hourly_df["time"] = pd.to_datetime(hourly_df["time"])

    current = data.get("current_weather", {})
    # Determine humidity by matching current time with hourly data
    humidity = None
    if current and not hourly_df.empty:
        humidity = get_current_humidity_from_hourly(current.get("time"), hourly_df)

    # Display current weather card
    st.subheader(f"Current weather — {display_name}")
    cols = st.columns(4)
    temp_c = current.get("temperature")
    cols[0].metric("Temperature (°C)", f"{temp_c}°" if temp_c is not None else "N/A")
    if humidity is not None:
        cols[1].metric("Humidity (%)", f"{humidity:.0f}%")
    else:
        cols[1].metric("Humidity (%)", "N/A")
    wind = current.get("windspeed")
    cols[2].metric("Wind (km/h)", f"{wind} km/h" if wind is not None else "N/A")
    wcode = current.get("weathercode")
    cols[3].metric("Conditions", WEATHER_CODE_MAP.get(wcode, str(wcode)))

    # Charts: show next 48 hours or all available hourly data
    if not hourly_df.empty:
        # limit to next 48 hours from current time if possible
        if current and "time" in current:
            cur_time = pd.to_datetime(current["time"])
            future_df = hourly_df[hourly_df["time"] >= cur_time].copy()
        else:
            future_df = hourly_df.copy()
        future_df = future_df.reset_index(drop=True)
        # Take up to 48 points
        plot_df = future_df.iloc[:48] if len(future_df) > 48 else future_df

        # Temperature chart
        temp_fig = px.line(plot_df, x="time", y="temperature_2m",
                           labels={"time": "Time", "temperature_2m": "Temperature (°C)"},
                           title="Temperature (next hours)")
        st.plotly_chart(temp_fig, use_container_width=True)

        # Humidity chart
        if "relativehumidity_2m" in plot_df.columns:
            hum_fig = px.line(plot_df, x="time", y="relativehumidity_2m",
                              labels={"time": "Time", "relativehumidity_2m": "Relative Humidity (%)"},
                              title="Relative Humidity (next hours)")
            st.plotly_chart(hum_fig, use_container_width=True)
        else:
            st.info("Hourly humidity data not available for this location.")

    # Option to show raw JSON for debugging
    with st.expander("Raw API response"):
        st.json(data)
else:
    st.info("Enter a city and press Search to get weather data.")