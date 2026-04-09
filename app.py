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
st.markdown("""
<style>
:root {
    --card-bg: rgba(127, 127, 127, 0.08);
    --border-color: rgba(127, 127, 127, 0.18);
    --hero-bg-1: rgba(30, 64, 175, 0.10);
    --hero-bg-2: rgba(16, 185, 129, 0.10);
    --muted-text: rgba(120, 120, 120, 0.95);
    --badge-bg: rgba(59, 130, 246, 0.12);
    --badge-border: rgba(59, 130, 246, 0.28);
    --good-bg: rgba(34, 197, 94, 0.14);
    --good-color: #15803d;
    --mid-bg: rgba(245, 158, 11, 0.16);
    --mid-color: #b45309;
    --bad-bg: rgba(239, 68, 68, 0.14);
    --bad-color: #b91c1c;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border-color);
}

html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

.hero {
    padding: 30px 34px;
    border-radius: 22px;
    margin-bottom: 22px;
    background: linear-gradient(135deg, var(--hero-bg-1), var(--hero-bg-2));
    border: 1px solid var(--border-color);
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 0.4rem;
}

.hero-subtitle {
    font-size: 1.08rem;
    opacity: 0.88;
    margin-bottom: 1rem;
}

.hero-badge {
    display: inline-block;
    padding: 0.38rem 0.75rem;
    border-radius: 999px;
    font-size: 0.84rem;
    font-weight: 600;
    background: var(--badge-bg);
    border: 1px solid var(--badge-border);
    margin-right: 8px;
    margin-top: 4px;
}

.info-card {
    padding: 18px 20px;
    border-radius: 16px;
    border: 1px solid var(--border-color);
    background: var(--card-bg);
    margin-bottom: 16px;
}

.metric-card {
    padding: 20px 20px 16px 20px;
    border-radius: 18px;
    border: 1px solid var(--border-color);
    background: var(--card-bg);
    min-height: 200px;
}

.section-card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid var(--border-color);
    background: var(--card-bg);
    margin-bottom: 16px;
    height: 100%;
}

.section-title {
    font-size: 2rem;
    font-weight: 780;
    margin-top: 0.4rem;
    margin-bottom: 1rem;
}

.small-label {
    font-size: 0.92rem;
    opacity: 0.76;
    margin-bottom: 0.28rem;
}

.kpi-title {
    font-size: 0.95rem;
    opacity: 0.78;
    margin-bottom: 0.3rem;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 750;
    line-height: 1.1;
    margin-bottom: 0.55rem;
}

.small-muted {
    font-size: 0.96rem;
    opacity: 0.82;
}

.status-badge {
    display: inline-block;
    padding: 0.35rem 0.72rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-top: 10px;
}

.status-good {
    background: var(--good-bg);
    color: var(--good-color);
}

.status-mid {
    background: var(--mid-bg);
    color: var(--mid-color);
}

.status-bad {
    background: var(--bad-bg);
    color: var(--bad-color);
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stFileUploader"] {
    border-radius: 14px;
    padding: 8px;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
}

button {
    border-radius: 10px !important;
}

.js-plotly-plot {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def load_summary(path, sep=";"):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, sep=sep)
            df.columns = df.columns.astype(str).str.strip()
            if "metric" in df.columns and "value" in df.columns:
                df["metric"] = df["metric"].astype(str).str.strip()
                return dict(zip(df["metric"], df["value"]))
        except Exception:
            return {}
    return {}

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def get_first_available_metric(summary_dict, possible_keys):
    for key in possible_keys:
        if key in summary_dict:
            value = safe_float(summary_dict.get(key))
            if value is not None:
                return value
    return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    rename_map = {
        "EU Taxonomy alignment (%)": "EU Taxonomy alignment",
        "EU taxonomy alignment": "EU Taxonomy alignment",
        "Taxonomy eligibility": "Taxonomy Eligibility",
        "Portfolio Weight %": "Portfolio Weight (%)",
        "Portfolio weight (%)": "Portfolio Weight (%)",
        "Company Name": "Company name",
        "Nace Code": "NACE Code",
    }

    df.rename(columns=rename_map, inplace=True)
    return df

def compute_gar_from_portfolio(df: pd.DataFrame):
    try:
        df = normalize_columns(df)

        required_cols = [
            "NACE Code",
            "Portfolio Weight (%)",
            "EU Taxonomy alignment"
        ]
        if not all(col in df.columns for col in required_cols):
            return None

        df = df.copy()
        df["NACE Code"] = df["NACE Code"].astype(str).str.strip()
        df["Portfolio Weight (%)"] = pd.to_numeric(df["Portfolio Weight (%)"], errors="coerce")
        df["EU Taxonomy alignment"] = pd.to_numeric(df["EU Taxonomy alignment"], errors="coerce").fillna(0)

        df = df.dropna(subset=["Portfolio Weight (%)"])
        df = df[~df["NACE Code"].str.upper().str.startswith("K")]

        if df.empty:
            return None

        total_weight = df["Portfolio Weight (%)"].sum()
        if total_weight <= 0:
            return None

        df["Normalized_Weight"] = df["Portfolio Weight (%)"] / total_weight
        gar_value = (df["Normalized_Weight"] * (df["EU Taxonomy alignment"] / 100.0)).sum()

        return float(gar_value)
    except Exception:
        return None

def status_badge(value, thresholds, reverse=False):
    if value is None:
        return '<span class="status-badge status-mid">Unavailable</span>'

    good_limit, mid_limit = thresholds

    if not reverse:
        if value <= good_limit:
            return '<span class="status-badge status-good">Favorable</span>'
        elif value <= mid_limit:
            return '<span class="status-badge status-mid">Watchlist</span>'
        else:
            return '<span class="status-badge status-bad">Critical</span>'
    else:
        if value >= good_limit:
            return '<span class="status-badge status-good">Favorable</span>'
        elif value >= mid_limit:
            return '<span class="status-badge status-mid">Watchlist</span>'
        else:
            return '<span class="status-badge status-bad">Critical</span>'

def format_value(value, decimals=3):
    if value is None:
        return "N/A"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:.{decimals}f}"

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
                if len(portfolio_df.columns) == 1:
                    uploaded_file.seek(0)
                    portfolio_df = pd.read_csv(uploaded_file)
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

st.sidebar.markdown("---")
st.sidebar.caption("Climate Risk Dashboard")
st.sidebar.caption("Enterprise portfolio analytics")

# =========================================================
# LOAD INDICATOR SUMMARIES
# =========================================================
waci_summary = load_summary("data/waci/dashboard_summary.csv")
physical_summary = load_summary("data/physical_risk/dashboard_summary.csv")
gar_summary = load_summary("data/gar/dashboard_summary.csv")
itr_summary = load_summary("data/itr/dashboard_summary.csv")

physical_val = get_first_available_metric(
    physical_summary,
    ["portfolio_indicator", "physical_risk_portfolio", "portfolio_physical_risk", "indicator"]
)

waci_val = get_first_available_metric(
    waci_summary,
    ["portfolio_indicator", "portfolio_waci", "waci_portfolio", "indicator"]
)

gar_val = get_first_available_metric(
    gar_summary,
    ["portfolio_indicator", "portfolio_gar", "gar_portfolio", "gar_ratio", "indicator"]
)

itr_val = get_first_available_metric(
    itr_summary,
    ["portfolio_indicator", "portfolio_itr", "itr_portfolio", "itr", "indicator"]
)

# If a portfolio is uploaded, overwrite GAR with actual computed GAR
if "portfolio_df" in st.session_state:
    uploaded_gar = compute_gar_from_portfolio(st.session_state["portfolio_df"])
    if uploaded_gar is not None:
        gar_val = uploaded_gar

# =========================================================
# HERO HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">Climate Risk & Portfolio Intelligence Dashboard</div>
    <div class="hero-subtitle">
        Enterprise platform for climate exposure analysis, transition alignment and portfolio decision support.
    </div>
    <span class="hero-badge">Enterprise View</span>
    <span class="hero-badge">Finance × Climate</span>
    <span class="hero-badge">Decision Support</span>
</div>
""", unsafe_allow_html=True)

