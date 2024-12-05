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
import re
import urllib.parse

# Load API keys
os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]
os.environ["OPENAI_API_KEY"] = st.secrets["IS883-OpenAIKey-RV"]

# Initialize the Google Serper API Wrapper
search = GoogleSerperAPIWrapper()
serper_tool = Tool(
    name="GoogleSerper",
    func=search.run,
    description="Useful for when you need to look up some information on the internet.",
)

# Function to generate Google Maps link
def generate_maps_link(place_name):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    return base_url + urllib.parse.quote(place_name)

# Function to extract activities with place names from the itinerary
def extract_activities_with_map_links(itinerary_text):
    # Match "Activity Name:" and extract the activity names
    activity_pattern = re.compile(r"Activity Name: (.*?)\n", re.DOTALL)
    activities = activity_pattern.findall(itinerary_text)
    activity_links = [
        {"activity": activity.strip(), "link": generate_maps_link(activity.strip())}
        for activity in activities
    ]
    return activity_links

# Function to generate a detailed itinerary using ChatGPT
def generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget):
    try:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in {interests}. The budget level is {budget}. 
        The travel dates are {travel_dates}. For each activity, include:
        - Activity name
        - Description
        - City and country
        - Latitude and Longitude (if possible)
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
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.header("Travel Planning Assistant 🛫")

# Sidebar Navigation
st.sidebar.title("Navigation")
branch = st.sidebar.radio("Select a branch", ["Plan Your Travel", "Post-travel", "OCR Receipts"])

# Plan Your Travel Branch
if branch == "Plan Your Travel":
    st.header("Plan Your Travel 🗺️")

    # Step 1: Collect basic trip details
    origin = st.text_input("Flying From (Origin Airport/City)")
    destination = st.text_input("Flying To (Destination Airport/City)")
    travel_dates = st.date_input("Select your travel dates", [])
    budget = st.selectbox(
        "Select your budget level",
        ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"]
    )

    # Initialize session state for interests
    if "interests" not in st.session_state:
        st.session_state.interests = []

    # Collect Interests
    if st.button("Set Interests"):
        if not origin or not destination or not travel_dates:
            st.error("Please fill in all required fields to proceed.")
        else:
            st.session_state.interests = st.multiselect(
                "Select your interests",
                ["Cultural Sites", "Local Food", "Museums", "Shopping", "Parks", "Nightlife", "Other"],
                default=st.session_state.interests
            )

    # Generate Itinerary and Map Links
    if st.button("Generate Travel Itinerary"):
        if not st.session_state.interests:
            st.error("Please select at least one interest.")
        else:
            # Generate itinerary
            itinerary = generate_itinerary_with_chatgpt(
                origin, destination, travel_dates, st.session_state.interests, budget
            )
            st.subheader("Generated Itinerary:")
            st.write(itinerary)

            # Extract activities and generate map links
            activities_with_links = extract_activities_with_map_links(itinerary)
            if activities_with_links:
                st.subheader("Places to Visit with Map Links:")
                for item in activities_with_links:
                    st.markdown(f"- **{item['activity']}**: [View on Google Maps]({item['link']})")
            else:
                st.write("No activities could be identified from the itinerary.")

# Post-travel Branch
elif branch == "Post-travel":
    st.header("Post-travel: Data Classification and Summary")
    uploaded_file = st.file_uploader("Upload your travel data (Excel file)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.subheader("Data Preview:")
        st.write(df.head())

# OCR Receipts Branch
elif branch == "OCR Receipts":
    st.header("OCR Receipts: Extract Data from Receipts")
    uploaded_receipt = st.file_uploader("Upload your receipt image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    if uploaded_receipt:
        receipt_image = Image.open(uploaded_receipt)
        receipt_data = preprocess_and_extract(receipt_image)
        if receipt_data:
            st.subheader("Extracted Data:")
            st.write(receipt_data)
