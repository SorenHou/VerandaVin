import streamlit as st
import pandas as pd

# Function to load data from Google Sheets
@st.cache_data(ttl=600)
def load_data(sheet_url):
    csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url)

# URL of your Google Sheet
sheet_url = "https://docs.google.com/spreadsheets/d/1hEqvhRM6qnflV_fkqHq5jf2fDXHuDFDZCv53HYPBQeI/edit#gid=0"

# Load data
df = load_data(sheet_url)

# Streamlit app layout
st.title("Wine List")

# Display data
st.dataframe(df)
