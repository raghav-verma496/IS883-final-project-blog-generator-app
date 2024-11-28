#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

import streamlit as st
import openai
import pandas as pd
import urllib.parse
import re
import os

# Load your API Key
my_secret_key = st.secrets['IS883-OpenAIKey-RV']
os.environ["OPENAI_API_KEY"] = my_secret_key

# Function to generate Google Maps link
def generate_maps_link(place_name):
    base_url = "https://www.google.com/maps/search/?api=1&query="
    return base_url + urllib.parse.quote(place_name)

# Function to extract activities from the "Activity" section
def extract_activities_from_itinerary(itinerary_text):
    # Find the section starting with "Activity" and extract its contents
    activity_section = re.search(r"(?i)Activity:.*?(?:(?:\n\n)|$)", itinerary_text, re.DOTALL)
    if activity_section:
        activities_text = activity_section.group(0)
        # Extract proper nouns or capitalized place names within the activity section
        places = re.findall(r'\b[A-Z][a-z]*(?: [A-Z][a-z]*)*\b', activities_text)
        return list(set(places))  # Remove duplicates
    return []

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
    
    budget = st.selectbox("Select your budget level", ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"])
    generate_itinerary = st.button("Generate Itinerary")

    if generate_itinerary:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in general activities. The budget level is {budget}. 
        The travel dates are {travel_dates}. For each activity, include the expected expense in both local currency 
        and USD. Provide a total expense at the end. Include at least 5 places to visit and list them under an "Activity" section.
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

            # Extract activities from the "Activity" section
            activities = extract_activities_from_itinerary(itinerary)

            st.subheader("Places to Visit with Map Links:")
            if activities:
                for activity in activities:
                    maps_link = generate_maps_link(activity)
                    st.markdown(f"- **{activity}**: [View on Google Maps]({maps_link})")
            else:
                st.write("No activities could be identified from the itinerary.")

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
