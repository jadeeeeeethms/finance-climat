# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 13:15:00 2026

@author: jadet
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Climate Physical Risk Dashboard", layout="wide")

st.title("Climate Physical Risk Dashboard : Flood")

# =========================
# LOAD DATA
# =========================
assets = pd.read_csv("data/physical_risk/dashboard_assets.csv", sep=";")
country = pd.read_csv("data/physical_risk/dashboard_country_indicator.csv", sep=";")
sector = pd.read_csv("data/physical_risk/dashboard_sector_indicator.csv", sep=";")
summary_raw = pd.read_csv("data/physical_risk/dashboard_summary.csv", sep=";")

summary = summary_raw.set_index("metric")["value"]

total_value = float(summary["total_value"])
total_risk = float(summary["total_risk"])
indicator = float(summary["portfolio_indicator"])

# =========================
# PORTFOLIO SUMMARY
# =========================
st.header("Portfolio Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Value", f"{total_value:,.0f}")
col2.metric("Total Risk", f"{total_risk:,.0f}")
col3.metric("Portfolio Indicator", f"{indicator:.3f}")

# =========================
# SIMPLE INTERPRETATION
# =========================
st.header("Interpretation for a beginner investor")

st.info("""
Lower values mean lower physical climate risk.
If you want a simple rule:
- prioritize countries, sectors and assets with the lowest indicator values,
- review carefully those with the highest values.
""")

# =========================
# ASSETS MAP
# =========================
st.header("Assets Map")

required_map_cols = {"latitude", "longitude", "physical_risk", "hazard", "name"}
if required_map_cols.issubset(assets.columns):
    fig_map = px.scatter_mapbox(
        assets,
        lat="latitude",
        lon="longitude",
        size="physical_risk",
        color="hazard",
        hover_name="name",
        zoom=1,
        height=600
    )
    fig_map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("Assets file is missing one of these columns: latitude, longitude, physical_risk, hazard, name")

# =========================
# RISK BY COUNTRY
# =========================
st.header("Risk by Country")
st.caption("Higher bar = higher average physical climate risk")

if {"country", "indicator"}.issubset(country.columns):
    fig_country = px.bar(
        country.sort_values("indicator", ascending=False).head(20),
        x="country",
        y="indicator"
    )
    st.plotly_chart(fig_country, use_container_width=True)
else:
    st.warning("Country file must contain columns: country, indicator")

# =========================
# RISK BY SECTOR
# =========================
st.header("Risk by Sector")
st.caption("Higher bar = higher average physical climate risk")

if {"sector", "indicator"}.issubset(sector.columns):
    fig_sector = px.bar(
        sector.sort_values("indicator", ascending=False),
        x="sector",
        y="indicator"
    )
    st.plotly_chart(fig_sector, use_container_width=True)
else:
    st.warning("Sector file must contain columns: sector, indicator")

# =========================
# ASSETS TABLE
# =========================
st.header("Assets Data")
st.dataframe(assets.head(1000), use_container_width=True)

# =========================
# DEBUG SECTION
# =========================
with st.expander("Debug - loaded files preview"):
    st.write("Summary")
    st.dataframe(summary_raw)
    st.write("Country")
    st.dataframe(country.head())
    st.write("Sector")
    st.dataframe(sector.head())
    st.write("Assets")
    st.dataframe(assets.head())
