import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from PIL import Image
from io import BytesIO

# API Keys (replace with your keys)
OPENWEATHERMAP_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"  # Get from https://openweathermap.org/api
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"  # Get from https://unsplash.com/developers

# Helper Functions
def fetch_weather(location):
    """Fetch current weather and coordinates from OpenWeatherMap."""
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    try:
        response = requests.get(weather_url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching weather: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching weather: {e}")
        return None

def create_location_map(lat, lon, location_name):
    """Create a map using Folium centered on the given coordinates."""
    m = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker([lat, lon], popup=f"{location_name}").add_to(m)
    return m

def fetch_location_images(location):
    """Fetch location-related images from Unsplash."""
    unsplash_url = f"https://api.unsplash.com/search/photos?query={location}&client_id={UNSPLASH_ACCESS_KEY}&per_page=3"
    try:
        response = requests.get(unsplash_url)
        if response.status_code == 200:
            data = response.json()
            return [img["urls"]["regular"] for img in data["results"]]
        else:
            st.error(f"Error fetching images: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return []

# Streamlit App
st.set_page_config(layout="wide", page_title="Weather Explorer")
st.title("🌍 Weather & Location Explorer")

# Input Location
location = st.text_input("Enter a location (e.g., New York, London):", value="New York")
if st.button("Get Weather"):
    weather_data = fetch_weather(location)
    if weather_data:
        # Extract weather info
        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        weather_desc = weather_data["weather"][0]["description"].capitalize()

        # Display weather info
        st.subheader(f"Current Weather in {location.capitalize()}")
        st.metric("Temperature", f"{temp}°C")
        st.metric("Feels Like", f"{feels_like}°C")
        st.metric("Condition", weather_desc)

        # Show location map
        st.subheader("📍 Location Map")
        map_object = create_location_map(lat, lon, location)
        st_folium(map_object, width=700, height=500)

        # Show location images
        st.subheader("🌄 Images of the Location")
        images = fetch_location_images(location)
        if images:
            for img_url in images:
                st.image(img_url, use_column_width=True)
        else:
            st.warning("No images found for this location.")
