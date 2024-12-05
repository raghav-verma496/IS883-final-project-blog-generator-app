#os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
#os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#openai.api_key = my_secret_key

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

    # Set Interests Button
    if st.button("Set Interests"):
        if not origin or not destination or not travel_dates:
            st.error("Please fill in all required fields to proceed.")
        else:
            # Dynamic interest list based on destination
            possible_interests = [
                "Cultural Sites", "Local Food", "Museums", "Shopping", "Parks", "Nightlife", "Other"
            ]
            selected_interests = st.multiselect(
                "Select your interests",
                possible_interests,
                default=st.session_state.interests  # Retain previously selected interests
            )

            if selected_interests:
                st.session_state.interests = selected_interests
                st.success("Interests set successfully!")
            else:
                st.error("Please select at least one interest.")

    # Display the selected interests
    if st.session_state.interests:
        st.subheader("Your Selected Interests:")
        st.write(", ".join(st.session_state.interests))

    # Generate Itinerary Button
    if st.button("Generate Travel Itinerary"):
        if not st.session_state.interests:
            st.error("Please set your interests first.")
        else:
            st.write("Generating itinerary based on your inputs...")
            # Placeholder for itinerary generation logic
