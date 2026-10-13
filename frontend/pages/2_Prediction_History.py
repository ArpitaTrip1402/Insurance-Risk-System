
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Prediction History | Insurance Risk Analyzer",
    page_icon="📜",
    layout="wide"

)


import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
HISTORY_URL = f"{API_URL}/history"

# --------------------------------------------------
# 2. Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    
/* Match the light background on both pages */
.stApp {
    background-color: #F4F7FC !important;
}

/* Light Streamlit top header */
[data-testid="stHeader"] {
    background-color: #F4F7FC !important;
}

/* Keep the top toolbar readable */
[data-testid="stToolbar"] {
    color: #12304A !important;
}

/* Ensure metric text stays readable */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #526780 !important;
    opacity: 1 !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #12304A !important;
}

    /* Main page */
    .stApp {
        background-color: #F4F7FC;
        color: #172B4D;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102A43 0%, #163D5C 100%);
    }

    [data-testid="stSidebar"] * {
        color: #F0F6FC;
    }

    /* Headings */
    h1, h2, h3 {
        color: #12304A !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #DFE7F1;
        box-shadow: 0 3px 12px rgba(20, 48, 74, 0.06);
    }

    [data-testid="stMetricLabel"] {
        color: #526780 !important;
    }

    [data-testid="stMetricValue"] {
        color: #12304A !important;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background: #087E8B;
        color: #FFFFFF !important;
        border: 1px solid #087E8B;
        border-radius: 9px;
        padding: 0.55rem 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease,
                    border-color 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #066570;
        border-color: #066570;
        color: #FFFFFF !important;
    }

    .stButton > button:focus,
    .stDownloadButton > button:focus {
        box-shadow: 0 0 0 3px rgba(8, 126, 139, 0.25);
        outline: none;
    }

    /* Input fields */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF;
        border-color: #CCD8E5;
        border-radius: 8px;
    }

    /* Dataframe container */
    [data-testid="stDataFrame"] {
        background: #FFFFFF;
        border: 1px solid #DFE7F1;
        border-radius: 12px;
        overflow: hidden;
    }

    /* General text */
    .history-subtitle {
        color: #526780;
        font-size: 15px;
    }

    hr {
        border-color: #DFE7F1;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 3. Header
# --------------------------------------------------

st.title("📜 Prediction History")

if st.button("← Back to Analyzer"):
    st.switch_page("app.py")

st.markdown(
    '<p class="history-subtitle">'
    'Explore historical insurance predictions, analyze risk '
    'patterns, and review saved applicant records.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# 4. Fetch records from FastAPI / PostgreSQL
# --------------------------------------------------

@st.cache_data(ttl=30)
def fetch_history():
    response = requests.get(HISTORY_URL, timeout=30)
    response.raise_for_status()

    records = response.json()

    if not isinstance(records, list):
        raise ValueError("Unexpected history API response.")

    return records


if st.button("🔄 Refresh History"):
    fetch_history.clear()

try:
    records = fetch_history()

except requests.exceptions.ConnectionError:
    st.error(
        "Cannot connect to FastAPI. Start your backend with "
        "`uvicorn src.api:app --reload`."
    )
    st.stop()

except requests.exceptions.Timeout:
    st.error("The history request timed out. Please try again.")
    st.stop()

except requests.exceptions.HTTPError as exc:
    st.error(f"History API returned an error: {exc}")
    st.stop()

except (ValueError, requests.exceptions.RequestException) as exc:
    st.error(f"Unable to load prediction history: {exc}")
    st.stop()

if not records:
    st.info(
        "No prediction history found yet. Make a prediction "
        "on the Insurance Risk Analyzer page first."
    )
    st.stop()

# --------------------------------------------------
# 5. Prepare data
# --------------------------------------------------

df = pd.DataFrame(records)

required_columns = [
    "id",
    "age",
    "sex",
    "bmi",
    "children",
    "smoker",
    "region",
    "predicted_charge",
    "risk_category",
    "created_at",
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "The history API is missing expected fields: "
        + ", ".join(missing_columns)
    )
    st.stop()

df["predicted_charge"] = pd.to_numeric(
    df["predicted_charge"], errors="coerce"
)

df["created_at"] = pd.to_datetime(
    df["created_at"], errors="coerce", utc=True
)

df["created_at"] = df["created_at"].dt.tz_convert(
    "Asia/Kolkata"
)

df["created_at"] = df["created_at"].dt.tz_localize(None)

df = df.dropna(subset=["predicted_charge"])

# --------------------------------------------------
# 6. Overall summary metrics
# --------------------------------------------------

st.subheader("Overview")

total_predictions = len(df)
average_charge = df["predicted_charge"].mean()
highest_charge = df["predicted_charge"].max()

high_risk_count = (
    df["risk_category"] == "High Risk"
).sum()


col1, col2, col3, col4 = st.columns(
    [0.9, 1.15, 1.35, 1.1],
    gap="medium"
)

col1.metric(
    "Total Predictions",
    f"{total_predictions:,}"
)

col2.metric(
    "Average Predicted Charge",
    f"${average_charge:,.2f}"
)

col3.metric(
    "Highest Predicted Charge",
    f"${highest_charge:,.2f}"
)

col4.metric(
    "High-Risk Predictions",
    f"{high_risk_count:,}"
)

st.caption(
    "Overview metrics are calculated from the loaded prediction "
    "history (up to the latest 100 records). Charges are in USD."
)

st.divider()

# --------------------------------------------------
# 7. Filters
# --------------------------------------------------

st.subheader("Explore Records")

filter1, filter2, filter3 = st.columns([1, 1, 2])

risk_options = ["All"] + sorted(
    df["risk_category"].dropna().unique().tolist()
)

smoker_options = ["All"] + sorted(
    df["smoker"].dropna().unique().tolist()
)

with filter1:
    selected_risk = st.selectbox(
        "Risk Category",
        risk_options
    )

with filter2:
    selected_smoker = st.selectbox(
        "Smoker Status",
        smoker_options
    )

with filter3:
    search_id = st.text_input(
        "Search Prediction ID",
        placeholder="Enter a prediction ID..."
    ).strip()

filtered_df = df.copy()

if selected_risk != "All":
    filtered_df = filtered_df[
        filtered_df["risk_category"] == selected_risk
    ]

if selected_smoker != "All":
    filtered_df = filtered_df[
        filtered_df["smoker"] == selected_smoker
    ]

if search_id:
    if search_id.isdigit():
        filtered_df = filtered_df[
            filtered_df["id"] == int(search_id)
        ]
    else:
        filtered_df = filtered_df.iloc[0:0]

st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} loaded records."
)

