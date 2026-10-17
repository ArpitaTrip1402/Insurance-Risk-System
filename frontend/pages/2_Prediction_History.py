
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

st.markdown("""
<style>

/* =====================================
   1. DARK THEME COLORS
===================================== */

:root {
    --bg-main: #0B1220;
    --bg-card: #142238;
    --bg-card-hover: #1A2D46;
    --bg-input: #101C2E;
    --bg-sidebar: #0D1B2D;
    --border: #2B405B;
    --text-main: #E5EDF8;
    --text-muted: #9FB0C8;
    --accent: #19C3B3;
    --accent-hover: #13A99B;
}

/* Main app background */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
}

/* Main page spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* Top header */
[data-testid="stHeader"] {
    background-color: var(--bg-main) !important;
}

/* Toolbar */
[data-testid="stToolbar"] {
    color: var(--text-main) !important;
}

/* =====================================
   2. SIDEBAR
===================================== */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0D1B2D 0%,
        #102A43 100%
    ) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: var(--text-main) !important;
}

/* =====================================
   3. SIDEBAR TOGGLE ARROW
   Always visible, not hover-dependent
===================================== */

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    opacity: 1 !important;
    visibility: visible !important;
}

/* Toggle button */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
button[kind="header"] {
    opacity: 1 !important;
    visibility: visible !important;
    background-color: #142238 !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 8px rgba(25, 195, 179, 0.15);
}

/* Arrow icon */
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
button[kind="header"] svg {
    color: var(--accent) !important;
    fill: var(--accent) !important;
    stroke: var(--accent) !important;
    opacity: 1 !important;
}

/* Toggle hover */
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover,
[data-testid="collapsedControl"] button:hover,
button[kind="header"]:hover {
    background-color: #1A3650 !important;
    border-color: #5DE8DA !important;
    color: #5DE8DA !important;
}

/* =====================================
   4. HEADINGS AND TEXT
===================================== */

h1, h2, h3, h4, h5, h6 {
    color: var(--text-main) !important;
}

p,
label,
.stMarkdown,
[data-testid="stMarkdownContainer"] {
    color: var(--text-main);
}

.history-subtitle {
    color: var(--text-muted) !important;
    font-size: 15px;
}

/* Captions */
[data-testid="stCaptionContainer"],
.stCaption {
    color: var(--text-muted) !important;
}

/* =====================================
   5. METRIC CARDS
===================================== */

[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
    transition: border-color 0.2s ease,
                transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: var(--accent) !important;
    transform: translateY(-2px);
}

/* Metric labels */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] label {
    color: var(--text-muted) !important;
    opacity: 1 !important;
}

/* Metric values */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: var(--text-main) !important;
    font-weight: 700 !important;
}

/* Metric delta */
[data-testid="stMetricDelta"] {
    color: var(--accent) !important;
}

/* =====================================
   6. BUTTONS
===================================== */

.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: var(--accent) !important;
    color: #061923 !important;
    border: 1px solid var(--accent) !important;
    border-radius: 9px;
    padding: 0.55rem 1rem;
    font-weight: 700;
    transition: background-color 0.2s ease,
                border-color 0.2s ease;
}

.stButton > button p,
.stDownloadButton > button p,
.stFormSubmitButton > button p {
    color: #061923 !important;
    font-weight: 700;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
}

.stButton > button:focus,
.stDownloadButton > button:focus,
.stFormSubmitButton > button:focus {
    box-shadow: 0 0 0 3px rgba(25, 195, 179, 0.25) !important;
    outline: none;
}

/* =====================================
   7. INPUTS AND SELECTBOXES
===================================== */

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
[data-baseweb="input"],
[data-baseweb="textarea"] {
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
    border-color: var(--border) !important;
    border-radius: 8px;
}

/* Input text */
input,
textarea {
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
    caret-color: var(--accent);
}

/* Dropdown text */
[data-baseweb="select"] span {
    color: var(--text-main) !important;
}

/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background-color: var(--bg-card) !important;
    border-color: var(--border) !important;
}

[role="option"] {
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
}

[role="option"]:hover {
    background-color: var(--bg-card-hover) !important;
}

/* =====================================
   8. DATAFRAME AND TABLES
===================================== */

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px;
    overflow: hidden;
}

/* =====================================
   9. CONTAINERS AND EXPANDERS
===================================== */

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: 12px;
}

[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px;
}

[data-testid="stExpander"] summary {
    color: var(--text-main) !important;
}

/* =====================================
   10. ALERTS
===================================== */

[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: var(--text-main) !important;
}

/* =====================================
   11. LINKS AND DIVIDERS
===================================== */

a {
    color: var(--accent) !important;
}

a:hover {
    color: #5DE8DA !important;
}

hr {
    border-color: var(--border) !important;
}

/* =====================================
   12. TABS
===================================== */

[data-testid="stTabs"] button {
    color: var(--text-muted) !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* =====================================
   13. CHARTS
===================================== */

[data-testid="stPlotlyChart"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 8px;
}

/* =====================================
   14. HIDE STREAMLIT MENU AND FOOTER
===================================== */

#MainMenu {
    display: none !important;
    visibility: hidden !important;
}

footer {
    display: none !important;
    visibility: hidden !important;
}

.stDeployButton {
    display: none !important;
}

/* =====================================
   15. SCROLLBAR
===================================== */

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-main);
}

::-webkit-scrollbar-thumb {
    background: #344960;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #526C88;
}

/* =====================================
   16. RESPONSIVE DESIGN
===================================== */

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.8rem 2rem 0.8rem;
    }

    [data-testid="stMetric"] {
        padding: 12px;
    }
}
/* Additional responsive improvements */

/* Prevent content from overflowing */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.block-container {
    min-width: 0;
    max-width: 100%;
}

/* Make buttons fit smaller screens */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    max-width: 100%;
    white-space: normal;
}

/* Keep charts within the available width */
[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"] {
    max-width: 100%;
    min-width: 0;
}

/* Mobile layout */
@media screen and (max-width: 768px) {
    .block-container {
        padding: 1rem 0.75rem !important;
    }

    [data-testid="stMetric"] {
        padding: 12px !important;
        overflow-wrap: anywhere;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.25rem;
    }

    h1 {
        font-size: 1.7rem !important;
    }

    h2 {
        font-size: 1.4rem !important;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        width: 100%;
    }
}

/* Extra-small phones */
@media screen and (max-width: 480px) {
    .block-container {
        padding: 0.75rem 0.5rem !important;
    }

    [data-testid="stMetric"] {
        padding: 10px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }
}

/* =========================================
   MOBILE RESPONSIVE DESIGN
========================================= */

/* Prevent horizontal overflow */
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    max-width: 100%;
    min-width: 0;
    box-sizing: border-box;
}

/* Keep all elements within their containers */
*,
*::before,
*::after {
    box-sizing: border-box;
}

/* Tablet and mobile */
@media screen and (max-width: 768px) {

    .main .block-container {
        padding: 1.25rem 1rem 2rem 1rem !important;
        max-width: 100% !important;
    }

    /* Responsive page headings */
    h1 {
        font-size: clamp(1.65rem, 6vw, 2.2rem) !important;
        line-height: 1.3 !important;
        overflow-wrap: anywhere;
    }

    h2 {
        font-size: 1.4rem !important;
        line-height: 1.35 !important;
    }

    h3 {
        font-size: 1.2rem !important;
    }

    /* Body text */
    p,
    .history-subtitle,
    [data-testid="stMarkdownContainer"] {
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .history-subtitle {
        font-size: 0.98rem !important;
        line-height: 1.65 !important;
    }

    /* Buttons: comfortable mobile touch targets */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        min-height: 44px;
        max-width: 100%;
        white-space: normal !important;
        overflow-wrap: anywhere;
        font-size: 0.95rem !important;
        padding: 0.65rem 0.8rem !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        padding: 12px !important;
        min-width: 0;
        overflow: hidden;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        white-space: normal !important;
    }

    [data-testid="stMetricValue"] {
        font-size: clamp(1rem, 4vw, 1.4rem) !important;
        overflow-wrap: anywhere;
    }

    /* Tables and dataframes */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        max-width: 100%;
        min-width: 0;
    }

    /* Charts */
    [data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100%;
        min-width: 0;
        padding: 4px !important;
    }

    /* Inputs and dropdowns */
    [data-testid="stTextInput"],
    [data-testid="stNumberInput"],
    [data-testid="stSelectbox"],
    [data-testid="stDateInput"],
    [data-testid="stMultiSelect"] {
        width: 100%;
        min-width: 0;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        padding: 0.8rem !important;
        overflow-wrap: anywhere;
    }

    /* Reduce excess divider spacing */
    hr {
        margin-top: 1.25rem !important;
        margin-bottom: 1.25rem !important;
    }
}

/* Small mobile phones */
@media screen and (max-width: 480px) {

    .main .block-container {
        padding: 1rem 0.75rem 1.5rem 0.75rem !important;
    }

    h1 {
        font-size: 1.55rem !important;
        line-height: 1.35 !important;
    }

    h2 {
        font-size: 1.25rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    .history-subtitle {
        font-size: 0.92rem !important;
    }

    [data-testid="stMetric"] {
        padding: 10px !important;
        border-radius: 10px !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        width: 100%;
    }

    [data-testid="stPlotlyChart"] {
        padding: 0 !important;
    }
}

/* =========================================
   MOBILE HEADER AND SIDEBAR TOGGLE FIX
========================================= */

@media screen and (max-width: 768px) {

    /* Reduce excess space above the page heading */
    [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding-top: 0.6rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }


    /* Keep the Streamlit header compact */
    [data-testid="stHeader"] {
        height: 2.5rem !important;
        min-height: 2.5rem !important;
    }

    /* Reduce space around the sidebar toggle */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        width: 2rem !important;
        min-width: 2rem !important;
        height: 2rem !important;
        min-height: 2rem !important;
        padding: 0.2rem !important;
        border-radius: 6px !important;
    }

    /* Prevent the title and buttons from overflowing */
    .stButton > button {
        max-width: 100%;
        white-space: normal !important;
    }
}

/* Extra-small phones */
@media screen and (max-width: 480px) {
    [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding-top: 0.4rem !important;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
    }

    h1 {
        font-size: 1.35rem !important;
    }
}


</style>
""", unsafe_allow_html=True)

 


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
