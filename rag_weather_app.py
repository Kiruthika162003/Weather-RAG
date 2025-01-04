import streamlit as st
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import folium
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

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
            return {"error": "Unable to fetch weather data"}
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
            dates.append(datetime.strptime(f"{date} {hour['time']}00", "%Y-%m-%d %H%M"))
            feels_like.append(float(hour["FeelsLikeC"]))
            temp.append(float(hour["tempC"]))
            humidity.append(float(hour["humidity"]))
    return dates, feels_like, temp, humidity

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
    """Create a map for the specified location."""
    geocode_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
    response = requests.get(geocode_url).json()
    if response:
        lat = float(response[0]["lat"])
        lon = float(response[0]["lon"])
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], popup=f"Location: {location}").add_to(m)
        return m
    return None

def fetch_images(query, max_results=3):
    """Fetch relevant images by scraping Bing."""
    url = f"https://www.bing.com/images/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    image_results = []
    for img_tag in soup.find_all("img", limit=max_results):
        src = img_tag.get("src")
        if src and src.startswith("http"):
            image_results.append(src)
    return image_results

# Streamlit App
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
        st.success(f"Showing weather for {location.capitalize()}")

        # Parse and plot time-series data
        dates, feels_like, temp, humidity = parse_forecast(weather)
        st.write("### Forecast for Feels Like Temperature")
        plot_time_series(dates, feels_like, "Feels Like (°C)", "Feels Like Temperature Over Time", color="orange")

        st.write("### Forecast for Humidity")
        plot_time_series(dates, humidity, "Humidity (%)", "Humidity Over Time", color="green")

        # Display location map
        st.write("### Location Map")
        location_map = fetch_location_map(location)
        if location_map:
            st_folium(location_map, width=700, height=500)
        else:
            st.warning("Unable to fetch location map.")

        # Fetch and display weather images
        st.write("### Relevant Weather Images")
        images = fetch_images(f"{location} weather")
        for img_url in images:
            st.image(img_url, caption="Weather Image", use_column_width=True)
