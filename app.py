import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Climate Risk Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# GLOBAL PORTFOLIO UPLOAD
# =========================
st.sidebar.markdown("## Data Ingestion")
uploaded_file = st.sidebar.file_uploader(
    "Upload Portfolio Data (CSV/XLSX)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            try:
                portfolio_df = pd.read_csv(uploaded_file, sep=";")
            except Exception:
                uploaded_file.seek(0)
                portfolio_df = pd.read_csv(uploaded_file)
        else:
            portfolio_df = pd.read_excel(uploaded_file)

        st.session_state["portfolio_df"] = portfolio_df
        st.session_state["portfolio_filename"] = uploaded_file.name
        st.sidebar.success(f"Portfolio loaded: {uploaded_file.name}")

    except Exception as e:
        st.sidebar.error(f"Error while loading file: {e}")

st.title("Climate Risk Dashboard")

st.markdown("""
Welcome to the climate dashboard.

This application presents climate indicators through separate pages.
""")

if "portfolio_df" in st.session_state:
    st.info(f"Current uploaded portfolio: {st.session_state['portfolio_filename']}")
else:
    st.warning("No uploaded portfolio. Default demo datasets will be used.")

# =========================
# INDICATOR CARDS
# =========================
st.markdown("## Available indicators")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
**🌊 Physical Risk**  
Measures exposure to physical climate hazards such as flood risk.
""")

with c2:
    st.markdown("""
**🏭 WACI**  
Weighted Average Carbon Intensity.
""")

with c3:
    st.markdown("""
**🌱 GAR**  
Green Asset Ratio.
""")

with c4:
    st.markdown("""
**🌡️ ITR**  
Implied Temperature Rise.
""")