if "portfolio_df" in st.session_state:
    st.markdown(f"""
    <div class="info-card">
        <div class="small-label">Current uploaded portfolio</div>
        <div style="font-size:1.05rem; font-weight:700;">
            {st.session_state['portfolio_filename']}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="info-card">
        <div class="small-label">Current portfolio status</div>
        <div style="font-size:1.05rem; font-weight:700;">
            No uploaded portfolio — default demo datasets are currently used.
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================
st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">Physical Risk</div>
        <div class="kpi-value">{format_value(physical_val)}</div>
        <div class="small-muted">Exposure to climate hazards such as floods and extreme events.</div>
        {status_badge(physical_val, (0.20, 0.50), reverse=False)}
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">WACI</div>
        <div class="kpi-value">{format_value(waci_val)}</div>
        <div class="small-muted">Weighted Average Carbon Intensity of the portfolio.</div>
        {status_badge(waci_val, (100, 300), reverse=False)}
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">GAR</div>
        <div class="kpi-value">{format_value(gar_val)}</div>
        <div class="small-muted">Share of assets aligned with green activities.</div>
        {status_badge(gar_val, (0.50, 0.25), reverse=True)}
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-title">ITR</div>
        <div class="kpi-value">{format_value(itr_val)}</div>
        <div class="small-muted">Implied temperature rise associated with the portfolio trajectory.</div>
        {status_badge(itr_val, (1.5, 2.0), reverse=False)}
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# FINANCE <-> CLIMATE LINK
# =========================================================
st.markdown('<div class="section-title">Why climate matters for financial decision-making</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">Indicator Landscape</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">Portfolio-Level Comparison</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">Suggested Management Actions</div>', unsafe_allow_html=True)

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
