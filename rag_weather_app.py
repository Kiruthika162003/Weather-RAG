import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

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

def generate_llm_message(df):
    """Generate a weather summary based on the graph data."""
    avg_temp = df["temperature"].mean()
    max_temp = df["temperature"].max()
    min_temp = df["temperature"].min()
    condition = df["condition"].mode()[0]

    message = (
        f"The weather forecast indicates an average temperature of {avg_temp:.1f}°C, "
        f"ranging from a low of {min_temp:.1f}°C to a high of {max_temp:.1f}°C. "
        f"The predominant condition throughout the day is '{condition}'. "
        f"Humidity levels are relatively stable, with hourly variations visible in the graph below. "
        "Be prepared for temperature fluctuations!"
    )
    return message

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
st.set_page_config(layout="wide", page_title="Weather RAG with Insights")
st.title("🌤️ Weather RAG with LLM Insights")

# Input Location
location = st.text_input("Enter a location (e.g., New York, London):", value="New York")

if st.button("Get Weather"):
    weather_data = fetch_weather(location)
    if weather_data:
        st.success(f"Weather data for {location.capitalize()} retrieved successfully!")
        df = parse_forecast_data(weather_data)

        # Display LLM-Generated Summary
        st.subheader("🌍 LLM Weather Insights")
        message = generate_llm_message(df)
        st.write(message)

        # Plot Graphs
        st.subheader("📈 Weather Graphs")
        st.plotly_chart(plot_weather_graph(df), use_container_width=True)
        st.plotly_chart(plot_humidity_graph(df), use_container_width=True)
