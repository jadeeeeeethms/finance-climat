# -*- coding: utf-8 -*-
"""
Physical Risk dashboard page
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Physical Risk", layout="wide")

# =========================
# LOAD DATA
# =========================
assets = pd.read_csv("data/physical_risk/dashboard_assets.csv", sep=";")
country = pd.read_csv("data/physical_risk/dashboard_country_indicator.csv", sep=";")
sector = pd.read_csv("data/physical_risk/dashboard_sector_indicator.csv", sep=";")
summary_raw = pd.read_csv("data/physical_risk/dashboard_summary.csv", sep=";")
interpretation = pd.read_csv("data/physical_risk/dashboard_interpretation.csv", sep=";")

summary = summary_raw.set_index("metric")["value"].to_dict()
interp = interpretation.set_index("item")["value"].to_dict()

# =========================
# SAFE CONVERSIONS
# =========================
def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

total_value = safe_float(summary.get("total_value"))
total_risk = safe_float(summary.get("total_risk"))
portfolio_indicator = safe_float(summary.get("portfolio_indicator"))

# =========================
# TITLE
# =========================
st.title("Climate Physical Risk Dashboard")
st.caption("Flood exposure indicator for portfolio assets")

# =========================
# INTRODUCTION
# =========================
st.markdown("""
This page helps a non-expert user understand where physical climate risk is low or high.

**General rule:**  
- **Lower indicator values = lower physical risk**
- **Higher indicator values = higher physical risk**
""")

# =========================
# SUMMARY METRICS
# =========================
st.header("1. Portfolio Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Value", f"{total_value:,.0f}")

with col2:
    st.metric("Total Risk", f"{total_risk:,.0f}")

with col3:
    st.metric("Portfolio Indicator", f"{portfolio_indicator:.3f}")

# =========================
# INTERPRETATION
# =========================
st.header("2. How to Interpret This Indicator")

st.info(
    summary.get(
        "interpretation",
        "This indicator measures the average exposure of the portfolio to physical climate risk. Lower values are better."
    )
)

st.success(
    summary.get(
        "investment_rule",
        "Simple rule: prioritize countries, sectors and assets with the lowest indicator values."
    )
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### What a high value means")
    st.write(
        interp.get(
            "meaning_of_high_value",
            "A high value means stronger exposure to flood-related physical risk."
        )
    )

with col2:
    st.markdown("### What a low value means")
    st.write(
        interp.get(
            "meaning_of_low_value",
            "A low value means lower exposure to physical climate risk."
        )
    )

# =========================
# QUICK DECISION SUPPORT
# =========================
st.header("3. Quick Decision Support")

best_country = summary.get("best_country_to_prioritize", "N/A")
worst_country = summary.get("worst_country_to_avoid", "N/A")
best_sector = summary.get("best_sector_to_prioritize", "N/A")
worst_sector = summary.get("worst_sector_to_avoid", "N/A")
best_asset = summary.get("best_asset_to_prioritize", "N/A")
worst_asset = summary.get("worst_asset_to_avoid", "N/A")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Lower-risk choices to prioritize")
    st.write(f"**Country:** {best_country}")
    st.write(f"**Sector:** {best_sector}")
    st.write(f"**Asset:** {best_asset}")

with col2:
    st.markdown("### Higher-risk choices to review carefully")
    st.write(f"**Country:** {worst_country}")
    st.write(f"**Sector:** {worst_sector}")
    st.write(f"**Asset:** {worst_asset}")

# =========================
# MAP
# =========================
st.header("4. Assets Map")

st.markdown("""
**How to read this map**
- each point represents one asset,
- point size reflects the level of physical risk,
- color reflects hazard intensity,
- larger and darker points deserve more attention.
""")

required_map_cols = {"latitude", "longitude", "name"}
if required_map_cols.issubset(assets.columns):

    size_col = "physical_risk" if "physical_risk" in assets.columns else None
    color_col = "hazard" if "hazard" in assets.columns else None

    fig_map = px.scatter_mapbox(
        assets,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        size=size_col if size_col else None,
        color=color_col if color_col else None,
        zoom=1,
        height=600
    )

    fig_map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.warning("The assets file must contain at least: latitude, longitude, name")

# =========================
# COUNTRY ANALYSIS
# =========================
st.header("5. Risk by Country")

st.markdown("""
This chart compares the average physical climate risk across countries.

- a **higher bar** means a riskier country,
- a **lower bar** means a safer country from this indicator's point of view.
""")

if {"country", "indicator"}.issubset(country.columns):
    country_sorted = country.sort_values("indicator", ascending=False)

    fig_country = px.bar(
        country_sorted.head(20),
        x="country",
        y="indicator",
        title="Top 20 countries by physical risk indicator"
    )
    st.plotly_chart(fig_country, use_container_width=True)

    st.markdown("### Lowest-risk countries")
    st.dataframe(
        country.sort_values("indicator", ascending=True).head(10),
        use_container_width=True
    )

    st.markdown("### Highest-risk countries")
    st.dataframe(
        country.sort_values("indicator", ascending=False).head(10),
        use_container_width=True
    )
else:
    st.warning("Country file must contain columns: country, indicator")

# =========================
# SECTOR ANALYSIS
# =========================
st.header("6. Risk by Sector")

st.markdown("""
This chart compares sectors.

- sectors with **higher values** are more exposed on average,
- sectors with **lower values** are better candidates for a cautious investor.
""")

if {"sector", "indicator"}.issubset(sector.columns):
    sector_sorted = sector.sort_values("indicator", ascending=False)

    fig_sector = px.bar(
        sector_sorted,
        x="sector",
        y="indicator",
        title="Physical risk indicator by sector"
    )
    st.plotly_chart(fig_sector, use_container_width=True)

    st.markdown("### Lowest-risk sectors")
    st.dataframe(
        sector.sort_values("indicator", ascending=True).head(10),
        use_container_width=True
    )

    st.markdown("### Highest-risk sectors")
    st.dataframe(
        sector.sort_values("indicator", ascending=False).head(10),
        use_container_width=True
    )
else:
    st.warning("Sector file must contain columns: sector, indicator")

# =========================
# ASSETS TABLE
# =========================
st.header("7. Detailed Asset View")

st.markdown("""
This table helps identify which assets look safest and which ones deserve more caution.
Use it to spot:
- high hazard values,
- high physical risk values,
- concentration in risky countries or sectors.
""")

show_cols = [c for c in [
    "name", "country", "sector", "value", "hazard", "physical_risk",
    "risk_ratio", "risk_level", "investment_view"
] if c in assets.columns]

st.dataframe(
    assets[show_cols].sort_values(
        "physical_risk" if "physical_risk" in assets.columns else show_cols[0],
        ascending=False
    ),
    use_container_width=True
)

# =========================
# FINAL TAKEAWAY
# =========================
st.header("8. Final Takeaway")

st.markdown(f"""
For a beginner investor using only this dashboard:

- **prefer** assets, countries and sectors with the **lowest indicator values**,
- **review carefully** those with the **highest values**,
- pay special attention to concentration in **{worst_country}** and **{worst_sector}** if these are the top risky contributors.
""")

# =========================
# OPTIONAL DEBUG
# =========================
with st.expander("Debug - preview loaded data"):
    st.write("Summary raw")
    st.dataframe(summary_raw)
    st.write("Country preview")
    st.dataframe(country.head())
    st.write("Sector preview")
    st.dataframe(sector.head())
    st.write("Assets preview")
    st.dataframe(assets.head())
