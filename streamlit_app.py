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

# Function to get response from GPT-4
def get_gpt4_response(input_text, no_words, blog_style):
    try:
        prompt = f"Write a blog for a {blog_style} job profile on the topic '{input_text}'. Limit the content to approximately {no_words} words."
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to fetch flight prices using Serper.dev
def fetch_flight_prices(origin, destination, departure_date):
    try:
        serper_api_key = st.secrets["SerperAPIKey"]
        headers = {"X-API-KEY": serper_api_key, "Content-Type": "application/json"}
        query = f"flights from {origin} to {destination} on {departure_date}"
        payload = {"q": query}

        response = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
        response.raise_for_status()
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
        image = image.convert("L")  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        
        custom_config = r'--psm 6'  # Assume a block of text
        raw_text = pytesseract.image_to_string(image, config=custom_config)
        
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
st.set_page_config(page_title="Travel Planning Assistant", page_icon="🛫", layout="centered")

st.header("Travel Planning Assistant 🛫")

# Homepage Buttons for Navigation
st.subheader("Choose an option to get started:")
col1, col2 = st.columns(2)

with col1:
    pre_travel = st.button("Pre-travel")

with col2:
    post_travel = st.button("Post-travel")

# Pre-travel Branch
if pre_travel:
    st.header("Plan Your Travel 🗺️")
    origin = st.text_input("Flying From (Origin Airport/City)")
    destination = st.text_input("Flying To (Destination Airport/City)")
    travel_dates = st.date_input("Select your travel dates", [])

    if origin and destination and travel_dates:
        flight_prices = fetch_flight_prices(origin, destination, travel_dates[0].strftime("%Y-%m-%d"))
        st.write("**Estimated Flight Prices:**")
        st.write(flight_prices)

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
elif post_travel:
    st.header("Post-travel: Data Classification and Summary")
    uploaded_file = st.file_uploader("Upload your travel data (Excel file)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.subheader("Data Preview:")
        st.write(df.head())
