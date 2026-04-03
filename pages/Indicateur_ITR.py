import streamlit as st
import pandas as pd
import plotly.express as px
from indicators.itr_logic import load_and_process_itr_data

st.set_page_config(page_title="Climate Risk Dashboard - ITR", layout="wide")

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def build_itr_from_uploaded_portfolio(df):
    data = df.copy()

    required_cols = ["counterparty_id", "sector", "asset_class", "itr"]
    missing = [c for c in required_cols if c not in data.columns]

    if missing:
        return None, (
            "Uploaded portfolio is not ITR-ready. Missing columns: "
            f"{missing}. Default ITR demo data will be used instead."
        )

    if "exposure" not in data.columns and "value" in data.columns:
        data["exposure"] = data["value"]

    if "weight" not in data.columns and "exposure" in data.columns:
        total = pd.to_numeric(data["exposure"], errors="coerce").fillna(0).sum()
        if total > 0:
            data["weight"] = pd.to_numeric(data["exposure"], errors="coerce").fillna(0) / total
        else:
            data["weight"] = 0

    if "source" not in data.columns:
        data["source"] = "Uploaded"
    if "dqs" not in data.columns:
        data["dqs"] = 3
    if "outlier_flag" not in data.columns:
        data["outlier_flag"] = False

    data["itr"] = pd.to_numeric(data["itr"], errors="coerce").fillna(0)
    data["weight"] = pd.to_numeric(data["weight"], errors="coerce").fillna(0)
    data["dqs"] = pd.to_numeric(data["dqs"], errors="coerce").fillna(0)

    portfolio_itr = (data["itr"] * data["weight"]).sum() if "weight" in data.columns else data["itr"].mean()
    baseline_temp = 1.5
    weighted_dqs = (data["dqs"] * data["weight"]).sum() if "weight" in data.columns else data["dqs"].mean()

    sector = (
        data.groupby("sector", as_index=False)
        .apply(lambda x: pd.Series({"itr": (x["itr"] * x["weight"]).sum() if "weight" in x.columns else x["itr"].mean()}))
        .reset_index(drop=True)
    )

    asset_class = (
        data.groupby("asset_class", as_index=False)
        .apply(lambda x: pd.Series({"itr": (x["itr"] * x["weight"]).sum() if "weight" in x.columns else x["itr"].mean()}))
        .reset_index(drop=True)
    )

    coverage = (
        data.groupby("source", as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    total_count = coverage["count"].sum()
    coverage["percentage"] = 100 * coverage["count"] / total_count if total_count > 0 else 0

    return {
        "success": True,
        "assets": data,
        "sector": sector,
        "asset_class": asset_class,
        "coverage": coverage[["source", "percentage"]],
        "portfolio_itr": portfolio_itr,
        "baseline_temp": baseline_temp,
        "weighted_dqs": weighted_dqs
    }, None

portfolio_df = st.session_state.get("portfolio_df", None)

if portfolio_df is not None:
    data, warning_msg = build_itr_from_uploaded_portfolio(portfolio_df)
    if data is not None:
        st.success("Using uploaded portfolio for ITR.")
    else:
        st.warning(warning_msg)
        data = load_and_process_itr_data()
        if not data["success"]:
            st.warning(f"⚠️ Erreur : {data['error']}")
            st.stop()
        st.info("Fallback to default ITR demo data.")
else:
    data = load_and_process_itr_data()
    if not data["success"]:
        st.warning(f"⚠️ Erreur : {data['error']}")
        st.stop()

assets = data["assets"]
sector = data["sector"]
asset_class = data["asset_class"]
coverage = data["coverage"]
portfolio_itr = safe_float(data["portfolio_itr"])
baseline_temp = safe_float(data["baseline_temp"], 1.5)
weighted_dqs = safe_float(data["weighted_dqs"])

st.title("Climate Transition Risk Dashboard : Implied Temperature Rise (ITR)")
st.markdown("""
The ITR indicator measures the estimated global temperature increase implied by the portfolio’s emissions trajectory.

**Reading rule:**  
- lower ITR = better climate alignment  
- higher ITR = weaker alignment with Paris-type scenarios
""")

st.header("Portfolio Summary")

col1, col2, col3 = st.columns(3)
delta_baseline = portfolio_itr - baseline_temp

col1.metric(
    label="Portfolio ITR",
    value=f"{portfolio_itr:.2f} °C",
    delta=f"{delta_baseline:+.2f} °C vs Baseline",
    delta_color="inverse"
)
col2.metric(label="Scenario Baseline Temperature", value=f"{baseline_temp:.2f} °C")
col3.metric(label="Weighted Data Quality Score", value=f"{weighted_dqs:.2f} / 5")

st.info("""
A portfolio ITR above the scenario baseline suggests weaker climate alignment.
A lower ITR is preferable because it indicates a trajectory closer to low-temperature pathways.
""")

st.header("ITR Breakdown")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("ITR by Asset Class")
    if {"asset_class", "itr"}.issubset(asset_class.columns):
        fig_ac = px.bar(
            asset_class.sort_values("itr", ascending=False),
            x="asset_class",
            y="itr",
            color="itr",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_ac, use_container_width=True)

with col_chart2:
    st.subheader("Top 10 Sectors Contributing to ITR")
    if {"sector", "itr"}.issubset(sector.columns):
        top_sectors = sector.sort_values("itr", ascending=False).head(10)
        fig_sector = px.bar(
            top_sectors,
            x="sector",
            y="itr",
            color="itr",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_sector, use_container_width=True)

st.header("ITR Distribution & Data Quality")

col_dist, col_cov = st.columns(2)

with col_dist:
    st.subheader("ITR Distribution Histogram")
    if "itr" in assets.columns:
        fig_hist = px.histogram(
            assets,
            x="itr",
            nbins=30,
            color_discrete_sequence=["#EF553B"]
        )
        fig_hist.add_vline(
            x=baseline_temp,
            line_dash="dash",
            line_color="green",
            annotation_text="Scenario Baseline"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

with col_cov:
    st.subheader("Coverage Metrics (Reduction Rate Source)")
    if {"percentage", "source"}.issubset(coverage.columns):
        fig_cov = px.pie(
            coverage,
            values="percentage",
            names="source",
            hole=0.4
        )
        st.plotly_chart(fig_cov, use_container_width=True)

st.header("Counterparty-level Drill-down Data")

display_columns = [
    "counterparty_id", "sector", "asset_class", "exposure", "weight",
    "current_intensity", "reduction_rate", "source",
    "itr", "dqs", "outlier_flag"
]

existing_cols = [col for col in display_columns if col in assets.columns]

if existing_cols:
    st.dataframe(assets[existing_cols].head(1000), use_container_width=True)

st.header("Interpretation")
st.markdown("""
**What this indicator means**
- ITR is a forward-looking indicator expressed in °C.
- It estimates the temperature rise implied if portfolio companies follow their projected emissions pathway.

**How to read it**
- higher ITR = weaker climate alignment
- lower ITR = stronger alignment with transition scenarios

**What to do**
- review sectors and counterparties with the highest ITR,
- compare the portfolio ITR with the baseline scenario,
- pay attention to low-quality coverage if many values come from proxies or defaults.
""")
