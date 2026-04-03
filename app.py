import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Climate Risk Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# STYLE
# =========================================================
st.set_page_config(
    page_title="Climate Risk Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body {
    background-color: white;
    color: black;
}
[data-testid="stAppViewContainer"] {
    background-color: white;
}
[data-testid="stSidebar"] {
    background-color: #f7f7f7;
}
[data-testid="stMarkdownContainer"] {
    color: black;
}
h1, h2, h3, h4, h5 {
    color: black;
}
</style>
""", unsafe_allow_html=True)
# =========================================================
# HELPERS
# =========================================================
def load_summary(path, sep=";"):
    if os.path.exists(path):
        df = pd.read_csv(path, sep=sep)
        if "metric" in df.columns and "value" in df.columns:
            return dict(zip(df["metric"], df["value"]))
    return {}

def safe_float(x):
    try:
        return float(x)
    except:
        return None

def status_badge(value, thresholds, reverse=False):
    """
    thresholds = (good_limit, mid_limit)
    reverse=False : lower is better
    reverse=True  : higher is better
    """
    if value is None:
        return '<span class="badge-mid">Unavailable</span>'

    good_limit, mid_limit = thresholds

    if not reverse:
        if value <= good_limit:
            return '<span class="badge-good">Favorable</span>'
        elif value <= mid_limit:
            return '<span class="badge-mid">Watchlist</span>'
        else:
            return '<span class="badge-bad">Critical</span>'
    else:
        if value >= good_limit:
            return '<span class="badge-good">Favorable</span>'
        elif value >= mid_limit:
            return '<span class="badge-mid">Watchlist</span>'
        else:
            return '<span class="badge-bad">Critical</span>'

# =========================================================
# GLOBAL PORTFOLIO UPLOAD
# =========================================================
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

# =========================================================
# LOAD INDICATOR SUMMARIES
# =========================================================
waci = load_summary("data/waci/dashboard_summary.csv")
physical = load_summary("data/physical_risk/dashboard_summary.csv")
gar = load_summary("data/gar/dashboard_summary.csv")
itr = load_summary("data/itr/dashboard_summary.csv")

waci_val = safe_float(waci.get("portfolio_indicator"))
physical_val = safe_float(physical.get("portfolio_indicator"))
gar_val = safe_float(gar.get("portfolio_indicator"))
itr_val = safe_float(itr.get("portfolio_indicator", itr.get("portfolio_itr")))

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="big-title">Climate Risk & Portfolio Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Enterprise view of climate exposure, transition alignment and portfolio decision support.</div>',
    unsafe_allow_html=True
)

if "portfolio_df" in st.session_state:
    st.info(f"Current uploaded portfolio: {st.session_state['portfolio_filename']}")
else:
    st.warning("No uploaded portfolio. Default demo datasets will be used.")

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================
st.markdown("## Executive Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">Physical Risk</div>
        <div class="kpi-value">{physical_val if physical_val is not None else "N/A"}</div>
        <div class="small-muted">Exposure to climate hazards such as floods and extreme events.</div>
        <br>
        {status_badge(physical_val, (0.20, 0.50), reverse=False)}
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">WACI</div>
        <div class="kpi-value">{waci_val if waci_val is not None else "N/A"}</div>
        <div class="small-muted">Weighted Average Carbon Intensity of the portfolio.</div>
        <br>
        {status_badge(waci_val, (100, 300), reverse=False)}
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">GAR</div>
        <div class="kpi-value">{gar_val if gar_val is not None else "N/A"}</div>
        <div class="small-muted">Share of assets aligned with green activities.</div>
        <br>
        {status_badge(gar_val, (0.50, 0.25), reverse=True)}
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">ITR</div>
        <div class="kpi-value">{itr_val if itr_val is not None else "N/A"}</div>
        <div class="small-muted">Implied temperature rise associated with the portfolio trajectory.</div>
        <br>
        {status_badge(itr_val, (1.5, 2.0), reverse=False)}
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FINANCE <-> CLIMATE LINK
# =========================================================
st.markdown("## Why climate matters for financial decision-making")

left, right = st.columns([1.2, 1])

with left:
    st.markdown("""
    <div class="section-card">
    <h4>Climate indicators are financial signals</h4>
    <p class="small-muted">
    Climate metrics are not only sustainability scores. They help identify how environmental exposure can translate into
    financial vulnerability, earnings pressure, valuation risk and capital allocation constraints.
    </p>
    <ul>
        <li><b>Physical Risk</b>: identifies assets exposed to climate hazards that can affect operations, collateral and insurance costs.</li>
        <li><b>WACI</b>: highlights carbon-intensive exposures that may suffer from transition pressure, regulation and margin erosion.</li>
        <li><b>GAR</b>: measures green alignment and can support strategic positioning toward sustainable finance objectives.</li>
        <li><b>ITR</b>: indicates how aligned the portfolio is with low-temperature scenarios and future transition pathways.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="section-card">
    <h4>Financial implications</h4>
    <ul>
        <li>credit deterioration</li>
        <li>asset repricing</li>
        <li>sector rotation pressure</li>
        <li>capex / financing reallocation</li>
        <li>reputational and regulatory exposure</li>
    </ul>
    <p class="small-muted">
    The purpose of this dashboard is to move from climate observation to portfolio action.
    </p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# INDICATOR LANDSCAPE
