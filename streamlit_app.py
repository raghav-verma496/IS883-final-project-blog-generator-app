import streamlit as st
import openai
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import pandas as pd
import os

### Load your API Key
my_secret_key = st.secrets['IS883-OpenAIKey-RV']
os.environ["OPENAI_API_KEY"] = my_secret_key

# Function to preprocess image and perform OCR
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
    page_title="Receipt OCR and Expense Classification",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.header("Receipt OCR and Expense Classification 🧾")

# Upload receipt for OCR
uploaded_receipt = st.file_uploader("Upload your receipt image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_receipt is not None:
    # Process the uploaded image
    receipt_image = Image.open(uploaded_receipt)
    st.image(receipt_image, caption="Uploaded Receipt", use_column_width=True)
    
    with st.spinner("Processing and extracting data..."):
        receipt_data = preprocess_and_extract(receipt_image)
        if receipt_data:
            st.subheader("Extracted Data:")
            st.write(f"**Raw Text:** {receipt_data['Raw Text']}")
            st.write(f"**Amount:** {receipt_data['Amount'] if receipt_data['Amount'] else 'Not Found'}")
            st.write(f"**Date:** {receipt_data['Date'] if receipt_data['Date'] else 'Not Found'}")
            st.write(f"**Type:** {receipt_data['Type']}")

            # Provide manual correction interface
            manual_amount = st.text_input("Correct the amount if needed", value=receipt_data["Amount"] or "")
            manual_date = st.text_input("Correct the date if needed", value=receipt_data["Date"] or "")
            manual_type = st.selectbox("Select the category if incorrect", 
                                       ["Food", "Transport", "Accommodation", "Entertainment", "Miscellaneous", "Unknown"], 
                                       index=["Food", "Transport", "Accommodation", "Entertainment", "Miscellaneous", "Unknown"].index(receipt_data["Type"]))

            # Display corrected data
            st.subheader("Final Corrected Data:")
            st.write(f"**Amount:** {manual_amount}")
            st.write(f"**Date:** {manual_date}")
            st.write(f"**Type:** {manual_type}")

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
