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
def generate_maps_link(place_name):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    return base_url + urllib.parse.quote(place_name)

# Function to clean and extract valid place names
def extract_place_name(activity_line):
    # Remove action words like "Visit", "Explore", "Rest and get acclimatized", etc.
    prefixes_to_remove = ["Visit", "Explore", "Rest", "Last-minute Shopping in"]
    for prefix in prefixes_to_remove:
        if activity_line.startswith(prefix):
            activity_line = activity_line.replace(prefix, "").strip()
    return activity_line

# Initialize the Google Serper API Wrapper
search = GoogleSerperAPIWrapper()
serper_tool = Tool(
    name="GoogleSerper",
    func=search.run,
    description="Useful for when you need to look up some information on the internet.",
)

# Function to generate a detailed itinerary using ChatGPT
def generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget):
    try:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in {interests}. The budget level is {budget}. 
        The travel dates are {travel_dates}. For each activity, include the expected expense in both local currency 
        and USD. Provide a total expense at the end. Include at least 5 places to visit and list them as "Activity 1", "Activity 2", etc.
        """
        prompt = prompt_template.format(
            origin=origin,
            destination=destination,
            interests=", ".join(interests) if interests else "general activities",
            budget=budget,
            travel_dates=travel_dates
        )
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"An error occurred while generating the itinerary: {e}"

# Streamlit UI configuration
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Title
st.title("🌍 Travel Planning Assistant")
st.write("Plan your perfect trip with personalized itineraries and flight suggestions!")

# Input Section
st.markdown("---")
st.header("🛣️ Trip Details")

# Use columns for better alignment
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input(
        "Flying From (Origin Airport/City)",
        placeholder="Enter your departure city/airport"
    )
with col2:
    destination = st.text_input(
        "Flying To (Destination Airport/City)",
        placeholder="Enter your destination city/airport"
    )

# Travel Dates Section
st.subheader("📅 Travel Dates")
travel_dates = st.date_input(
    "Select your travel date range (start and end dates)",
    [],
)

# Preferences Section
st.subheader("🎯 Preferences")
col1, col2 = st.columns(2)
with col1:
    budget = st.selectbox(
        "Select your budget level",
        ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"]
    )
with col2:
    interests = st.multiselect(
        "Select your interests",
        ["Beach", "Hiking", "Museums", "Local Food", "Shopping", "Parks", "Cultural Sites", "Nightlife"]
    )

# Generate Itinerary
st.markdown("---")
if st.button("📝 Generate Travel Itinerary"):
    if not origin or not destination or len(travel_dates) != 2:
        st.error("⚠️ Please provide all required details: origin, destination, and a valid travel date range.")
    else:
        with st.spinner("Fetching details..."):
            itinerary = generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget)

        st.success("✅ Your travel details are ready!")
        with st.expander("📋 Itinerary", expanded=False):
            st.subheader("Generated Itinerary:")
            st.write(itinerary)

            # Extract activities and generate map links
            activities = [
                line.split(":")[1].strip() 
                for line in itinerary.split("\n") 
                if "Activity" in line
            ]
            st.subheader("Places to Visit with Map Links:")
            if activities:
                for activity in activities:
                    place_name = extract_place_name(activity)
                    if place_name:  # Only generate links for valid place names
                        maps_link = generate_maps_link(place_name)
                        st.markdown(f"- **{place_name}**: [View on Google Maps]({maps_link})")
            else:
                st.write("No activities could be identified from the itinerary.")
