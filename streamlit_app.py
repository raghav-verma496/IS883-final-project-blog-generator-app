import streamlit as st
import openai
import pandas as pd
import pytesseract
from PIL import Image
import re
from langchain.llms import OpenAI
import os

### Load your API Key
my_secret_key = st.secrets['MyOpenAIKey']
os.environ["OPENAI_API_KEY"] = my_secret_key

llm = OpenAI(
    model_name="gpt-4o-mini",  # Replace with a valid OpenAI model
    temperature=0.7,
    openai_api_key=my_secret_key
)

# OCR Function to extract text from receipts
def extract_receipt_data(image):
    try:
        text = pytesseract.image_to_string(image)
        # Extract possible amount, date, and type using regex
        amount = re.search(r'\$?(\d+\.\d{2})', text)
        date = re.search(r'\d{2}/\d{2}/\d{4}', text)  # Matches dates in MM/DD/YYYY format
        type_keywords = ["food", "transport", "accommodation", "entertainment", "miscellaneous"]
        category = next((kw for kw in type_keywords if kw.lower() in text.lower()), "Unknown")

        return {
            "Text": text,
            "Amount": float(amount.group(1)) if amount else None,
            "Date": date.group(0) if date else None,
            "Type": category
        }
    except Exception as e:
        st.error(f"Error during OCR processing: {e}")
        return None

# Streamlit UI configuration
st.set_page_config(
    page_title="Expense Manager with OCR",
    page_icon="🛫",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.header("Post-travel: Receipt OCR and Data Classification")

# Upload receipt for OCR
uploaded_receipt = st.file_uploader("Upload your receipt image", type=["png", "jpg", "jpeg"])

if uploaded_receipt is not None:
    # Process the uploaded image
    receipt_image = Image.open(uploaded_receipt)
    st.image(receipt_image, caption="Uploaded Receipt", use_column_width=True)

    with st.spinner("Extracting data..."):
        receipt_data = extract_receipt_data(receipt_image)
        if receipt_data:
            st.subheader("Extracted Data:")
            st.write(f"**Raw Text:** {receipt_data['Text']}")
            st.write(f"**Amount:** {receipt_data['Amount']}")
            st.write(f"**Date:** {receipt_data['Date']}")
            st.write(f"**Type:** {receipt_data['Type']}")

            # Ask GPT-4 for classification or further suggestions
            classification_prompt = f"""
            Here is the extracted text from a receipt: {receipt_data['Text']}.
            The amount is {receipt_data['Amount']}, and the date is {receipt_data['Date']}.
            Suggest the most likely category for this expense.
            """
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": classification_prompt}]
                )
                suggested_category = response.choices[0].message["content"].strip()
                st.subheader("AI-Suggested Category:")
                st.write(suggested_category)
            except Exception as e:
                st.error(f"Error in GPT-4 classification: {e}")
        else:
            st.error("Failed to extract data from the uploaded receipt.")

# Allow user to upload travel data (Excel file)
uploaded_file = st.file_uploader("Upload your travel data (Excel file)", type=["xlsx"])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    st.subheader("Data Preview:")
    st.write(df.head())

    # Check if required columns exist
    if 'Description' in df.columns and 'Amount' in df.columns:
        # Function to classify each expense
        def classify_expense(description):
            try:
                prompt = f"Classify the following expense description into categories like 'Food', 'Transport', 'Accommodation', 'Entertainment', 'Miscellaneous':\n\n'{description}'\n\nCategory:"
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message["content"].strip()
            except Exception as e:
                st.error(f"Error in classifying expense: {e}")
                return "Unknown"

        # Apply the classification function to each description
        df['Category'] = df['Description'].apply(classify_expense)

        st.subheader("Classified Data:")
        st.write(df)

        # Generate a summary of expenses
        try:
            total_spent = df['Amount'].sum()
            summary_prompt = f"Provide a quick summary of the travel expenses based on the following data:\n\n{df.to_string()}\n\nSummary:"

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary = response.choices[0].message["content"].strip()

            st.subheader("Summary:")
            st.write(summary)

            st.subheader(f"Total Spent: ${total_spent:.2f}")
        except Exception as e:
            st.error(f"Error in generating summary: {e}")
    else:
        st.error("The uploaded Excel file must contain 'Description' and 'Amount' columns.")
