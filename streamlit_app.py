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

### Load your API Key
my_secret_key = st.secrets['IS883-OpenAIKey-RV']
os.environ["OPENAI_API_KEY"] = my_secret_key

llm = OpenAI(
    model_name="gpt-4o-mini",  # Replace with a valid OpenAI model
    temperature=0.7,
    openai_api_key=my_secret_key
)

# Function to get response from GPT-4
def get_gpt4_response(input_text, no_words, blog_style):
    try:
        # Construct the prompt
        prompt = f"Write a blog for a {blog_style} job profile on the topic '{input_text}'. Limit the content to approximately {no_words} words."
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Ensure this is a valid model
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to fetch flight prices using Serper.dev
def fetch_flight_prices(origin, destination, departure_date):
    try:
        serper_api_key = st.secrets["SerperAPIKey"]  # Replace with your Serper.dev API key
        headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        query = f"flights from {origin} to {destination} on {departure_date}"
        payload = {"q": query}  # Construct the payload

        # API request
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=payload
        )

        # Debugging: Print the entire response
        print("Full Response from Serper.dev API:")
        print(response.json())  # Prints the full response to help debug issues

        # Raise an error for bad HTTP responses
        response.raise_for_status()

        # Parse and return the relevant snippet from the API response
        data = response.json()
        snippet = data.get("answerBox", {}).get("snippet", "No flight prices found.")
        return snippet
    except requests.exceptions.RequestException as e:
        return f"HTTP Request failed: {e}"
    except ValueError:
        return "Failed to parse the response from the Serper.dev API."

# Function for OCR extraction
def preprocess_and_extract(image):
    try:
        # Convert image to grayscale and sharpen
        image = image.convert("L")  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        
        # OCR with custom configuration
        custom_config = r'--psm 6'  # Assume a block of text
        raw_text = pytesseract.image_to_string(image, config=custom_config)
        
        # Extract details using regex
        amount = re.search(r'(\d+\.\d{2})', raw_text)  # Match amounts like 19.70
        date = re.search(r'\d{2}/\d{2}/\d{4}', raw_text)  # Match dates like MM/DD/YYYY
        type_keywords = ["food", "transport", "accommodation", "entertainment", "miscellaneous"]
        category = next((kw for kw in type_keywords if kw.lower() in raw_text.lower()), "Unknown")
        
        return {
            "Raw Text": raw_text,
            "Amount": float(amount.group(1)) if amount else None,
            "Date": date.group(0) if date else None,
            "Type": category
        }
    except Exception as e:
        st.error(f"Error during OCR processing: {e}")
        return None

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
branch = st.sidebar.radio("Select a branch", ["Generate Blogs", "Plan Your Travel", "Post-travel", "OCR Receipts"])

if branch == "Generate Blogs":
    st.header("Generate Blogs 🛫")

    # User inputs
    input_text = st.text_input("Enter the Blog Topic")
    col1, col2 = st.columns([5, 5])

    with col1:
        no_words = st.text_input("No of Words")
    with col2:
        blog_style = st.selectbox("Writing the blog for", ("Researchers", "Data Scientist", "Common People"), index=0)

    # Generate blog button
    submit = st.button("Generate")

    # Display the generated blog content
    if submit:
        blog_content = get_gpt4_response(input_text, no_words, blog_style)
        if blog_content:
            st.write(blog_content)

# Plan Your Travel Branch
elif branch == "Plan Your Travel":
    st.header("Plan Your Travel 🗺️")

    # User inputs
    origin = st.text_input("Flying From (Origin Airport/City)")
    destination = st.text_input("Flying To (Destination Airport/City)")
    travel_dates = st.date_input("Select your travel dates", [])

    # Fetch flight prices
    if origin and destination and travel_dates:
        flight_prices = fetch_flight_prices(origin, destination, travel_dates[0].strftime("%Y-%m-%d"))
        st.write("**Estimated Flight Prices:**")
        st.write(flight_prices)

    # Dynamic interests dropdown based on the destination
    if destination:
        destination_interests = {
            "New York": ["Statue of Liberty", "Central Park", "Broadway Shows", "Times Square", "Brooklyn Bridge",
                         "Museum of Modern Art", "Empire State Building", "High Line", "Fifth Avenue", "Rockefeller Center"],
            "Paris": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Champs-Élysées", "Montmartre",
                      "Versailles", "Seine River Cruise", "Disneyland Paris", "Arc de Triomphe", "Latin Quarter"],
            "Tokyo": ["Shinjuku Gyoen", "Tokyo Tower", "Akihabara", "Meiji Shrine", "Senso-ji Temple",
                      "Odaiba", "Ginza", "Tsukiji Market", "Harajuku", "Roppongi"],
        }
        top_interests = destination_interests.get(destination.title(), ["Beach", "Hiking", "Museums", "Local Food",
                                                                        "Shopping", "Parks", "Cultural Sites", 
                                                                        "Water Sports", "Music Events", "Nightlife"])
        interests = st.multiselect(
            "Select your interests",
            top_interests + ["Other"],  # Include "Other" option
            default=None
        )
        if "Other" in interests:
            custom_interest = st.text_input("Enter your custom interest(s)")
            if custom_interest:
                interests.append(custom_interest)

    # Budget categories
    budget = st.selectbox(
        "Select your budget level",
        ["Low (up to $5,000)", "Medium ($5,000 to $10,000)", "High ($10,000+)"]
    )

    # Generate itinerary button
    generate_itinerary = st.button("Generate Itinerary")

    if generate_itinerary:
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
elif branch == "Post-travel":
    st.header("Post-travel: Data Classification and Summary")
    uploaded_file = st.file_uploader("Upload your travel data (Excel file)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.subheader("Data Preview:")
        st.write(df.head())
elif branch == "OCR Receipts":
    st.header("OCR Receipts: Extract Data from Receipts")
    uploaded_receipt = st.file_uploader("Upload your receipt image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    if uploaded_receipt:
        receipt_image = Image.open(uploaded_receipt)
        receipt_data = preprocess_and_extract(receipt_image)
        if receipt_data:
            st.subheader("Extracted Data:")
            st.write(receipt_data)
