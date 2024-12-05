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

# Function to fetch Google Maps links for itinerary activities
def fetch_google_maps_links(activity_list):
    activity_links = []
    for activity in activity_list:
        try:
            query = f"site:maps.google.com {activity}"
            raw_response = serper_tool.func(query)
            if "https://maps.google.com" in raw_response:
                link_start = raw_response.find("https://maps.google.com")
                link_end = raw_response.find(" ", link_start)
                link = raw_response[link_start:link_end].strip()
            else:
                link = "No link found"
            activity_links.append({"activity": activity, "link": link})
        except Exception as e:
            activity_links.append({"activity": activity, "link": f"Error: {e}"})
    return activity_links

# Function to generate itinerary using ChatGPT
def generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget):
    try:
        prompt_template = """
        You are a travel assistant. Create a detailed itinerary for a trip from {origin} to {destination}. 
        The user is interested in {interests}. The budget level is {budget}. 
        The travel dates are {travel_dates}. List activities for each day without links.
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

        # Extract activities from the response
        activity_list = [line.split(". ")[-1] for line in itinerary.split("\n") if line.strip().startswith("•")]

        # Fetch Google Maps links
        activity_links = fetch_google_maps_links(activity_list)

        # Append links to the itinerary
        itinerary_with_links = ""
        for item in activity_links:
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

# Initialize session state variables
if "branch" not in st.session_state:
    st.session_state.branch = None

# Homepage Navigation
if st.session_state.branch is None:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Pre-travel"):
            st.session_state.branch = "Pre-travel"
    with col2:
        if st.button("Post-travel"):
            st.session_state.branch = "Post-travel"

# Pre-travel Branch
if st.session_state.branch == "Pre-travel":
    st.header("Plan Your Travel 🗺️")
    origin = st.text_input("Flying From (Origin Airport/City)")
    destination = st.text_input("Flying To (Destination Airport/City)")
    travel_dates = st.date_input("Select your travel date range", value=[], min_value=None, max_value=None, key="date_range", help="Pick a start and end date.")
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
            # Generate itinerary
            itinerary = generate_itinerary_with_chatgpt(
                origin, destination, travel_dates, interests, budget
            )
            # Display the results
            with st.expander("Itinerary with Google Maps Links", expanded=True):
                st.write(itinerary)

# Post-travel Branch
if st.session_state.branch == "Post-travel":
    st.header("Post-travel: Data Classification and Summary")
    uploaded_file = st.file_uploader("Upload your travel data (Excel file)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.subheader("Data Preview:")
        st.write(df.head())
