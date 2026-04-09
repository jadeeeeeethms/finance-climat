# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Physical Risk", layout="wide")

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def load_default_data():
    assets = pd.read_csv("data/physical_risk/dashboard_assets.csv", sep=";")
    country = pd.read_csv("data/physical_risk/dashboard_country_indicator.csv", sep=";")
    sector = pd.read_csv("data/physical_risk/dashboard_sector_indicator.csv", sep=";")
    summary_raw = pd.read_csv("data/physical_risk/dashboard_summary.csv", sep=";")
    interpretation = pd.read_csv("data/physical_risk/dashboard_interpretation.csv", sep=";")
    return assets, country, sector, summary_raw, interpretation

def build_from_uploaded_portfolio(df):
    data = df.copy()

    #harmonisation minimale
    rename_map = {}
    if "exposure_value" in data.columns and "value" not in data.columns:
        rename_map["exposure_value"] = "value"
    if "counterparty" in data.columns and "name" not in data.columns:
        rename_map["counterparty"] = "name"

    data = data.rename(columns=rename_map)

    required = ["name", "country", "sector", "value", "latitude", "longitude"]
    missing = [c for c in required if c not in data.columns]

    if missing:
        return None, f"Uploaded portfolio missing columns for Physical Risk: {missing}"

    data["value"] = pd.to_numeric(data["value"], errors="coerce").fillna(0)

    #si hazard existe on calcule physical_risk
    if "hazard" in data.columns and "physical_risk" not in data.columns:
        data["hazard"] = pd.to_numeric(data["hazard"], errors="coerce").fillna(0)
        data["physical_risk"] = data["hazard"] * data["value"]

    #si physical_risk n'existe pas, on ne peut pas faire un vrai calcul
    if "physical_risk" not in data.columns:
        return None, ( "Uploaded portfolio has no 'physical_risk' column and no 'hazard' column. " "Default demo dataset will be used instead." )

    data["physical_risk"] = pd.to_numeric(data["physical_risk"], errors="coerce").fillna(0)
    data["risk_ratio"] = data["physical_risk"] / data["value"].replace(0, pd.NA)

    total_value = data["value"].sum()
    total_risk = data["physical_risk"].sum()
    portfolio_indicator = total_risk / total_value if total_value > 0 else 0.0

    country = (data.groupby("country", as_index=False)
        .agg(total_value=("value", "sum"), total_risk=("physical_risk", "sum")))
    country["indicator"] = country["total_risk"] / country["total_value"].replace(0, pd.NA)
    country = country[["country", "indicator"]].fillna(0)

    sector = (data.groupby("sector", as_index=False).agg(total_value=("value", "sum"), total_risk=("physical_risk", "sum")))
    sector["indicator"] = sector["total_risk"] / sector["total_value"].replace(0, pd.NA)
    sector = sector[["sector", "indicator"]].fillna(0)

    best_country = country.sort_values("indicator", ascending=True).iloc[0]["country"] if not country.empty else "N/A"
    worst_country = country.sort_values("indicator", ascending=False).iloc[0]["country"] if not country.empty else "N/A"
    best_sector = sector.sort_values("indicator", ascending=True).iloc[0]["sector"] if not sector.empty else "N/A"
    worst_sector = sector.sort_values("indicator", ascending=False).iloc[0]["sector"] if not sector.empty else "N/A"
    best_asset = data.sort_values("physical_risk", ascending=True).iloc[0]["name"] if not data.empty else "N/A"
    worst_asset = data.sort_values("physical_risk", ascending=False).iloc[0]["name"] if not data.empty else "N/A"

    summary_raw = pd.DataFrame({
        "metric": [
            "total_value",
            "total_risk",
            "portfolio_indicator",
            "interpretation",
            "investment_rule",
            "best_country_to_prioritize",
            "worst_country_to_avoid",
            "best_sector_to_prioritize",
            "worst_sector_to_avoid",
            "best_asset_to_prioritize",
            "worst_asset_to_avoid"
        ],
        "value": [
            total_value,
            total_risk,
            portfolio_indicator,
            "Lower values are better because they mean lower exposure to climate physical risk.",
            "Invest first in the lowest indicator values; avoid or review the highest ones.",
            best_country,
            worst_country,
            best_sector,
            worst_sector,
            best_asset,
            worst_asset
        ]
    })

    interpretation = pd.DataFrame({
        "item": ["meaning_of_high_value", "meaning_of_low_value"],
        "value": [
            "A high value means stronger exposure to physical climate risk.",
            "A low value means lower exposure to physical climate risk."
        ]
    })

    return (data, country, sector, summary_raw, interpretation), None
