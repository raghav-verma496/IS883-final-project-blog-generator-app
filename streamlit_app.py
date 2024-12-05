#os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
#os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#openai.api_key = my_secret_key

import os
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import openai
import streamlit as st

# Load API keys
os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

# Initialize the Google Serper API Wrapper
search = GoogleSerperAPIWrapper()
serper_tool = Tool(
    name="GoogleSerper",
    func=search.run,
    description="Useful for when you need to look up some information on the internet.",
)

# Function to query ChatGPT for better formatting
def format_flight_prices_with_chatgpt(raw_response, origin, destination, departure_date):
    try:
        prompt = f"""
        You are a helpful assistant. I received the following raw flight information for a query:
        'Flights from {origin} to {destination} on {departure_date}':
        {raw_response}

        Please clean and reformat this information into a professional, readable format. Use bullet points,
        categories, or a table wherever appropriate to make it easy to understand. Also include key highlights
        like the cheapest fare, airlines, and travel dates. Ensure that any missing or irrelevant text is ignored.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"An error occurred while formatting the response: {e}"

# Function to fetch flight prices and format them with ChatGPT
def fetch_flight_prices(origin, destination, departure_date):
    try:
        query = f"flights from {origin} to {destination} on {departure_date}"
        raw_response = serper_tool.func(query)
        formatted_response = format_flight_prices_with_chatgpt(
            raw_response, origin, destination, departure_date
        )
        return formatted_response
    except Exception as e:
        return f"An error occurred while fetching or formatting flight prices: {e}"

# Function to generate a detailed itinerary using ChatGPT
def generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget):
    try:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in {interests}. The budget level is {budget}. 
        The travel dates are {travel_dates}. For each activity, include the expected expense in both local currency 
        and USD. Provide a total expense at the end.
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

# Function to fetch Google Map links for a given location
def fetch_map_link(location):
    try:
        query = f"{location} site:maps.google.com"
        response = serper_tool.func(query)
        # Extract the first Google Maps link
        for line in response.splitlines():
            if "https://maps.google.com" in line:
                return line.strip()
        return "Map link not found"
    except Exception as e:
        return "Error fetching map link"

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
        background-color: #f9f9f9;
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .st-expander-header {
        font-weight: bold;
        color: #2980b9;
    }
    .stButton>button {
        background-color: #2980b9;
        color: white;
        font-size: 16px;
        border-radius: 5px;
        padding: 10px 15px;
    }
    .stButton>button:hover {
        background-color: #1c598a;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
            flight_prices = fetch_flight_prices(origin, destination, travel_dates[0].strftime("%Y-%m-%d"))
            itinerary = generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget)

        st.success("✅ Your travel details are ready!")
        with st.expander("✈️ Flight Prices", expanded=False):
            st.write(flight_prices)

        with st.expander("📋 Itinerary", expanded=False):
            lines = itinerary.split("\n")
            day_wise_plans = [line for line in lines if line.lower().startswith("day ")]
            other_content = [line for line in lines if line not in day_wise_plans]
            for line in other_content:
                st.write(line)

            if day_wise_plans:
                st.write("### Day-wise Plans")
                for line in day_wise_plans:
                    if ":" in line:
                        parts = line.split(":")
                        day_info = parts[0].strip()
                        details = parts[1].strip()
                        if " in " in details:
                            location = details.split(" in ")[-1].strip()
                            map_link = fetch_map_link(location)
                            st.markdown(f"**{day_info}**")
                            st.markdown(f":round_pushpin: **Location**: [{location}]({map_link})")
                            st.write(details)
