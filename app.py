import streamlit as st
import pandas as pd

# Establish connection to Google Sheets
conn = st.connection("gsheets", type="gspread", url="https://docs.google.com/spreadsheets/d/1hEqvhRM6qnflV_fkqHq5jf2fDXHuDFDZCv53HYPBQeI/edit?gid=0")

# Fetch data from the specified sheet
df = conn.read(worksheet="Sheet1", usecols=[0, 1, 2], ttl=600)

# Display the data in the app
st.title('Veranda Vin Wine List')
st.dataframe(df)
