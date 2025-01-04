import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Helper Functions
def fetch_weather(location):
    """Fetch weather data from wttr.in."""
    try:
        response = requests.get(f"https://wttr.in/{location}?format=j1")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch weather data. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

def fetch_location_coordinates(location):
    """Fetch latitude and longitude using OpenStreetMap's Nominatim."""
    try:
        geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
        response = requests.get(geocode_url)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data["lat"]), float(data["lon"])
        else:
            st.warning(f"Failed to fetch location coordinates for {location}. Please try a different location.")
            return None, None
    except Exception as e:
        st.error(f"Error fetching location coordinates: {e}")
        return None, None

def create_location_map(lat, lon, location_name):
    """Create an interactive map using Folium centered on the given coordinates."""
    try:
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=f"{location_name}").add_to(m)
        return m
    except Exception as e:
        st.error(f"Error creating map: {e}")
        return None

def fetch_images_from_unsplash(location):
    """Fetch a location image from Unsplash Source API."""
    try:
        unsplash_url = f"https://source.unsplash.com/800x400/?{location}"
        return unsplash_url
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return None

# Streamlit App
st.set_page_config(layout="wide", page_title="Weather Explorer (No API Keys)")
st.title("🌍 Weather Explorer (No API Keys Required)")

# Input Location
location = st.text_input("Enter a location (e.g., New York, London):", value="New York")

if st.button("Get Weather"):
    # Fetch weather data
    weather_data = fetch_weather(location)
    if weather_data:
        # Extract weather info
        current_condition = weather_data["current_condition"][0]
        temp = current_condition["temp_C"]
        feels_like = current_condition["FeelsLikeC"]
        weather_desc = current_condition["weatherDesc"][0]["value"]

        # Display weather info
        st.subheader(f"🌤️ Current Weather in {location.capitalize()}")
        st.metric("Temperature", f"{temp}°C")
        st.metric("Feels Like", f"{feels_like}°C")
        st.metric("Condition", weather_desc.capitalize())

        # Fetch location coordinates
        lat, lon = fetch_location_coordinates(location)
        if lat is not None and lon is not None:
            st.subheader("📍 Location Map")
            map_object = create_location_map(lat, lon, location)
            if map_object:
                st_folium(map_object, width=700, height=500)
            else:
                st.warning("Unable to generate map for this location.")
        else:
            st.warning("Could not fetch coordinates for the location.")

        # Fetch and display Unsplash images
        st.subheader("🌄 Location Images")
        image_url = fetch_images_from_unsplash(location)
        if image_url:
            st.image(image_url, caption=f"Beautiful view of {location.capitalize()}", use_container_width=True)
        else:
            st.warning("No images found for this location.")
