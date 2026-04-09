import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def load_default_waci_data():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "waci"

    assets = pd.read_csv(data_dir / "dashboard_assets.csv", sep=";")
    country = pd.read_csv(data_dir / "dashboard_country_indicator.csv", sep=";")
    sector = pd.read_csv(data_dir / "dashboard_sector_indicator.csv", sep=";")
    summary_raw = pd.read_csv(data_dir / "dashboard_summary.csv", sep=";")

    return assets, country, sector, summary_raw

def build_waci_from_uploaded_portfolio(df):
    data = df.copy()

    rename_map = {}
    if "exposure_value" not in data.columns and "value" in data.columns:
        rename_map["value"] = "exposure_value"
    if "counterparty" not in data.columns and "name" in data.columns:
        rename_map["name"] = "counterparty"

    data = data.rename(columns=rename_map)

    required = ["counterparty", "country", "sector", "exposure_value", "emissions", "revenue"]
    missing = [c for c in required if c not in data.columns]

    if missing:
        return None, f"Uploaded portfolio missing columns for WACI: {missing}"

    data["exposure_value"] = pd.to_numeric(data["exposure_value"], errors="coerce").fillna(0)
    data["emissions"] = pd.to_numeric(data["emissions"], errors="coerce").fillna(0)
    data["revenue"] = pd.to_numeric(data["revenue"], errors="coerce").fillna(0)

    total_value = data["exposure_value"].sum()
    if total_value <= 0:
        return None, "Uploaded portfolio has zero total exposure_value."

    data["intensity"] = data.apply( lambda row: row["emissions"] / (row["revenue"] / 1_000_000) if row["revenue"] > 0 else 0,
        axis=1 )
    data["weight"] = data["exposure_value"] / total_value
    data["contribution"] = data["weight"] * data["intensity"]

    portfolio_indicator = data["contribution"].sum()
    total_emissions = data["emissions"].sum()

    country = (data.groupby("country", as_index=False)["contribution"].sum().rename(columns={"contribution": "indicator"}))

    sector = (data.groupby("sector", as_index=False)["contribution"].sum().rename(columns={"contribution": "indicator"}))

    summary_raw = pd.DataFrame({ "metric": ["total_value", "total_emissions", "portfolio_indicator"], "value": [total_value, total_emissions, portfolio_indicator] })

    data = data.rename(columns={"counterparty": "name"})

    return (data, country, sector, summary_raw), None

def show_waci_dashboard():
    st.header("Climate Transition Risk Dashboard : WACI")

    portfolio_df = st.session_state.get("portfolio_df", None)

    if portfolio_df is not None:
        built, warning_msg = build_waci_from_uploaded_portfolio(portfolio_df)
        if built is not None:
            assets, country, sector, summary_raw = built
            st.success("Using uploaded portfolio for WACI.")
        else:
            st.warning(warning_msg)
            assets, country, sector, summary_raw = load_default_waci_data()
            st.info("Fallback to default WACI demo data.")
    else:
        assets, country, sector, summary_raw = load_default_waci_data()

    summary = summary_raw.set_index("metric")["value"]

    total_value = safe_float(summary.get("total_value"))
    total_emissions = safe_float(summary.get("total_emissions"))
    indicator = safe_float(summary.get("portfolio_indicator"))

    st.subheader("Portfolio Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Value", f"{total_value:,.0f}")
    col2.metric("Total Emissions", f"{total_emissions:,.0f}")
    col3.metric("Portfolio Indicator", f"{indicator:.3f}")

    st.caption("WACI = Σ(weight_i × carbon intensity_i)")

    st.subheader("Assets Map")

    if {"latitude", "longitude", "name"}.issubset(assets.columns):
        size_col = "exposure_value" if "exposure_value" in assets.columns else None
        color_col = "sector" if "sector" in assets.columns else None

        fig_map = px.scatter_mapbox(
            assets,
            lat="latitude",
            lon="longitude",
            size=size_col,
            color=color_col,
            hover_name="name",
            hover_data=[c for c in ["country", "exposure_value"] if c in assets.columns],
            zoom=2,
            height=600 )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No map displayed because latitude/longitude are not available.")

    st.subheader("WACI by Country")
    if {"country", "indicator"}.issubset(country.columns):
        fig_country = px.bar(
            country.sort_values("indicator", ascending=False).head(20),
            x="country",
            y="indicator")
        st.plotly_chart(fig_country, use_container_width=True)

    st.subheader("WACI by Sector")
    if {"sector", "indicator"}.issubset(sector.columns):
        fig_sector = px.bar(
            sector.sort_values("indicator", ascending=False),
            x="sector",
            y="indicator"  )
        st.plotly_chart(fig_sector, use_container_width=True)

    st.subheader("Assets Data")
    st.dataframe(assets.head(1000), use_container_width=True)
