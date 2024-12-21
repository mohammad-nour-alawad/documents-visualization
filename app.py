# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import base64
import io

from utils import process_text, quality_estimation, client, DEFAULT_GEN_KWARGS
from visualization import interactive_timeline, interactive_relationships

# Additional imports for file processing
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract

# Function to extract text from different file types
def extract_text(file):
    filename = file.name
    file_extension = filename.split('.')[-1].lower()
    
    try:
        if file_extension == 'txt':
            return file.read().decode('utf-8')
        
        elif file_extension == 'pdf':
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text
        
        elif file_extension in ['doc', 'docx']:
            doc = Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        
        elif file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif']:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
            return text
        
        else:
            st.warning(f"Unsupported file type: {file_extension}")
            return ""
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return ""

# Function to generate download link for text
def to_text_download_link(text, filename="extracted_text.txt"):
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Extracted Text</a>'
    return href

st.set_page_config(page_title="Visualize Your Docs", page_icon="📜", layout="wide")

st.title("📜 Visualize Your Docs")
st.write("This assistant helps you identify important dates and persons from historical documents and visualize events and relationships.")

with st.sidebar:
    st.write("## Instructions")
    st.write("""
    1. **Upload** your document (supports TXT, PDF, DOCX, and Images).
    2. **Extract** the text from the uploaded document.
    3. **Process** the extracted text to identify dates, persons, and relationships.
    4. **Visualize** the extracted information.
    5. **Download** the extracted data as CSV files.
    """)

# File uploader
uploaded_file = st.file_uploader("Upload a document", type=['txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif'])

# Initialize default text
default_text = """On April 19, 1775, the Battles of Lexington and Concord marked the beginning of the American Revolutionary War.
George Washington was appointed as the Commander-in-Chief of the Continental Army by the Second Continental Congress in June 1775.
In 1781, the Siege of Yorktown led to the surrender of British General Charles Cornwallis, effectively ending the war.
Thomas Jefferson drafted the Declaration of Independence, which was adopted on July 4, 1776.
Benjamin Franklin played a crucial role in securing French support for the American cause.
"""

# Initialize session state for extracted text
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = default_text

if uploaded_file is not None:
    with st.spinner("Extracting text from the uploaded document..."):
        extracted_text = extract_text(uploaded_file)
        if extracted_text:
            st.session_state.extracted_text = extracted_text
            st.success("Text extraction complete!")
            st.markdown(to_text_download_link(extracted_text, "extracted_text.txt"), unsafe_allow_html=True)
        else:
            st.warning("No text extracted from the uploaded document.")

# Text input area displaying extracted text
input_text = st.text_area("Review and edit the extracted text below:", value=st.session_state.extracted_text, height=300)

if st.button("Process"):
    with st.spinner("Extracting information..."):
        dates_df, persons_df, relationships_df = process_text(input_text, client=client, **DEFAULT_GEN_KWARGS)

        # Quality Estimation
        dates_df, persons_df, relationships_df = quality_estimation(dates_df, persons_df, relationships_df)

        st.success("Extraction complete!")

        # Display DataFrames
        st.write("### Extracted Dates")
        st.dataframe(dates_df)

        st.write("### Extracted Persons")
        st.dataframe(persons_df)

        st.write("### Extracted Relationships")
        st.dataframe(relationships_df)

        # Download buttons
        def to_csv_download_link(df, filename="data.csv"):
            csv_data = df.to_csv(index=False).encode('utf-8')
            return st.download_button(
                label=f"Download {filename}",
                data=csv_data,
                file_name=filename,
                mime='text/csv'
            )

        if not dates_df.empty:
            to_csv_download_link(dates_df, "dates.csv")
        if not persons_df.empty:
            to_csv_download_link(persons_df, "persons.csv")
        if not relationships_df.empty:
            to_csv_download_link(relationships_df, "relationships.csv")

        # Visualizations
        st.write("### Interactive Events Timeline")
        fig_int_timeline = interactive_timeline(dates_df)
        st.plotly_chart(fig_int_timeline, use_container_width=True)

        st.write("### Interactive Relationships")
        fig_int_rel = interactive_relationships(persons_df, relationships_df)
        st.plotly_chart(fig_int_rel, use_container_width=True)
