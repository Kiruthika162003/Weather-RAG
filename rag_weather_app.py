import streamlit as st
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image
from io import BytesIO

# Weather API endpoint
WEATHER_API_URL = "https://wttr.in"

# Helper Functions
def fetch_weather(location=""):
    """Fetch real-time weather forecast data."""
    try:
        params = {"format": "j1"}
        response = requests.get(f"{WEATHER_API_URL}/{location}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Unable to fetch weather data. HTTP status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def parse_forecast(weather_data):
    """Parse the weather forecast into time-series data."""
    forecast = weather_data["weather"]
    dates, feels_like, temp, humidity = [], [], [], []

    for day in forecast:
        date = day["date"]
        hourly_data = day["hourly"]
        for hour in hourly_data:
            time = hour["time"].zfill(4)  # Ensure it is zero-padded (e.g., '900' -> '0900')
            formatted_time = f"{date} {time[:2]}:{time[2:]}"  # Format as 'YYYY-MM-DD HH:MM'

            try:
                dates.append(datetime.strptime(formatted_time, "%Y-%m-%d %H:%M"))
                feels_like.append(float(hour["FeelsLikeC"]))
                temp.append(float(hour["tempC"]))
                humidity.append(float(hour["humidity"]))
            except ValueError as e:
                st.warning(f"Skipping invalid time entry: {formatted_time}")
                continue

    return dates, feels_like, temp, humidity

def calculate_comparison(feels_like):
    """Compare today's feels-like temperature with the last 3 days."""
    if len(feels_like) < 24:  # Ensure enough data exists
        return None, None, None

    today_avg = sum(feels_like[:8]) / len(feels_like[:8])  # First 8 hours for today
    past_3_days_avg = sum(feels_like[8:]) / len(feels_like[8:])  # Rest for past 3 days
    return today_avg, past_3_days_avg, today_avg - past_3_days_avg

def plot_time_series(dates, values, ylabel, title, color="blue"):
    """Plot a time-series graph."""
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, color=color, marker="o", linestyle="-")
    plt.title(title)
    plt.xlabel("Date & Time")
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(plt)

def fetch_location_map(location):
    """Fetch a map image for the given location using OpenStreetMap."""
    map_url = f"https://www.mapquestapi.com/staticmap/v5/map?key=YOUR_MAPQUEST_API_KEY&center={location}&size=600,400&type=map"
    try:
        response = requests.get(map_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img
        else:
            return None
    except Exception as e:
        return None

def fetch_images(query):
    """Fetch relevant images using a simple fallback Unsplash API."""
    search_url = f"https://source.unsplash.com/600x400/?{query}"
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            return response.url
        else:
            return None
    except Exception:
        return None

# Initialize session state
if "weather_data" not in st.session_state:
    st.session_state["weather_data"] = None
if "location_map" not in st.session_state:
    st.session_state["location_map"] = None

# Streamlit App
st.set_page_config(layout="wide", page_title="Weather Forecast App 🌦️")
st.title("Weather Forecast with Real-Time Data and Images 🌦️")
st.sidebar.header("Navigation")
st.sidebar.write("Use this app to check real-time weather data with forecasts, maps, and relevant images.")

# Section 1: Weather Search
st.header("🌦️ Real-Time Weather Forecast")
location = st.text_input("Enter a location (e.g., 'New York', 'London'):", value="London")
if st.button("Get Weather"):
    weather = fetch_weather(location)
    if "error" in weather:
        st.error(weather["error"])
    else:
        st.session_state["weather_data"] = weather
        st.session_state["location_map"] = fetch_location_map(location)

if st.session_state["weather_data"]:
    weather = st.session_state["weather_data"]
    current_condition = weather["current_condition"][0]
    current_temp = float(current_condition["temp_C"])
    feels_like_now = float(current_condition["FeelsLikeC"])
    st.success(f"Current Temperature: {current_temp}°C | Feels Like: {feels_like_now}°C")

    # Parse and plot time-series data
    dates, feels_like, temp, humidity = parse_forecast(weather)
    today_avg, past_3_days_avg, difference = calculate_comparison(feels_like)

    if today_avg is not None:
        st.write(f"### Comparison: Feels Like Temperature")
        st.write(f"Today's average: {today_avg:.2f}°C")
        st.write(f"Past 3 days' average: {past_3_days_avg:.2f}°C")
        st.write(f"Difference: {difference:+.2f}°C")

    st.write("### Forecast for Feels Like Temperature")
    plot_time_series(dates, feels_like, "Feels Like (°C)", "Feels Like Temperature Over Time", color="orange")

    st.write("### Forecast for Humidity")
    plot_time_series(dates, humidity, "Humidity (%)", "Humidity Over Time", color="green")

    # Display location map
    st.write("### Location Map")
    location_map = st.session_state["location_map"]
    if location_map:
        st.image(location_map, caption=f"Map of {location}", use_column_width=True)
    else:
        st.warning("Unable to fetch location map. Please check your input.")

    # Display weather images
    st.write("### Relevant Weather Images")
    img_url = fetch_images(f"{location} weather")
    if img_url:
        st.image(img_url, caption="Weather Image", use_column_width=True)
    else:
        st.warning("Unable to fetch weather images at this time.")
