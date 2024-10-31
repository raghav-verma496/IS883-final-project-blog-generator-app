import streamlit as st
import openai

# Load your API Key
my_secret_key = st.secrets['IS883-OpenAIKey-RV']
openai.api_key = my_secret_key

# Function to get response from GPT-4
def getGPT4response(input_text, no_words, blog_style):
    try:
        # Construct the prompt directly
        prompt = f"Write a blog for a {blog_style} job profile on the topic '{input_text}'. Limit the content to approximately {no_words} words."
        
        # Make a direct API call to OpenAI's GPT-4 model
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract and return the response content
        return response.choices[0].message['content']
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Streamlit UI configuration
st.set_page_config(
    page_title="Generate Blogs",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.header("Generate Blogs 🤖")

# User inputs
input_text = st.text_input("Enter the Blog Topic")

# Two columns for additional fields
col1, col2 = st.columns([5, 5])

with col1:
    no_words = st.text_input("No of Words")
with col2:
    blog_style = st.selectbox("Writing the blog for", ("Researchers", "Data Scientist", "Common People"), index=0)

# Generate blog button
submit = st.button("Generate")

# Display the generated blog content
if submit:
    blog_content = getGPT4response(input_text, no_words, blog_style)
    if blog_content:
        st.write(blog_content)
