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
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from langchain_core.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
import openai
import streamlit as st
import time

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

# Function to create a PDF from itinerary and flight prices
def create_pdf(itinerary, flight_prices):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Styles for the document
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    section_style = styles["Heading2"]
    text_style = styles["BodyText"]

    elements = []

    # Add title
    elements.append(Paragraph("Travel Itinerary", title_style))
    elements.append(Spacer(1, 20))  # Add space

    # Add itinerary section
    elements.append(Paragraph("Itinerary:", section_style))
    for line in itinerary.splitlines():
        elements.append(Paragraph(line, text_style))
    elements.append(Spacer(1, 20))  # Add space

    # Add flight prices section
    elements.append(Paragraph("Flight Prices:", section_style))
    for line in flight_prices.splitlines():
        elements.append(Paragraph(line, text_style))
    elements.append(Spacer(1, 20))  # Add space

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Streamlit UI configuration
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for sky blue background
st.markdown(
    """
    <style>
    body {
        background-color: #e3f2fd;
    }
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

# Store results in session state
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "flight_prices" not in st.session_state:
    st.session_state.flight_prices = None

# Main Content Section
if st.button("📝 Generate Travel Itinerary"):
    if not origin or not destination or len(travel_dates) != 2:
        st.error("⚠️ Please provide all required details: origin, destination, and a valid travel date range.")
    else:
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)  # Simulate loading time
            progress.progress(i + 1)

        with st.spinner("Fetching details..."):
            st.session_state.flight_prices = fetch_flight_prices(origin, destination, travel_dates[0].strftime("%Y-%m-%d"))
            st.session_state.itinerary = generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget)

# Display results only if available
if st.session_state.itinerary and st.session_state.flight_prices:
    st.success("✅ Your travel details are ready!")

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(display_card("Itinerary", st.session_state.itinerary), unsafe_allow_html=True)

    with col2:
        st.markdown(display_card("Flight Prices", st.session_state.flight_prices), unsafe_allow_html=True)

    # Display map links directly on the main page
    st.subheader("📍 Places to Visit with Map Links")
    activities = [
        line.split(":")[1].strip() 
        for line in st.session_state.itinerary.split("\n") 
        if ":" in line and "Activity" in line
    ]
    if activities:
        for activity in activities:
            place_name = extract_place_name(activity)
            if place_name:
                maps_link = generate_maps_link(place_name, destination)
                st.markdown(f"- **{place_name}**: [View on Google Maps]({maps_link})")
    else:
        st.write("No activities could be identified.")

    # Generate and provide download link for PDF
    pdf_buffer = create_pdf(st.session_state.itinerary, st.session_state.flight_prices)
    st.download_button(
        label="📥 Download Itinerary as PDF",
        data=pdf_buffer,
        file_name="travel_itinerary.pdf",
        mime="application/pdf",
    )

import time
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


# Add a section at the bottom for evaluation metrics
if "itinerary" in st.session_state and st.session_state.itinerary:
    st.markdown("### Your itinerary has been generated successfully!")

    # Expander for Evaluation Metrics
    with st.expander("Evaluation Metrics", expanded=False):
        # Initialize variables to store metrics
        execution_times = {}

        # Measure the execution time for fetching flight prices
        start_time = time.time()
        fetch_flight_prices(origin, destination, travel_dates[0].strftime("%Y-%m-%d"))
        end_time = time.time()
        execution_times["Fetch Flight Prices"] = end_time - start_time

        # Measure the execution time for generating an itinerary
        start_time = time.time()
        generate_itinerary_with_chatgpt(origin, destination, travel_dates, interests, budget)
        end_time = time.time()
        execution_times["Generate Itinerary"] = end_time - start_time

        # Display Execution Times
        st.markdown("#### Execution Times (in seconds)")
        for task, exec_time in execution_times.items():
            st.write(f"- **{task}**: {exec_time:.2f} seconds")

        # Reference Itinerary for Evaluation (manually curated or from trusted sources)
        reference_itinerary = """
Trip Itinerary: Boston to Sydney
Travel Dates: December 29, 2024 - January 3, 2025
Budget Level: Low (up to $5,000)

Day 1: December 29, 2024 - Departure from Boston
- Flight:
  - Depart from Boston (BOS) to Sydney (SYD).
  - Estimated Cost: $1,200 USD (around 1,800 AUD).
- Total Expense Day 1: $1,200 USD (1,800 AUD).

Day 2: December 30, 2024 - Arrival in Sydney
- Activity 1: Explore the Sydney Opera House.
  - Description: Iconic architectural marvel and cultural venue.
  - Cost: Free self-guided tour (booked in advance). Guided tours cost around 150 AUD.
  - Expense in Local Currency: 0 AUD (self-guided).
  - Expense in USD: 0 USD.
- Activity 2: Visit the Royal Botanic Garden.
  - Description: Beautiful gardens with stunning views of the Sydney Harbour and the Opera House.
  - Cost: Free entry.
  - Expense in Local Currency: 0 AUD.
  - Expense in USD: 0 USD.

Day 3: December 31, 2024 - Sydney
- Activity 3: Australian Museum.
  - Description: Australia's oldest museum featuring natural history and cultural artifacts.
  - Cost: Ticket price is 15 AUD.
  - Expense in Local Currency: 15 AUD.
  - Expense in USD: 10 USD.
- Activity 4: Explore The Rocks.
  - Description: Historic area with quaint houses, shops, and a market on weekends.
  - Cost: Free to explore.
  - Expense in Local Currency: 0 AUD.
  - Expense in USD: 0 USD.

Day 4: January 1, 2025 - Sydney
- Activity 5: Art Gallery of New South Wales.
  - Description: A major public gallery featuring Australian and international art.
  - Cost: Free entry to the main galleries; special exhibitions may charge around 20 AUD.
  - Expense in Local Currency: 0 AUD (main galleries).
  - Expense in USD: 0 USD.

Day 5: January 2, 2025 - Sydney
- Activity 6: Visit Taronga Zoo.
  - Description: A well-known zoo with a focus on conservation and education.
  - Cost: Ticket price is 49 AUD.
  - Expense in Local Currency: 49 AUD.
  - Expense in USD: 32 USD.

Day 6: January 3, 2025 - Departure from Sydney
- Flight:
  - Depart from Sydney (SYD) back to Boston (BOS).
  - Estimated Cost: Included in the round-trip airfare.

Summary of Expenses:
- Flight (Boston to Sydney): $1,200 USD (1,800 AUD).
- Australian Museum: $10 USD (15 AUD).
- Taronga Zoo: $32 USD (49 AUD).
- Total Expense: $1,242 USD (1,864 AUD).
- Remaining Budget: $5,000 USD - $1,242 USD = $3,758 USD.

Additional Tips:
- Access to transportation such as public transport (Opal card) will cost an additional 50-100 AUD for the duration of your stay.
- Enjoy local eateries for affordable meals; budget around 20-35 AUD per meal.
"""

        # Generate Itinerary for Evaluation (Replace with the output from the app)
        generated_itinerary = st.session_state.itinerary

        # ROUGE Evaluation
        def evaluate_rouge(reference, generated):
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            scores = scorer.score(reference, generated)
            return scores
    
        # BLEU Evaluation
        def evaluate_bleu(reference, generated):
            # Tokenize and split sentences into lists of words
            reference_sentences = [reference.split()]  # BLEU expects a list of references
            generated_sentences = generated.split()  # Tokenize generated text
            smoothing = SmoothingFunction().method1  # Add smoothing to avoid zero scores
            bleu_score = sentence_bleu(reference_sentences, generated_sentences, smoothing_function=smoothing)
            return bleu_score

        # Perform Evaluations
        rouge_scores = evaluate_rouge(reference_itinerary, generated_itinerary)
        bleu_score = evaluate_bleu(reference_itinerary, generated_itinerary)

        # Display ROUGE Scores
        st.markdown("#### ROUGE Scores")
        st.write(f"ROUGE-1 (Unigram Overlap): {rouge_scores['rouge1'].fmeasure:.4f}")
        st.write(f"ROUGE-2 (Bigram Overlap): {rouge_scores['rouge2'].fmeasure:.4f}")
        st.write(f"ROUGE-L (Longest Common Subsequence): {rouge_scores['rougeL'].fmeasure:.4f}")
    
        # Display BLEU Score
        st.markdown("#### BLEU Score")
        st.write(f"BLEU Score: {bleu_score:.4f}")
else:
    st.info("Please generate an itinerary first to view evaluation metrics.")
