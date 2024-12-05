#os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
#os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#openai.api_key = my_secret_key

import os
import urllib.parse
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import openai
import streamlit as st

# Load API keys
os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

# Function to generate Google Maps link
def generate_maps_link(place_name, city_name):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    full_query = f"{place_name}, {city_name}"
    return base_url + urllib.parse.quote(full_query)

# Function to clean and extract valid place names
def extract_place_name(activity_line):
    prefixes_to_remove = ["Visit", "Explore", "Rest", "the", "Last-minute Shopping in"]
    for prefix in prefixes_to_remove:
        if activity_line.lower().startswith(prefix.lower()):
            activity_line = activity_line.replace(prefix, "").strip()
    return activity_line

# Initialize the Google Serper API Wrapper
search = GoogleSerperAPIWrapper()
serper_tool = Tool(
    name="GoogleSerper",
    func=search.run,
    description="Useful for when you need to look up some information on the internet.",
)

# Streamlit UI configuration
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS styling
st.markdown(
    """
    <style>
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }
    .st-expander {
        background-color:#f9f9f9;
        border-radius:10px;
        border:1px solid #ddd;
        padding:10px;
    }
    .st-expander-header {
        font-weight:bold;
        color:#2980b9;
    }
    .stButton>button {
        background-color:#2980b9;
        color:white;
        font-size:16px;
        border-radius:5px;
        padding:10px 15px;
    }
    .stButton>button:hover {
        background-color:#1c598a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to display content in cards
def display_card(title, content):
    return f"""
    <div style="background-color:#f9f9f9; padding:10px; border-radius:10px; margin-bottom:10px; border:1px solid #ddd;">
        <h4 style="color:#2980b9;">{title}</h4>
        <p>{content}</p>
    </div>
    """

# App Title
st.title("🌍 Travel Planning Assistant")
st.write("Plan your perfect trip with personalized itineraries and flight suggestions!")

# Sidebar Inputs
with st.sidebar:
    st.header("🛠️ Trip Details")
    origin = st.text_input("Flying From (Origin Airport/City)", placeholder="Enter your departure city/airport")
    destination = st.text_input("Flying To (Destination Airport/City)", placeholder="Enter your destination city/airport")
    travel_dates = st.date_input("📅 Travel Dates", [], help="Select your trip's start and end dates.")
    budget = st.selectbox("💰 Select your budget level", ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"])
    interests = st.multiselect("🎯 Select your interests", ["Beach", "Hiking", "Museums", "Local Food", "Shopping", "Parks", "Cultural Sites", "Nightlife"])

# Main Content
st.header("📋 Results")
if st.button("📝 Generate Travel Itinerary"):
    if not origin or not destination or len(travel_dates) != 2:
        st.error("⚠️ Please provide all required details: origin, destination, and a valid travel date range.")
    else:
        with st.spinner("Fetching details..."):
            flight_prices = "Cheapest fare is $350 USD on Airline X"
            itinerary = """
            Activity 1: Explore Sultanahmet
            Activity 2: Visit Grand Bazaar
            Activity 3: Bosphorus Cruise
            Activity 4: Dinner at Local Restaurant
            """

        st.success("✅ Your travel details are ready!")

        # Create two columns
        col1, col2 = st.columns(2)

        with col1:
            if itinerary:
                st.subheader("🗺️ Itinerary")
                st.markdown(display_card("Itinerary", itinerary), unsafe_allow_html=True)

        with col2:
            if flight_prices:
                st.subheader("✈️ Flight Prices")
                st.markdown(display_card("Flight Prices", flight_prices), unsafe_allow_html=True)

            if itinerary:
                # Extract activities and generate map links
                activities = [
                    line.split(":")[1].strip()
                    for line in itinerary.split("\n")
                    if ":" in line and "Activity" in line
                ]
                if activities:
                    places_content = "\n".join(
                        [
                            f"- {extract_place_name(activity)}: [View on Google Maps]({generate_maps_link(extract_place_name(activity), destination)})"
                            for activity in activities
                        ]
                    )
                    st.subheader("📍 Places to Visit with Map Links")
                    st.markdown(display_card("Places to Visit", places_content), unsafe_allow_html=True)
                else:
                    st.markdown(display_card("Places to Visit", "No activities could be identified."), unsafe_allow_html=True)
