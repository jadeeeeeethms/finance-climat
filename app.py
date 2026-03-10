import streamlit as st
from indicators.waci import show_waci_dashboard

st.set_page_config(page_title="Climate Risk Dashboard", layout="wide")

st.title("Climate Risk Dashboard")

indicator = st.sidebar.selectbox(
    "Select indicator",
    ["WACI"]
)

if indicator == "WACI":
    show_waci_dashboard()