# --------------------------------------------------
# 8. Charts
# --------------------------------------------------

st.subheader("Risk Analytics")

if filtered_df.empty:
    st.warning("No records match your selected filters.")

else:
    chart1, chart2 = st.columns(2)

    with chart1:
        risk_counts = (
            filtered_df["risk_category"]
            .value_counts()
            .rename_axis("Risk Category")
            .reset_index(name="Count")
        )

        fig_risk = px.pie(
            risk_counts,
            names="Risk Category",
            values="Count",
            hole=0.55,
            title="Risk Category Distribution",
            color="Risk Category",
            color_discrete_map={
                "Low Risk": "#16A34A",
                "Medium Risk": "#F59E0B",
                "High Risk": "#DC2626",
            },
        )

        fig_risk.update_layout(
            legend_title_text="Risk Category",
            margin=dict(t=60, b=20, l=20, r=20),
        )

        st.plotly_chart(
            fig_risk,
            use_container_width=True
        )

    with chart2:
        fig_charge = px.histogram(
            filtered_df,
            x="predicted_charge",
            color="risk_category",
            nbins=20,
            title="Distribution of Predicted Charges",
            labels={
                "predicted_charge": "Predicted Charge (USD)",
                "risk_category": "Risk Category",
                "count": "Number of Predictions",
            },
            color_discrete_map={
                "Low Risk": "#16A34A",
                "Medium Risk": "#F59E0B",
                "High Risk": "#DC2626",
            },
        )

        fig_charge.update_layout(
            legend_title_text="Risk Category",
            margin=dict(t=60, b=20, l=20, r=20),
        )

        st.plotly_chart(
            fig_charge,
            use_container_width=True
        )

st.divider()

# --------------------------------------------------
# 9. Prediction history table
# --------------------------------------------------

st.subheader("Saved Prediction Records")

if filtered_df.empty:
    st.info("No prediction records to display.")

else:
    display_df = filtered_df[
        [
            "id",
            "created_at",
            "age",
            "sex",
            "bmi",
            "children",
            "smoker",
            "region",
            "predicted_charge",
            "risk_category",
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "id": "Prediction ID",
            "created_at": "Date & Time (IST)",
            "age": "Age",
            "sex": "Sex",
            "bmi": "BMI",
            "children": "Children",
            "smoker": "Smoker",
            "region": "Region",
            "predicted_charge": "Predicted Charge (USD)",
            "risk_category": "Risk Category",
        }
    )

    display_df["Predicted Charge (USD)"] = (
        display_df["Predicted Charge (USD)"].round(2)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prediction ID": st.column_config.NumberColumn(
                format="%d"
            ),
            "Predicted Charge (USD)": st.column_config.NumberColumn(
                format="$%.2f"
            ),
            "BMI": st.column_config.NumberColumn(
                format="%.2f"
            ),
            "Date & Time (IST)": st.column_config.DatetimeColumn(
                format="DD MMM YYYY, hh:mm A"
            ),
        },
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Export Filtered History as CSV",
        data=csv_data,
        file_name="insurance_prediction_history.csv",
        mime="text/csv",
    )

st.divider()

st.caption(
    "Insurance Risk Analyzer · Prediction history retrieved "
    "from your FastAPI backend and PostgreSQL database."
)
