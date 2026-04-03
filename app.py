import streamlit as st

st.set_page_config(
    page_title="Climate Risk Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    .hero-box {
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        padding: 2.2rem 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
    }

    .card {
        background: white;
        padding: 1.3rem 1.2rem;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
        border: 1px solid #e5e7eb;
        min-height: 180px;
    }

    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #111827;
    }

    .card-text {
        font-size: 0.98rem;
        color: #374151;
    }

    .section-title {
        font-size: 1.7rem;
        font-weight: 800;
        color: #111827;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }

    .small-note {
        color: #475569;
        font-size: 0.95rem;
    }

    div[data-testid="stSidebar"] {
        background: #eef2ff;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero-box">
    <div class="hero-title">Climate Risk Dashboard</div>
    <div class="hero-subtitle">
        A multi-indicator dashboard to analyze the same portfolio through different climate and sustainability lenses.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# INTRO
# =========================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## What this application does")
    st.write("""
This dashboard helps users understand a portfolio through several complementary indicators.

Each page focuses on one indicator and answers three questions:
- **What does it measure?**
- **How should I read it?**
- **What can I do with this information?**
""")

with col2:
    st.info("""
**General reading rule**
- Lower value = lower risk  
- Higher value = more caution needed  

This rule may vary depending on the indicator.  
See the **Indicator Guide** page for details.
""")

# =========================
# INDICATOR CARDS
# =========================
st.markdown('<div class="section-title">Available indicators</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="card">
        <div class="card-title">🌊 Physical Risk</div>
        <div class="card-text">
            Measures exposure to physical climate hazards such as flood risk.
            Useful to identify risky countries, sectors and assets.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
        <div class="card-title">🏭 WACI</div>
        <div class="card-text">
            Weighted Average Carbon Intensity.  
            Helps assess transition risk and carbon exposure of the portfolio.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card">
        <div class="card-title">🌱 GAR</div>
        <div class="card-text">
            Green Asset Ratio.  
            Shows the share of portfolio assets aligned with green or sustainable activities.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="card">
        <div class="card-title">🌡️ ITR</div>
        <div class="card-text">
            Implied Temperature Rise.  
            Measures the estimated global temperature increase implied by the portfolio's trajectory.
        </div>
    </div>
    """, unsafe_allow_html=True)
# =========================
# HOW TO USE
# =========================
st.markdown('<div class="section-title">How to use the dashboard</div>', unsafe_allow_html=True)

a, b, c = st.columns(3)
a.success("1. Open the **Indicator Guide** page")
b.info("2. Explore one indicator page at a time")
c.warning("3. Compare insights before making a decision")

st.markdown("""
<div class="small-note">
Use the sidebar to navigate between pages.  
For the best reading experience, start with <b>Indicator Guide</b>, then open each indicator page.
</div>
""", unsafe_allow_html=True)

# =========================
# FOOTER MESSAGE
# =========================
st.markdown("---")
st.write("""
This dashboard is designed for users who want both:
- a **global portfolio overview**
- and a **simple interpretation** of each climate indicator.
""")
