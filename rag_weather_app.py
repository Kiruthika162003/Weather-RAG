import streamlit as st
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
import matplotlib.pyplot as plt

# Initialize SentenceTransformer for local embedding
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Weather API endpoint
WEATHER_API_URL = "https://wttr.in"

# Predefined data for RAG (real-time weather data and custom knowledge base)
knowledge_base = [
    "What is the weather today?",
    "Tell me the weather conditions in different cities.",
    "Explain the difference between sunny and rainy weather.",
    "What are some tips for staying safe during a storm?",
    "How can I plan for extreme weather events?"
]

# Generate embeddings for the knowledge base
knowledge_base_embeddings = embedding_model.encode(knowledge_base)


# Utility Functions
def fetch_weather(location=""):
    """Fetch real-time weather data from wttr.in."""
    try:
        params = {"format": "j1"}
        response = requests.get(f"{WEATHER_API_URL}/{location}", params=params)
        if response.status_code == 200:
            weather_data = response.json()
            current_condition = weather_data["current_condition"][0]
            return current_condition
        else:
            return {"error": "Unable to fetch weather data"}
    except Exception as e:
        return {"error": str(e)}


def find_best_match(query, knowledge_base, embeddings):
    """Find the best matching response from the knowledge base."""
    query_embedding = embedding_model.encode([query])
    distances = np.linalg.norm(embeddings - query_embedding, axis=1)
    best_match_idx = np.argmin(distances)
    return knowledge_base[best_match_idx]


# App Layout
st.title("Real-Time RAG System with Weather Updates")
st.sidebar.header("Navigation")
st.sidebar.write("Use this application to get real-time weather data and answers to weather-related queries!")

# Section 1: Weather Search
st.header("🌦️ Real-Time Weather Updates")
location = st.text_input("Enter a location (e.g., 'New York', 'London', or leave blank for your IP-based location):")
if st.button("Get Weather"):
    weather = fetch_weather(location)
    if "error" in weather:
        st.error(weather["error"])
    else:
        st.success("Current Weather Data:")
        st.write(weather)
        # Visualization Example: Weather Temperature Bar
        plt.bar(["Temp (°C)"], [float(weather["temp_C"])])
        plt.title(f"Temperature in {location if location else 'your location'}")
        st.pyplot(plt)

# Section 2: Knowledge-Based Query
st.header("🤖 Knowledge-Based Query")
query = st.text_input("Ask a weather-related question:")
if st.button("Get Answer"):
    response = find_best_match(query, knowledge_base, knowledge_base_embeddings)
    st.success(f"Answer: {response}")

# Footer
st.write("---")
st.caption("Built using SentenceTransformers and Streamlit.")
