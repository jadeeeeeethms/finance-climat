import streamlit as st

st.set_page_config(
    page_title="Indicator Guide",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.12);
        margin-bottom: 1.4rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
    }

    .hero p {
        margin-top: 0.5rem;
        font-size: 1rem;
        opacity: 0.95;
    }

    .guide-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.2rem 1.2rem;
        box-shadow: 0 6px 16px rgba(15,23,42,0.07);
        margin-bottom: 1rem;
    }

    .guide-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.6rem;
    }

    .mini-tag-good {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: #dcfce7;
        color: #166534;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .mini-tag-bad {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: #fee2e2;
        color: #991b1b;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #111827;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stSidebar"] {
        background: #eef2ff;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>Indicator Guide</h1>
    <p>
        This page explains what each climate indicator measures, how to read it,
        and what action a user can take from the result.
    </p>
</div>
""", unsafe_allow_html=True)

st.info("""
A dashboard is useful only if the user understands:
- what the indicator measures,
- whether a high value is good or bad,
- and what decision should follow.
""")

st.markdown('<div class="section-title">General reading rules</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.success("""
**Indicators where lower is better**
- Physical Exposure Risk
- WACI
- Financed Emissions
- ITR
""")

with col2:
    st.success("""
**Indicator where higher is better**
- GAR
""")

# =========================
# WACI
# =========================
st.markdown("""
<div class="guide-card">
    <div class="guide-title">🏭 WACI — Weighted Average Carbon Intensity</div>
    <p><b>What it measures:</b> the carbon intensity of the portfolio, computed as the weighted average of counterparties’ emissions intensity relative to revenue.</p>
    <p><b>Main idea:</b> it tells you how carbon-intensive the portfolio is from a transition-risk perspective.</p>
    <p><b>Unit:</b> tCO2e / EUR million revenue.</p>
    <p><b>Interpretation:</b> a high WACI means the portfolio is more exposed to carbon-intensive counterparties; a low WACI means the portfolio is less carbon-intensive.</p>
    <p><span class="mini-tag-bad">Lower is better</span></p>
    <p><b>What to do:</b> prioritize sectors, countries and counterparties with the lowest contributions to WACI.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# FINANCED EMISSIONS
# =========================
st.markdown("""
<div class="guide-card">
    <div class="guide-title">🌍 Financed Emissions</div>
    <p><b>What it measures:</b> the absolute GHG emissions attributable to the portfolio using an attribution factor based on exposure and denominator such as EVIC.</p>
    <p><b>Main idea:</b> unlike WACI, this is an absolute emissions indicator, not an intensity indicator.</p>
    <p><b>Unit:</b> tCO2e.</p>
    <p><b>Interpretation:</b> a high value means the portfolio finances more real-economy emissions in absolute terms.</p>
    <p><span class="mini-tag-bad">Lower is better</span></p>
    <p><b>What to do:</b> use it to identify the biggest absolute contributors by sector, country and counterparty.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# GAR
# =========================
st.markdown("""
<div class="guide-card">
    <div class="guide-title">🌱 GAR — Green Asset Ratio</div>
    <p><b>What it measures:</b> the proportion of portfolio assets aligned with EU Taxonomy activities.</p>
    <p><b>Main idea:</b> it is a greenness ratio, not a risk ratio. In your specification, it also supports optimization to maximize GAR under diversification constraints.</p>
    <p><b>Unit:</b> % of covered assets.</p>
    <p><b>Interpretation:</b> a higher GAR means a larger share of the portfolio is aligned with green activities.</p>
    <p><span class="mini-tag-good">Higher is better</span></p>
    <p><b>What to do:</b> compare current GAR and optimized GAR, and identify green sectors and assets that increase alignment without excessive concentration.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# PHYSICAL RISK
# =========================
st.markdown("""
<div class="guide-card">
    <div class="guide-title">🌊 Physical Exposure Risk</div>
    <p><b>What it measures:</b> the monetary value of assets exposed to a physical climate hazard such as floods, heat stress, wildfires or droughts.</p>
    <p><b>Main idea:</b> the indicator is based on the spatial intersection between asset locations and hazard maps.</p>
    <p><b>Unit:</b> EUR / USD.</p>
    <p><b>Interpretation:</b> a higher value means more assets or more value are exposed to the selected hazard.</p>
    <p><span class="mini-tag-bad">Lower is better</span></p>
    <p><b>What to do:</b> identify the most exposed countries, sectors and assets, and review concentration in hazard-prone areas.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# ITR
# =========================
st.markdown("""
<div class="guide-card">
    <div class="guide-title">🌡️ ITR — Implied Temperature Rise</div>
    <p><b>What it measures:</b> the estimated global warming trajectory implied by the portfolio if all companies followed their projected emissions pathway.</p>
    <p><b>Main idea:</b> it is forward-looking and scenario-dependent, unlike WACI or Financed Emissions which focus on current emissions profiles.</p>
    <p><b>Unit:</b> °C.</p>
    <p><b>Interpretation:</b> a higher ITR means the portfolio is less aligned with Paris Agreement climate pathways.</p>
    <p><span class="mini-tag-bad">Lower is better</span></p>
    <p><b>What to do:</b> compare the portfolio ITR with scenario baselines, and focus on counterparties with high ITR and weak reduction pathways.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">How to read the graphs</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
**Maps**
- each point usually represents one asset or one counterparty,
- point size often reflects exposure or contribution,
- point color often reflects risk level, sector, or hazard intensity.
""")

    st.markdown("""
**Bar charts**
- used to compare countries, sectors or counterparties,
- high bars can mean either “worse” or “better” depending on the indicator,
- always check the page rule first.
""")

with c2:
    st.markdown("""
**KPI cards**
- highlight the main portfolio-level number,
- useful for a quick reading,
- should always be interpreted together with breakdowns.
""")

    st.markdown("""
**Tables**
- help identify top contributors,
- useful for drill-down analysis,
- should include exclusions, proxies, and data quality when available.
""")

st.markdown('<div class="section-title">Decision logic by indicator</div>', unsafe_allow_html=True)

decision_df = pd.DataFrame({
    "Indicator": ["WACI", "Financed Emissions", "GAR", "Physical Exposure Risk", "ITR"],
    "Main question": [
        "How carbon-intensive is the portfolio today?",
        "How much absolute emissions does the portfolio finance?",
        "How green is the portfolio?",
        "How much value is physically exposed to hazards?",
        "How aligned is the portfolio with climate scenarios?"
    ],
    "Preferred direction": [
        "Lower",
        "Lower",
        "Higher",
        "Lower",
        "Lower"
    ],
    "Typical action": [
        "Reduce high-carbon contributors",
        "Reduce biggest absolute emitters",
        "Increase green aligned assets",
        "Reduce concentration in exposed areas",
        "Prioritize counterparties with stronger transition pathways"
    ]
})

st.dataframe(decision_df, use_container_width=True)

st.markdown("---")
st.write("""
This guide is based on the project specification and should remain aligned with the
actual calculation logic implemented in each indicator page.
""")
