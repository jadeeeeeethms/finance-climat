import streamlit as st
import pandas as pd

st.set_page_config(page_title="Physical Risk", layout="wide")

st.title("Physical Risk Indicator")

# =========================
# LOAD DATA
# =========================
summary = pd.read_csv("data/physical_risk/dashboard_summary.csv", sep=";")
country = pd.read_csv("data/physical_risk/dashboard_country_indicator.csv", sep=";")
sector = pd.read_csv("data/physical_risk/dashboard_sector_indicator.csv", sep=";")
assets = pd.read_csv("data/physical_risk/dashboard_assets.csv", sep=";")
interpretation = pd.read_csv("data/physical_risk/dashboard_interpretation.csv", sep=";")

summary_dict = dict(zip(summary["metric"], summary["value"]))
interp_dict = dict(zip(interpretation["item"], interpretation["value"]))

# =========================
# HEADER
# =========================
st.subheader("Definition")
st.write(summary_dict.get("indicator_definition", "No definition available."))

st.subheader("Interpretation")
st.info(summary_dict.get("interpretation", "No interpretation available."))

st.subheader("Investment rule")
st.success(summary_dict.get("investment_rule", "No rule available."))

# =========================
# MAIN METRICS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    try:
        st.metric("Portfolio indicator", round(float(summary_dict["portfolio_indicator"]), 6))
    except:
        st.metric("Portfolio indicator", summary_dict.get("portfolio_indicator", "N/A"))

with col2:
    try:
        st.metric("Total value", round(float(summary_dict["total_value"]), 2))
    except:
        st.metric("Total value", summary_dict.get("total_value", "N/A"))

with col3:
    try:
        st.metric("Total risk", round(float(summary_dict["total_risk"]), 2))
    except:
        st.metric("Total risk", summary_dict.get("total_risk", "N/A"))

# =========================
# QUICK DECISION
# =========================
st.subheader("Quick decision help")

col1, col2 = st.columns(2)

with col1:
    st.write("### Best choices to prioritize")
    st.write("**Country:**", summary_dict.get("best_country_to_prioritize", "N/A"))
    st.write("**Sector:**", summary_dict.get("best_sector_to_prioritize", "N/A"))
    st.write("**Asset:**", summary_dict.get("best_asset_to_prioritize", "N/A"))

with col2:
    st.write("### Highest-risk choices to review")
    st.write("**Country:**", summary_dict.get("worst_country_to_avoid", "N/A"))
    st.write("**Sector:**", summary_dict.get("worst_sector_to_avoid", "N/A"))
    st.write("**Asset:**", summary_dict.get("worst_asset_to_avoid", "N/A"))

# =========================
# COUNTRY CHART
# =========================
st.subheader("Risk by country")
st.caption("This chart compares countries. Lower values are better.")

if "country" in country.columns and "indicator" in country.columns:
    country_chart = country.sort_values("indicator", ascending=True).set_index("country")
    st.bar_chart(country_chart["indicator"])
else:
    st.warning("Country file must contain columns: country, indicator")

# =========================
# SECTOR CHART
# =========================
st.subheader("Risk by sector")
st.caption("This chart compares sectors. Lower values are better.")

if "sector" in sector.columns and "indicator" in sector.columns:
    sector_chart = sector.sort_values("indicator", ascending=True).set_index("sector")
    st.bar_chart(sector_chart["indicator"])
else:
    st.warning("Sector file must contain columns: sector, indicator")

# =========================
# ASSETS TABLE
# =========================
st.subheader("Assets")
st.caption("This table helps identify the safest and riskiest assets.")

st.dataframe(assets, use_container_width=True)

# =========================
# EDUCATIONAL GUIDE
# =========================
st.subheader("How to read this dashboard")

for key, value in interp_dict.items():
    nice_key = key.replace("_", " ").capitalize()
    st.write(f"**{nice_key}**: {value}")
