#os.environ["OPENAI_API_KEY"] = st.secrets['IS883-OpenAIKey-RV']
#os.environ["SERPER_API_KEY"] = st.secrets["SerperAPIKey"]

#my_secret_key = st.secrets['MyOpenAIKey']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#os.environ["OPENAI_API_KEY"] = my_secret_key

#my_secret_key = st.secrets['IS883-OpenAIKey-RV']
#openai.api_key = my_secret_key

# Display Outputs
st.success("✅ Your travel details are ready!")

# Collapsible boxes for results
with st.expander("✈️ Flight Prices", expanded=False):
    st.write(flight_prices)

with st.expander("📋 Itinerary", expanded=False):
    # Assume itinerary content is a string and split it into lines
    lines = itinerary.split('\n')
    
    # Separate day-wise plans and other content
    day_wise_plans = [line for line in lines if line.lower().startswith('day ')]
    other_content = [line for line in lines if line not in day_wise_plans]
    
    # Display other content as is
    for line in other_content:
        st.write(line)
    
    # Split day-wise plans into two columns
    if day_wise_plans:
        st.write("### Day-wise Plans")
        col1, col2 = st.columns(2)
        with col1:
            for i, line in enumerate(day_wise_plans):
                if i % 2 == 0:  # Even index -> Column 1
                    st.write(line)
        with col2:
            for i, line in enumerate(day_wise_plans):
                if i % 2 != 0:  # Odd index -> Column 2
                    st.write(line)
