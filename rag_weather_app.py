import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from PIL import Image
from io import BytesIO

# Weather API endpoint
WEATHER_API_URL = "https://wttr.in"

# Helper Functions
def fetch_weather(location):
    """Fetch real-time weather data from wttr.in."""
    try:
        params = {"format": "j1"}
        response = requests.get(f"{WEATHER_API_URL}/{location}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch weather data. HTTP status: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def fetch_location_coordinates(location):
    """Fetch latitude and longitude using OpenCage Geocoding API."""
    api_key = "YOUR_OPENCAGE_API_KEY"  # Replace with your OpenCage API key
    geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    try:
        response = requests.get(geocode_url)
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                coordinates = data["results"][0]["geometry"]
                return coordinates["lat"], coordinates["lng"]
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        st.error(f"Error fetching coordinates: {e}")
        return None, None

def create_location_map(lat, lon, location):
    """Create an interactive map using folium."""
    try:
        m = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], popup=f"Location: {location}").add_to(m)
        return m
    except Exception as e:
        st.error(f"Error creating map: {e}")
        return None

def fetch_images_from_unsplash(location):
    """Fetch images from Unsplash based on location."""
    url = f"https://source.unsplash.com/800x400/?{location}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.url
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return None

# Streamlit App
st.set_page_config(layout="wide", page_title="Weather App with Location & Images 🌦️")
st.title("🌍 Weather & Location Explorer")
st.sidebar.header("Enter a Location")
location = st.sidebar.text_input("Type a city or place (e.g., London, Tokyo):", value="London")

if st.sidebar.button("Get Weather"):
    # Fetch weather data
    weather_data = fetch_weather(location)
    if "error" in weather_data:
        st.error(weather_data["error"])
    else:
        st.success(f"Weather data for {location.capitalize()} loaded successfully!")

        # Fetch location coordinates
        lat, lon = fetch_location_coordinates(location)
        if lat is not None and lon is not None:
            st.subheader(f"📍 Location: {location.capitalize()}")
            
            # Display location map
            map_display = create_location_map(lat, lon, location)
            if map_display:
                st_folium(map_display, width=700, height=500)

            # Fetch and display Unsplash images
            st.subheader("🌄 Images of the Location")
            image_url = fetch_images_from_unsplash(location)
            if image_url:
                st.image(image_url, caption=f"Images of {location.capitalize()}", use_column_width=True)
            else:
                st.warning("Could not load images for this location.")
        else:
            st.warning("Could not find the coordinates for the location.")

        # Display current weather
        current_condition = weather_data["current_condition"][0]
        st.subheader("🌤️ Current Weather")
        st.metric(label="Temperature", value=f"{current_condition['temp_C']}°C")
        st.metric(label="Feels Like", value=f"{current_condition['FeelsLikeC']}°C")
        st.metric(label="Condition", value=current_condition["weatherDesc"][0]["value"])

        # Display forecast for the day
        st.subheader("🌦️ Weather Forecast")
        hourly_forecast = weather_data["weather"][0]["hourly"]
        for hour in hourly_forecast:
            st.write(f"**Time:** {hour['time']} | **Temp:** {hour['tempC']}°C | **Feels Like:** {hour['FeelsLikeC']}°C | **Condition:** {hour['weatherDesc'][0]['value']}")