portfolio_df = st.session_state.get("portfolio_df", None)

if portfolio_df is not None:
    built, warning_msg = build_from_uploaded_portfolio(portfolio_df)
    if built is not None:
        assets, country, sector, summary_raw, interpretation = built
        st.success("Using uploaded portfolio for Physical Risk.")
    else:
        st.warning(warning_msg)
        assets, country, sector, summary_raw, interpretation = load_default_data()
        st.info("Fallback to default Physical Risk demo dataset.")
else:
    assets, country, sector, summary_raw, interpretation = load_default_data()

summary = summary_raw.set_index("metric")["value"].to_dict()
interp = interpretation.set_index("item")["value"].to_dict()

total_value = safe_float(summary.get("total_value"))
total_risk = safe_float(summary.get("total_risk"))
portfolio_indicator = safe_float(summary.get("portfolio_indicator"))

st.title("Climate Physical Risk Dashboard")
st.caption("Flood exposure indicator for portfolio assets")

st.markdown("""
This page helps a non-expert user understand where physical climate risk is low or high.

**General rule:**  
- **Lower indicator values = lower physical risk**
- **Higher indicator values = higher physical risk**
""")

st.header("1. Portfolio Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total Value", f"{total_value:,.0f}")
col2.metric("Total Risk", f"{total_risk:,.0f}")
col3.metric("Portfolio Indicator", f"{portfolio_indicator:.3f}")

st.header("2. How to Interpret This Indicator")
st.info(summary.get("interpretation", "Lower values are better."))
st.success(summary.get("investment_rule", "Prefer the lowest values."))

col1, col2 = st.columns(2)
with col1:
    st.markdown("### What a high value means")
    st.write(interp.get("meaning_of_high_value", "A high value means stronger exposure."))
with col2:
    st.markdown("### What a low value means")
    st.write(interp.get("meaning_of_low_value", "A low value means lower exposure."))

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

st.header("4. Assets Map")

if {"latitude", "longitude", "name"}.issubset(assets.columns):
    size_col = "physical_risk" if "physical_risk" in assets.columns else None
    color_col = "hazard" if "hazard" in assets.columns else None

    fig_map = px.scatter_mapbox(
        assets,
        lat="latitude",
        lon="longitude",
        hover_name="name",
        size=size_col,
        color=color_col,
        zoom=1,
        height=600
    )
    fig_map.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("The assets file must contain at least: latitude, longitude, name")

st.header("5. Risk by Country")
if {"country", "indicator"}.issubset(country.columns):
    fig_country = px.bar(
        country.sort_values("indicator", ascending=False).head(20),
        x="country", y="indicator"
    )
    st.plotly_chart(fig_country, use_container_width=True)

st.header("6. Risk by Sector")
if {"sector", "indicator"}.issubset(sector.columns):
    fig_sector = px.bar(
        sector.sort_values("indicator", ascending=False),
        x="sector", y="indicator"
    )
    st.plotly_chart(fig_sector, use_container_width=True)

st.header("7. Detailed Asset View")

show_cols = [c for c in [
    "name", "country", "sector", "value", "hazard", "physical_risk", "risk_ratio"
] if c in assets.columns]

if show_cols:
    sort_col = "physical_risk" if "physical_risk" in assets.columns else show_cols[0]
    st.dataframe(assets[show_cols].sort_values(sort_col, ascending=False), use_container_width=True)
