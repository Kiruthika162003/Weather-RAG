import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import random
from datetime import datetime, timedelta

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

def parse_forecast_data(weather_data):
    """Parse weather data into a structured DataFrame for graphing."""
    hourly_data = []
    for day in weather_data["weather"]:
        date = day["date"]
        for hour in day["hourly"]:
            time = hour["time"].zfill(4)  # Ensure time is zero-padded
            timestamp = datetime.strptime(f"{date} {time[:2]}:{time[2:]}", "%Y-%m-%d %H:%M")
            hourly_data.append({
                "timestamp": timestamp,
                "temperature": float(hour["tempC"]),
                "feels_like": float(hour["FeelsLikeC"]),
                "humidity": float(hour["humidity"]),
                "condition": hour["weatherDesc"][0]["value"]
            })
    return pd.DataFrame(hourly_data)

def clothing_recommendation(current_temp, current_condition):
    """Provide a clothing recommendation based on temperature and weather condition."""
    if current_condition.lower() in ["rain", "showers", "thunderstorm"]:
        return "Don't forget your raincoat and umbrella!"
    elif current_temp < 10:
        return "It's cold outside. Wear a warm jacket!"
    elif 10 <= current_temp <= 20:
        return "A light jacket or sweater should be enough."
    else:
        return "It's warm enough for summer clothing!"

def get_random_joke():
    """Return a random weather-related joke."""
    jokes = [
        "Why did the woman go outdoors with her purse open? Because she expected some change in the weather!",
        "What’s a tornado’s favorite game? Twister!",
        "What do you call it when it rains chickens and ducks? Fowl weather!",
        "What’s the difference between weather and climate? You can’t weather a tree, but you can climate!"
    ]
    return random.choice(jokes)

def plot_weather_graph(df):
    """Plot interactive graphs for temperature and humidity."""
    fig = px.line(
        df,
        x="timestamp",
        y=["temperature", "feels_like"],
        labels={"value": "Temperature (°C)", "timestamp": "Time"},
        title="Temperature and Feels Like Over Time",
        template="plotly_white"
    )
    fig.update_layout(legend_title_text="Legend")
    return fig

def plot_humidity_graph(df):
    """Plot an interactive graph for humidity."""
    fig = px.line(
        df,
        x="timestamp",
        y="humidity",
        labels={"humidity": "Humidity (%)", "timestamp": "Time"},
        title="Humidity Over Time",
        template="plotly_white"
    )
    fig.update_layout(legend_title_text="Legend")
    return fig

# Streamlit App
st.set_page_config(layout="wide", page_title="Weather Insights with Clothing Advice")
st.title("🌤️ Weather Insights with Clothing Advice")

# Input Location
location = st.text_input("Enter a location (e.g., New York, London):", value="New York")

if st.button("Get Weather"):
    weather_data = fetch_weather(location)
    if weather_data:
        st.success(f"Weather data for {location.capitalize()} retrieved successfully!")

        # Parse data
        df = parse_forecast_data(weather_data)

        # Display Current Weather
        st.subheader(f"🌍 Current Weather in {location.capitalize()}")
        current_condition = weather_data["current_condition"][0]
        current_temp = float(current_condition["temp_C"])
        feels_like = float(current_condition["FeelsLikeC"])
        condition = current_condition["weatherDesc"][0]["value"]
        st.metric("Temperature", f"{current_temp}°C")
        st.metric("Feels Like", f"{feels_like}°C")
        st.metric("Condition", condition.capitalize())

        # Clothing Recommendation
        recommendation = clothing_recommendation(current_temp, condition)
        st.info(f"💡 Clothing Recommendation: {recommendation}")

        # Weather for the Last 3 Days
        st.subheader("📊 Weather Trends (Last 3 Days)")
        st.plotly_chart(plot_weather_graph(df), use_container_width=True)
        st.plotly_chart(plot_humidity_graph(df), use_container_width=True)

        # Random Joke
        st.subheader("😂 A Weather Joke for You")
        joke = get_random_joke()
        st.write(f"_{joke}_")
