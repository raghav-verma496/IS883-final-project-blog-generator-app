import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# Function to get response from GPT-4
def getGPT4response(input_text, no_words, blog_style):
    # Initialize the OpenAI GPT-4 model
    chat = ChatOpenAI(model="gpt-4", temperature=0.7)

    # Prompt template for GPT-4
    template = """
        Write a blog for a {blog_style} job profile on the topic '{input_text}'.
        Limit the content to approximately {no_words} words.
    """
    
    prompt = PromptTemplate(
        input_variables=["blog_style", "input_text", "no_words"],
        template=template
    )

    # Generate response from GPT-4
    response = chat(prompt.format(blog_style=blog_style, input_text=input_text, no_words=no_words))
    return response.content

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
    st.write(blog_content)
