#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

import streamlit as st
import openai
import pandas as pd
from langchain.llms import OpenAI
import pytesseract
from PIL import Image, ImageFilter
import re
import os
import requests

# Load your API Key
my_secret_key = st.secrets['IS883-OpenAIKey-RV']
os.environ["OPENAI_API_KEY"] = my_secret_key

llm = OpenAI(
    model_name="gpt-4o-mini",  # Replace with a valid OpenAI model
    temperature=0.7,
    openai_api_key=my_secret_key
)

# Function to fetch flight prices using Serper.dev
# def fetch_flight_prices(origin, destination, departure_date):
#     try:
#         serper_api_key = st.secrets["SerperAPIKey"]
#         headers = {"X-API-KEY": serper_api_key, "Content-Type": "application/json"}
#         query = f"flights from {origin} to {destination} on {departure_date}"
#         payload = {"q": query}

#         response = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         snippet = data.get("answerBox", {}).get("snippet", "No flight prices found.")
#         return snippet
#     except requests.exceptions.RequestException as e:
#         return f"HTTP Request failed: {e}"
#     except ValueError:
#         return "Failed to parse the response from the Serper.dev API."

# Initialize session state for navigation if not already set
if "active_branch" not in st.session_state:
    st.session_state.active_branch = None  # None means no branch is active

st.header("Travel Planning Assistant 🛫")
st.subheader("Choose an option to get started:")

# Display buttons only if no branch is active
if st.session_state.active_branch is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Pre-travel", key="pre_travel_btn"):
            st.session_state.active_branch = "Pre-travel"  # Set active branch to Pre-travel

    with col2:
        if st.button("Post-travel", key="post_travel_btn"):
            st.session_state.active_branch = "Post-travel"  # Set active branch to Post-travel

# Pre-travel Branch
if st.session_state.active_branch == "Pre-travel":
    st.header("Plan Your Travel 🗺️")
    origin = st.text_input("Flying From (Origin Airport/City)")
    destination = st.text_input("Flying To (Destination Airport/City)")
    travel_dates = st.date_input("Select your travel dates", [])
    
    # if origin and destination and travel_dates:
    #     flight_prices = fetch_flight_prices(origin, destination, travel_dates[0].strftime("%Y-%m-%d"))
    #     st.write("**Estimated Flight Prices:**")
    #     st.write(flight_prices)

    budget = st.selectbox("Select your budget level", ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"])
    generate_itinerary = st.button("Generate Itinerary")

    if generate_itinerary:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in general activities. The budget level is {budget}. 
        The travel dates are {travel_dates}. For each activity, include the expected expense in both local currency 
        and USD. Provide a total expense at the end.
        """
        prompt = prompt_template.format(origin=origin, destination=destination, budget=budget, travel_dates=travel_dates)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            itinerary = response.choices[0].message["content"]
            st.subheader("Generated Itinerary:")
            st.write(itinerary)
        except Exception as e:
            st.error(f"An error occurred while generating the itinerary: {e}")

# Post-travel Branch
elif st.session_state.active_branch == "Post-travel":
    st.header("Post-travel: Data Classification and Summary")
    uploaded_file = st.file_uploader("Upload your travel data (Excel file)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.subheader("Data Preview:")
        st.write(df.head())

# Add a Back Button
if st.session_state.active_branch is not None:
    if st.button("Back to Home", key="back_btn"):
        st.session_state.active_branch = None  # Reset active branch
