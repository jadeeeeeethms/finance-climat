import streamlit as st
from indicators.waci import show_waci_dashboard

st.set_page_config(page_title="WACI", layout="wide")
show_waci_dashboard()
