import streamlit as st
import plotly.express as px
from indicators.itr_logic import load_and_process_itr_data

st.set_page_config(page_title="Climate Risk Dashboard - ITR", layout="wide")

st.title("Climate Transition Risk Dashboard : Implied Temperature Rise (ITR)")
st.markdown("""
The ITR indicator measures the estimated global temperature increase implied by the portfolio’s emissions trajectory.

**Reading rule:**  
- lower ITR = better climate alignment  
- higher ITR = weaker alignment with Paris-type scenarios
""")

data = load_and_process_itr_data()

if not data["success"]:
    st.warning(f"⚠️ Erreur : {data['error']}")
    st.stop()

assets = data["assets"]
sector = data["sector"]
asset_class = data["asset_class"]
coverage = data["coverage"]
portfolio_itr = data["portfolio_itr"]
baseline_temp = data["baseline_temp"]
weighted_dqs = data["weighted_dqs"]

# =========================
# KPI
# =========================
st.header("Portfolio Summary")

col1, col2, col3 = st.columns(3)

delta_baseline = portfolio_itr - baseline_temp

col1.metric(
    label="Portfolio ITR",
    value=f"{portfolio_itr:.2f} °C",
    delta=f"{delta_baseline:+.2f} °C vs Baseline",
    delta_color="inverse"
)
col2.metric(
    label="Scenario Baseline Temperature",
    value=f"{baseline_temp:.2f} °C"
)
col3.metric(
    label="Weighted Data Quality Score",
    value=f"{weighted_dqs:.2f} / 5",
    help="1 = best quality, 5 = weakest quality"
)

st.info("""
A portfolio ITR above the scenario baseline suggests weaker climate alignment.
A lower ITR is preferable because it indicates a trajectory closer to low-temperature pathways.
""")

# =========================
# BREAKDOWNS
# =========================
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
    else:
        st.warning("Le fichier asset class doit contenir : asset_class, itr")

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
    else:
        st.warning("Le fichier sector doit contenir : sector, itr")

# =========================
# DISTRIBUTION / COVERAGE
# =========================
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
    else:
        st.warning("Le fichier assets doit contenir la colonne : itr")

with col_cov:
    st.subheader("Coverage Metrics (Reduction Rate Source)")
    if {"percentage", "source"}.issubset(coverage.columns):
        fig_cov = px.pie(
            coverage,
            values="percentage",
            names="source",
            hole=0.4,
            color="source",
            color_discrete_map={
                "SBTi Target": "#00CC96",
                "Sector Proxy": "#FFA15A",
                "Broad Default": "#EF553B"
            }
        )
        st.plotly_chart(fig_cov, use_container_width=True)
    else:
        st.warning("Le fichier coverage doit contenir : percentage, source")

# =========================
# DRILL DOWN
# =========================
st.header("Counterparty-level Drill-down Data")

display_columns = [
    "counterparty_id", "sector", "exposure", "weight",
    "current_intensity", "reduction_rate", "source",
    "itr", "dqs", "outlier_flag"
]

existing_cols = [col for col in display_columns if col in assets.columns]

if existing_cols:
    st.dataframe(assets[existing_cols].head(1000), use_container_width=True)
else:
    st.warning("Aucune des colonnes attendues n'a été trouvée dans itr_assets_data.csv")

# =========================
# INTERPRETATION
# =========================
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