# =========================================================
st.markdown("## Indicator Landscape")

i1, i2, i3, i4 = st.columns(4)

with i1:
    st.markdown("""
    <div class="section-card">
    <h4>🌊 Physical Risk</h4>
    <p class="small-muted">Measures exposure to climate hazards such as flood risk.</p>
    <p><b>Reading rule:</b> lower is better</p>
    <p><b>Main question:</b> where is the portfolio physically vulnerable?</p>
    </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown("""
    <div class="section-card">
    <h4>🏭 WACI</h4>
    <p class="small-muted">Weighted Average Carbon Intensity.</p>
    <p><b>Reading rule:</b> lower is better</p>
    <p><b>Main question:</b> how carbon-intensive is the portfolio?</p>
    </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown("""
    <div class="section-card">
    <h4>🌱 GAR</h4>
    <p class="small-muted">Green Asset Ratio.</p>
    <p><b>Reading rule:</b> higher is better</p>
    <p><b>Main question:</b> how much of the portfolio is green-aligned?</p>
    </div>
    """, unsafe_allow_html=True)

with i4:
    st.markdown("""
    <div class="section-card">
    <h4>🌡️ ITR</h4>
    <p class="small-muted">Implied Temperature Rise.</p>
    <p><b>Reading rule:</b> lower is better</p>
    <p><b>Main question:</b> how aligned is the portfolio with climate scenarios?</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# COMPARISON SECTION
# =========================================================
st.markdown("## Portfolio-Level Comparison")

comparison_rows = []

if physical_val is not None:
    comparison_rows.append({
        "Indicator": "Physical Risk",
        "Portfolio Value": physical_val,
        "Preferred Direction": "Lower",
        "Interpretation": "Physical climate exposure"
    })

if waci_val is not None:
    comparison_rows.append({
        "Indicator": "WACI",
        "Portfolio Value": waci_val,
        "Preferred Direction": "Lower",
        "Interpretation": "Carbon intensity"
    })

if gar_val is not None:
    comparison_rows.append({
        "Indicator": "GAR",
        "Portfolio Value": gar_val,
        "Preferred Direction": "Higher",
        "Interpretation": "Green alignment"
    })

if itr_val is not None:
    comparison_rows.append({
        "Indicator": "ITR",
        "Portfolio Value": itr_val,
        "Preferred Direction": "Lower",
        "Interpretation": "Climate scenario alignment"
    })

comparison_df = pd.DataFrame(comparison_rows)

col_table, col_chart = st.columns([1.15, 1])

with col_table:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### Comparison Table")
    if not comparison_df.empty:
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    else:
        st.info("No summary files available yet for comparison.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### Comparison Chart")
    if not comparison_df.empty:
        st.bar_chart(comparison_df.set_index("Indicator")["Portfolio Value"])
    else:
        st.info("Comparison chart unavailable.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIONS / BUSINESS DECISIONS
# =========================================================
st.markdown("## Suggested Management Actions")

a1, a2 = st.columns(2)

with a1:
    st.markdown("""
    <div class="section-card">
    <h4>Portfolio management actions</h4>
    <ul>
        <li>reduce concentration in high-risk countries and sectors,</li>
        <li>review top carbon contributors,</li>
        <li>increase green-aligned allocations when possible,</li>
        <li>prioritize counterparties with better transition pathways.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown("""
    <div class="section-card">
    <h4>How to use this application</h4>
    <ol>
        <li>Start from this page for the executive overview.</li>
        <li>Open each indicator page for detailed breakdowns.</li>
        <li>Use the comparison page to align the indicators.</li>
        <li>Use the indicator guide to interpret graphs and tables correctly.</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FOOTER NOTE
# =========================================================
st.markdown("---")
st.caption("This dashboard is designed as a portfolio decision-support tool linking climate analytics with financial interpretation.")
