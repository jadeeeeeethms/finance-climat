import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px

st.set_page_config(page_title="GAR Module", layout="wide")


# =========================================================
# HELPERS
# =========================================================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    rename_map = {
        "Company Name": "Company name",
        "Nace Code": "NACE Code",
        "Portfolio Weight %": "Portfolio Weight (%)",
        "Portfolio weight (%)": "Portfolio Weight (%)",
        "Taxonomy eligibility": "Taxonomy Eligibility",
        "EU Taxonomy alignment (%)": "EU Taxonomy alignment",
        "EU taxonomy alignment": "EU Taxonomy alignment",
    }

    df.rename(columns=rename_map, inplace=True)
    return df


def clean_numeric_series(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.str.replace(" ", "", regex=False)
    s = s.str.replace("%", "", regex=False)
    s = s.str.replace(",", ".", regex=False)
    s = s.replace(["", "nan", "None", "NA", "N/A", "null"], pd.NA)
    return pd.to_numeric(s, errors="coerce")


# =========================================================
# MAIN GAR FUNCTION
# =========================================================
def run_gar_module(df: pd.DataFrame):
    st.header("Green Asset Ratio (GAR) & Portfolio Optimization")

    df = normalize_columns(df)

    required_cols = [
        "Company name",
        "NACE Code",
        "Portfolio Weight (%)",
        "Taxonomy Eligibility",
        "EU Taxonomy alignment"
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing mandatory columns in the uploaded file: {missing_cols}")
        with st.expander("Detected columns"):
            st.write(list(df.columns))
        return

    df = df.copy()

    df["Company name"] = df["Company name"].astype(str).str.strip()
    df["NACE Code"] = df["NACE Code"].astype(str).str.strip()
    df["Taxonomy Eligibility"] = df["Taxonomy Eligibility"].astype(str).str.strip()

    df["Portfolio Weight (%)"] = clean_numeric_series(df["Portfolio Weight (%)"])
    df["EU Taxonomy alignment"] = clean_numeric_series(df["EU Taxonomy alignment"]).fillna(0)

    df = df.dropna(subset=["Portfolio Weight (%)"])

    if df.empty:
        st.error("No valid rows remain after cleaning the portfolio.")
        return

    # Exclude financial sector K from denominator
    df["Is_Financial"] = df["NACE Code"].str.upper().str.startswith("K")
    df_nfc = df[~df["Is_Financial"]].copy()

    if df_nfc.empty:
        st.error("No eligible Non-Financial Corporations (NFCs) found in the dataset.")
        return

    total_weight = df_nfc["Portfolio Weight (%)"].sum()

    if total_weight <= 0:
        st.error("Portfolio Weight (%) must have a strictly positive total.")
        return

    df_nfc["Normalized_Weight"] = df_nfc["Portfolio Weight (%)"] / total_weight

    # Traceability
    df_nfc["Data_Source"] = np.where(
        df_nfc["Taxonomy Eligibility"].str.upper().isin(["X", "NO", "N", "0"]),
        "Proxy (Estimated)",
        "Reported"
    )

    # Sidebar settings
    st.sidebar.subheader("GAR Optimization Settings")
    cap_limit = st.sidebar.slider(
        "Max Weight Cap per Issuer (%)",
        min_value=5,
        max_value=30,
        value=15,
        key="gar_cap"
    ) / 100.0

    current_gar = np.sum(
        df_nfc["Normalized_Weight"] * (df_nfc["EU Taxonomy alignment"] / 100.0)
    )

    def objective_function(weights):
        return -np.sum(weights * (df_nfc["EU Taxonomy alignment"].values / 100.0))

    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0, cap_limit) for _ in range(len(df_nfc)))

    run_optimization = st.sidebar.button("Run GAR Optimization", key="run_gar_optimization")

    if not run_optimization:
        st.info("Set parameters in the sidebar and click 'Run GAR Optimization'.")
        return

    initial_weights = df_nfc["Normalized_Weight"].values

    result = minimize(
        objective_function,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:
        st.error("Optimization failed. Check constraints.")
        st.write(result.message)
        return

    df_nfc["Optimized_Weight"] = result.x
    optimized_gar = -result.fun

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Baseline GAR", f"{current_gar * 100:.2f}%")

    with col2:
        st.metric(
            "Optimized GAR",
            f"{optimized_gar * 100:.2f}%",
            delta=f"{(optimized_gar - current_gar) * 100:.2f} pp"
        )

    with col3:
        dqs_score = (
            df_nfc.loc[df_nfc["Data_Source"] == "Reported", "Normalized_Weight"].sum() * 100
        )
        st.metric("Data Quality Score (Reported Data)", f"{dqs_score:.0f}%")

    st.divider()

    # Chart 1
    st.subheader("Capital Reallocation Strategy")

    df_chart = df_nfc.melt(
        id_vars=["Company name", "EU Taxonomy alignment"],
        value_vars=["Normalized_Weight", "Optimized_Weight"],
        var_name="Scenario",
        value_name="Weight"
    )

    fig_bar = px.bar(
        df_chart,
        x="Company name",
        y="Weight",
        color="Scenario",
        barmode="group",
        hover_data=["EU Taxonomy alignment"]
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Chart 2
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("GAR Data Traceability")
        fig_proxy = px.pie(
            df_nfc,
            values="Optimized_Weight",
            names="Data_Source",
            hole=0.4,
            title="Portfolio Weight by Data Source"
        )
        st.plotly_chart(fig_proxy, use_container_width=True)

    with col_right:
        st.subheader("Sector Breakdown")
        fig_sector = px.pie(
            df_nfc,
            values="Optimized_Weight",
            names="NACE Code",
            title="Optimized Weight by NACE Sector"
        )
        st.plotly_chart(fig_sector, use_container_width=True)

    # Table
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
        use_container_width=True
    )

    # Optional debug
    with st.expander("Debug GAR input"):
        st.write("Detected columns:", list(df.columns))
        st.write("Portfolio Weight (%) sample:", df["Portfolio Weight (%)"].head(10).tolist())
        st.write("EU Taxonomy alignment sample:", df["EU Taxonomy alignment"].head(10).tolist())
        st.write("Taxonomy Eligibility sample:", df["Taxonomy Eligibility"].head(10).tolist())


# =========================================================
# PAGE EXECUTION
# =========================================================
portfolio_df = st.session_state.get("portfolio_df", None)

if portfolio_df is None:
    st.warning("Please upload a portfolio from the sidebar.")
else:
    run_gar_module(portfolio_df)
