#os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
#os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#openai.api_key = my_secret_key

import os
import re
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

# Function to extract specific places/landmarks
def extract_places(itinerary_text):
    place_pattern = r"(?:Visit|Explore|Head to|Take a walk at|Stroll through|Spend time at|Enjoy)\s+([\w\s,'-]+)"
    matches = re.findall(place_pattern, itinerary_text)
    places = [place.strip(" .,") for place in matches if place]
    return places

# Function to fetch Google Maps links for places
def fetch_google_maps_links(place_list):
    place_links = []
    for place in place_list:
        try:
            query = f"site:maps.google.com {place}"
            raw_response = serper_tool.func(query)
            if "https://maps.google.com" in raw_response:
                link_start = raw_response.find("https://maps.google.com")
                link_end = raw_response.find(" ", link_start)
                link = raw_response[link_start:link_end].strip()
            else:
                link = "No link found"
            place_links.append({"activity": place, "link": link})
        except Exception as e:
            place_links.append({"activity": place, "link": f"Error: {e}"})
    return place_links

# Main function to generate itinerary
def generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget):
    try:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in {interests}. The budget level is {budget}. 
        The travel dates are {travel_dates}. List activities for each day with specific landmarks.
        """
        travel_dates_str = f"{travel_dates[0]} to {travel_dates[1]}" if len(travel_dates) == 2 else "unspecified dates"
        prompt = prompt_template.format(
            origin=origin,
            destination=destination,
            interests=", ".join(interests) if interests else "general activities",
            budget=budget,
            travel_dates=travel_dates_str
        )
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        itinerary = response.choices[0].message["content"]

        # Extract specific places/landmarks
        places = extract_places(itinerary)

        # Fetch Google Maps links
        place_links = fetch_google_maps_links(places)

        # Append links to the itinerary
        itinerary_with_links = ""
        for item in place_links:
            itinerary_with_links += f"• {item['activity']}\n  Google Maps: {item['link']}\n"

        return itinerary_with_links
    except Exception as e:
        return f"An error occurred while generating the itinerary: {e}"

# Streamlit UI configuration
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="🛫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.header("Travel Planning Assistant 🛫")

# UI Logic
origin = st.text_input("Flying From (Origin Airport/City)")
destination = st.text_input("Flying To (Destination Airport/City)")
travel_dates = st.date_input("Select your travel date range", value=[], key="date_range")
budget = st.selectbox(
    "Select your budget level",
    ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"]
)
interests = st.multiselect(
    "Select your interests",
    ["Beach", "Hiking", "Museums", "Local Food", "Shopping", "Parks", "Cultural Sites", "Nightlife"]
)

if st.button("Generate Travel Itinerary"):
    if not origin or not destination or len(travel_dates) != 2:
        st.error("Please fill in all required fields (origin, destination, and a valid date range).")
    else:
        itinerary = generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget)
        with st.expander("Itinerary with Google Maps Links", expanded=True):
            st.write(itinerary)
