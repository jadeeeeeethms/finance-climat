import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px

# =========================================================
# HELPERS
# =========================================================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Robust column cleaning:
    - strip spaces
    - remove duplicated spaces
    - standardize known variants
    """
    df = df.copy()

    # Clean raw column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Rename known variants to canonical names
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


def run_gar_module(df: pd.DataFrame):
    st.header("Green Asset Ratio (GAR) & Portfolio Optimization")

    # =====================================================
    # 0. Robust cleaning
    # =====================================================
    df = normalize_columns(df)

    required_cols = [
        "Company name",
        "NACE Code",
        "Portfolio Weight (%)",
        "Taxonomy Eligibility",
        "EU Taxonomy alignment",
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing mandatory columns in the uploaded file: {missing_cols}")
        st.write("Detected columns:")
        st.write(list(df.columns))
        return

    # =====================================================
    # 1. Type cleaning
    # =====================================================
    df = df.copy()

    df["Company name"] = df["Company name"].astype(str).str.strip()
    df["NACE Code"] = df["NACE Code"].astype(str).str.strip()
    df["Taxonomy Eligibility"] = df["Taxonomy Eligibility"].astype(str).str.strip()

    df["Portfolio Weight (%)"] = pd.to_numeric(
        df["Portfolio Weight (%)"], errors="coerce"
    )
    df["EU Taxonomy alignment"] = pd.to_numeric(
        df["EU Taxonomy alignment"], errors="coerce"
    ).fillna(0)

    # Remove invalid rows
    df = df.dropna(subset=["Portfolio Weight (%)"])

    if df.empty:
        st.error("No valid rows remain after cleaning the uploaded portfolio.")
        return

    # =====================================================
    # 2. NFC filter
    # =====================================================
    df["Is_Financial"] = df["NACE Code"].str.upper().str.startswith("K")
    df_nfc = df[~df["Is_Financial"]].copy()

    if df_nfc.empty:
        st.error("No eligible Non-Financial Corporations (NFCs) found in the dataset.")
        return

    # =====================================================
    # 3. Normalize weights
    # =====================================================
    total_weight = df_nfc["Portfolio Weight (%)"].sum()

    if total_weight <= 0:
        st.error("Portfolio Weight (%) must have a strictly positive total.")
        return

    df_nfc["Normalized_Weight"] = df_nfc["Portfolio Weight (%)"] / total_weight

    # Traceability logic
    df_nfc["Data_Source"] = np.where(
        df_nfc["Taxonomy Eligibility"].str.upper().isin(["X", "NO", "N", "0"]),
        "Proxy (Estimated)",
        "Reported",
    )

    # =====================================================
    # 4. Sidebar parameters
    # =====================================================
    st.sidebar.subheader("GAR Optimization Settings")
    cap_limit = st.sidebar.slider(
        "Max Weight Cap per Issuer (%)", 5, 30, 15, key="gar_cap"
    ) / 100.0

    # =====================================================
    # 5. Current GAR
    # =====================================================
    current_gar = np.sum(
        df_nfc["Normalized_Weight"] * (df_nfc["EU Taxonomy alignment"] / 100.0)
    )

    def objective_function(weights):
        return -np.sum(weights * (df_nfc["EU Taxonomy alignment"].values / 100.0))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0, cap_limit) for _ in range(len(df_nfc)))

    run_optimization = st.sidebar.button("Run GAR Optimization")

    if not run_optimization:
        st.info("Set parameters in the sidebar and click 'Run GAR Optimization'.")
        return

    # =====================================================
    # 6. Optimization
    # =====================================================
    initial_weights = df_nfc["Normalized_Weight"].values

    result = minimize(
        objective_function,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if not result.success:
        st.error("Optimization failed. Check constraints.")
        st.write(result.message)
        return

    df_nfc["Optimized_Weight"] = result.x
    optimized_gar = -result.fun

    # =====================================================
    # 7. KPIs
    # =====================================================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Baseline GAR", f"{current_gar*100:.2f}%")

    with col2:
        st.metric(
            "Optimized GAR",
            f"{optimized_gar*100:.2f}%",
            delta=f"{(optimized_gar-current_gar)*100:.2f} pp",
        )

    with col3:
        dqs_score = (
            df_nfc.loc[df_nfc["Data_Source"] == "Reported", "Normalized_Weight"].sum()
            * 100
        )
        st.metric("Data Quality Score (Reported Data)", f"{dqs_score:.0f}%")

    st.divider()

    # =====================================================
    # 8. Charts
    # =====================================================
    st.subheader("Capital Reallocation Strategy")

    df_chart = df_nfc.melt(
        id_vars=["Company name", "EU Taxonomy alignment"],
        value_vars=["Normalized_Weight", "Optimized_Weight"],
        var_name="Scenario",
        value_name="Weight",
    )

    fig_bar = px.bar(
        df_chart,
        x="Company name",
        y="Weight",
        color="Scenario",
        barmode="group",
        hover_data=["EU Taxonomy alignment"],
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("GAR Data Traceability")
        fig_proxy = px.pie(
            df_nfc,
            values="Optimized_Weight",
            names="Data_Source",
            hole=0.4,
            title="Portfolio Weight by Data Source",
        )
        st.plotly_chart(fig_proxy, use_container_width=True)

    with col_right:
        st.subheader("Sector Breakdown")
        fig_sector = px.pie(
            df_nfc,
            values="Optimized_Weight",
            names="NACE Code",
            title="Optimized Weight by NACE Sector",
        )
        st.plotly_chart(fig_sector, use_container_width=True)

    # =====================================================
    # 9. Detailed table
    # =====================================================
    st.subheader("Detailed Portfolio Data")
    st.dataframe(
        df_nfc[
            [
                "Company name",
                "NACE Code",
                "Taxonomy Eligibility",
                "Data_Source",
                "EU Taxonomy alignment",
                "Portfolio Weight (%)",
                "Normalized_Weight",
                "Optimized_Weight",
            ]
        ],
        use_container_width=True,
    )


# =========================================================
# PAGE EXECUTION
# =========================================================
st.set_page_config(page_title="GAR Module", layout="wide")

if "portfolio_df" not in st.session_state:
    st.warning("Please upload a portfolio from the sidebar on the main app first.")
else:
    run_gar_module(st.session_state["portfolio_df"])
