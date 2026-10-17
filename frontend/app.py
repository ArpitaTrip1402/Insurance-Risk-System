import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Insurance Risk Analyzer",
    page_icon="📊",
    layout="wide"
)

import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

#
# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown("""
<style>

/* =========================================
   1. GLOBAL DARK THEME
========================================= */

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

.stApp {
    background: var(--bg-main);
    color: var(--text-main);
}

/* Main content area */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2.5rem;
    max-width: 1500px;
}

/* Default text */
html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stMain"] {
    background-color: var(--bg-main);
    color: var(--text-main);
}

h1, h2, h3, h4, h5, h6,
p, label, li, span,
.stMarkdown,
[data-testid="stMarkdownContainer"] {
    color: var(--text-main);
}

/* Muted helper text */
small,
.stCaption,
[data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
}

/* Header area */
[data-testid="stHeader"] {
    background: rgba(11, 18, 32, 0.95);
}

/* =========================================
   2. SIDEBAR
========================================= */

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0D1B2D 0%,
        #10253B 100%
    );
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: var(--text-main);
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: var(--border);
}

/* =========================================
   3. SIDEBAR COLLAPSE / EXPAND TOGGLE
   Keep the toggle visible without hover.
========================================= */

/* Streamlit toggle selectors vary by version */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="header"] {
    opacity: 1 !important;
    visibility: visible !important;
}

/* Toggle button styling */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
button[kind="header"] {
    background-color: #142238 !important;
    color: var(--accent) !important;
    border: 1px solid #19C3B3 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(25, 195, 179, 0.15);
    opacity: 1 !important;
    visibility: visible !important;
}

/* Toggle icon */
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
button[kind="header"] svg {
    color: var(--accent) !important;
    fill: var(--accent) !important;
    stroke: var(--accent) !important;
    opacity: 1 !important;
}

/* Hover effect */
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover,
[data-testid="collapsedControl"] button:hover,
button[kind="header"]:hover {
    background-color: #1B3650 !important;
    border-color: #5DE8DA !important;
    color: #5DE8DA !important;
}

/* =========================================
   4. METRIC CARDS
========================================= */

[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.15);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    color: var(--text-main) !important;
    font-weight: 700;
}

[data-testid="stMetricDelta"] {
    color: var(--accent) !important;
}

/* =========================================
   5. BUTTONS
========================================= */

.stButton > button,
.stFormSubmitButton > button {
    background: var(--accent);
    color: #061923 !important;
    border: 1px solid var(--accent);
    border-radius: 9px;
    padding: 0.55rem 1.1rem;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button p,
.stFormSubmitButton > button p {
    color: #061923 !important;
    font-weight: 700;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(25, 195, 179, 0.2);
}

.stButton > button:focus,
.stFormSubmitButton > button:focus {
    box-shadow: 0 0 0 2px rgba(25, 195, 179, 0.35);
}

/* Disabled buttons */
.stButton > button:disabled,
.stFormSubmitButton > button:disabled {
    background: #26384E;
    color: #8395AC !important;
    border-color: #344960;
}

/* =========================================
   6. INPUTS AND SELECTBOXES
========================================= */

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    caret-color: var(--accent);
}

/* Selectbox */
[data-baseweb="select"] > div {
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
    border-color: var(--border) !important;
    border-radius: 8px !important;
}

/* Selected dropdown value */
[data-baseweb="select"] span {
    color: var(--text-main) !important;
}

/* Dropdown menu */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="list"] {
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

/* Input focus */
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
[data-baseweb="input"]:focus-within,
[data-baseweb="select"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}


/* Number input: preserve Streamlit's internal layout */
[data-testid="stNumberInput"] {
    width: 100%;
    min-width: 0;
}

[data-testid="stNumberInput"] [data-baseweb="input"] {
    background-color: #101C2E !important;
    border: 1px solid #2B405B !important;
    border-radius: 8px !important;
    overflow: hidden;
    box-shadow: none;
}

[data-testid="stNumberInput"] input {
    background-color: transparent !important;
    color: #E5EDF8 !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    min-width: 0;
}

/* Number increment/decrement controls */
[data-testid="stNumberInput"] button {
    color: #E5EDF8 !important;
    background-color: #142238 !important;
    border: none !important;
}

/* Hide the form-submit hint, without hiding other small text */
[data-testid="stForm"] [data-testid="stFormSubmitter"] small,
[data-testid="stForm"] [data-testid="stFormSubmitter"] [data-testid="stTooltipHoverTarget"] {
    display: none !important;
}

/* =========================================
   7. RADIO BUTTONS AND CHECKBOXES
========================================= */

[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {
    color: var(--text-main) !important;
}

[data-testid="stRadio"] [role="radiogroup"] {
    gap: 0.4rem;
}

[data-testid="stCheckbox"] input {
    accent-color: var(--accent);
}

/* =========================================
   8. FORMS AND CONTAINERS
========================================= */

[data-testid="stForm"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: 12px;
}

/* =========================================
   9. ALERTS AND STATUS MESSAGES
========================================= */

[data-testid="stAlert"] {
    background-color: #14263B;
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text-main);
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: var(--text-main) !important;
}

/* Success */
[data-testid="stAlert"][kind="success"] {
    background-color: #102E2D;
    border-color: #176B64;
}

/* Warning */
[data-testid="stAlert"][kind="warning"] {
    background-color: #302719;
    border-color: #8C682B;
}

/* Error */
[data-testid="stAlert"][kind="error"] {
    background-color: #351F2A;
    border-color: #8E3B51;
}

/* =========================================
   10. DATAFRAMES AND TABLES
========================================= */

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stDataFrame"] * {
    color: var(--text-main);
}

/* =========================================
   11. TABS
========================================= */

[data-testid="stTabs"] button {
    color: var(--text-muted) !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

[data-testid="stTabs"] button:hover {
    color: var(--text-main) !important;
}

/* =========================================
   12. EXPANDERS
========================================= */

[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
}

[data-testid="stExpander"] summary {
    color: var(--text-main) !important;
}

/* =========================================
   13. LINKS
========================================= */

a {
    color: var(--accent) !important;
    text-decoration: none;
}

a:hover {
    color: #5DE8DA !important;
    text-decoration: underline;
}

/* =========================================
   14. PROGRESS INDICATORS
========================================= */

[data-testid="stProgressBar"] > div > div {
    background-color: var(--accent) !important;
}

/* =========================================
   15. SPINNER
========================================= */

[data-testid="stSpinner"] {
    color: var(--accent) !important;
}

/* =========================================
   16. PLOTLY CHART CONTAINER
========================================= */

[data-testid="stPlotlyChart"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 8px;
    overflow: hidden;
}

/* =========================================
   17. SCROLLBARS
========================================= */

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

/* =========================================
   18. RESPONSIVE LAYOUT
========================================= */

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.8rem 2rem 0.8rem;
    }

    [data-testid="stMetric"] {
        padding: 12px;
    }

    [data-testid="stForm"] {
        padding: 12px;
    }
}
/* Hide Streamlit's top-right menu */
#MainMenu {
    visibility: hidden !important;
    display: none !important;
}

/* Hide the Streamlit footer */
footer {
    visibility: hidden !important;
    display: none !important;
}

/* Hide the Deploy button, if present */
.stDeployButton {
    display: none !important;
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

/* Hide the form keyboard-submit hint */
[data-testid="stForm"] [data-testid="InputInstructions"],
[data-testid="stForm"] [data-testid="stInputInstructions"],
[data-testid="stForm"] [data-testid="stNumberInput"] [data-testid="InputInstructions"],
[data-testid="stForm"] [data-testid="stNumberInput"] [data-testid="stInputInstructions"] {
    display: none !important;
}

/* Hide the visible "form" label inside number inputs */
[data-testid="stNumberInput"] [data-baseweb="input"] + div {
    display: none !important;
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
# Header
# --------------------------------------------------


st.title("📊 Insurance Risk Analyzer")
if st.button("📜 View Prediction History"):
    st.switch_page("pages/2_Prediction_History.py")
st.markdown(
    "Estimate insurance charges and understand the "
    "factors influencing each prediction."
)

st.caption(
    "Note: Estimates are in USD and intended for educational "
    "purposes only. They are not official insurance quotes."
)

st.write("")

# --------------------------------------------------
# Applicant form
# --------------------------------------------------
with st.sidebar:
    st.header("Applicant Information")
    st.caption("Enter the details to analyze.")

    with st.form("insurance_form"):
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=30
        )

        sex = st.selectbox(
            "Sex",
            ["female", "male"]
        )

        bmi = st.number_input(
            "BMI",
            min_value=1.0,
            max_value=100.0,
            value=28.5,
            step=0.1
        )

        children = st.number_input(
           "Number of children",
            min_value=0,
            max_value=20,
            value=2,
            step=1,
            help="Enter a whole number between 0 and 20."
)

        smoker = st.selectbox(
            "Smoker",
            ["no", "yes"]
        )

        region = st.selectbox(
            "Region",
            ["southwest", "southeast", "northwest", "northeast"]
        )

        submitted = st.form_submit_button(
            "Analyze Insurance Risk",
            use_container_width=True,
            type="primary"
        )

    if submitted and not (0 <= children <= 20):
        st.error(
        "Invalid number of children. "
        "Please enter a value between 0 and 20."
    )
        st.stop()

    

# --------------------------------------------------
# Prediction and explanation
# --------------------------------------------------
if submitted:
    input_data = {
        "age": int(age),
        "sex": sex,
        "bmi": float(bmi),
        "children": int(children),
        "smoker": smoker,
        "region": region
    }

    # Call prediction endpoint
    try:
        with st.spinner("Calculating predicted insurance charges..."):
            response = requests.post(
                f"{API_URL}/predict",
                json=input_data,
                timeout=30
            )
            response.raise_for_status()
            prediction = response.json()

        if not isinstance(prediction, dict):
            raise ValueError("The prediction response is not a JSON object.")

        predicted_charge = float(prediction["predicted_charge"])
        risk = prediction["risk_category"]

        if not pd.notna(predicted_charge):
            raise ValueError("The model returned an invalid prediction.")

        if risk not in ["Low Risk", "Medium Risk", "High Risk"]:
            raise ValueError("The API returned an unknown risk category.")

    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to the FastAPI backend. "
            "Start it with: uvicorn src.api:app --reload"
        )
        st.stop()

    except requests.exceptions.Timeout:
        st.error("The prediction request timed out. Please try again.")
        st.stop()

    except requests.exceptions.HTTPError as error:
        st.error(f"The prediction API returned an error: {error}")
        st.stop()

    except (requests.exceptions.RequestException, ValueError, KeyError) as error:
        st.error(f"Could not process the prediction response: {error}")
        st.stop()

    # Call explanation endpoint separately so a SHAP failure
    # does not hide an otherwise successful prediction.
    explanation = None
    explanation_error = None

    try:
        with st.spinner("Preparing feature explanations..."):
            response = requests.post(
                f"{API_URL}/explain",
                json=input_data,
                timeout=30
            )
            response.raise_for_status()
            explanation = response.json()

        if not isinstance(explanation, dict):
            raise ValueError("The explanation response is invalid.")

    except requests.exceptions.ConnectionError:
        explanation_error = "The explanation API could not be reached."
    except requests.exceptions.Timeout:
        explanation_error = "The explanation request timed out."
    except requests.exceptions.HTTPError as error:
        explanation_error = f"The explanation API returned an error: {error}"
    except (requests.exceptions.RequestException, ValueError) as error:
        explanation_error = f"Could not process the explanation: {error}"

    # --------------------------------------------------
    # Prediction summary
    # --------------------------------------------------
    st.divider()
    st.subheader("Prediction Summary")

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric(
            "Estimated Insurance Charge (USD)",
            f"${predicted_charge:,.2f}"
        )

    with metric2:
        st.metric("Risk Category", risk)

    if risk == "Low Risk":
        st.success(
            "**Low Risk:** The predicted charge falls within "
            "the model's lowest risk band."
        )
    elif risk == "Medium Risk":
        st.warning(
            "**Medium Risk:** The predicted charge falls within "
            "the model's middle risk band."
        )
    else:
        st.error(
            "**High Risk:** The predicted charge falls within "
            "the model's highest risk band."
        )

    st.caption(
        "Risk bands are project-defined from the training data's "
        "charge distribution. They are not official insurance "
        "risk classifications."
    )

    # --------------------------------------------------
    # SHAP explanation
    # --------------------------------------------------
    st.divider()
    st.subheader("What Influenced This Prediction?")

    if explanation_error:
        st.warning(
            f"The prediction succeeded, but its explanation "
            f"could not be loaded. {explanation_error}"
        )

    elif explanation is not None:
        baseline = explanation.get("baseline_charge")

        if baseline is not None:
            st.caption(
                f"Model baseline prediction: ${float(baseline):,.2f} USD. "
                "This is a reference point, not the applicant's estimate."
            )

        features = explanation.get("explanation", [])

        if features:
            chart_data = pd.DataFrame(features)

            required_columns = {"feature", "shap_value"}
            if not required_columns.issubset(chart_data.columns):
                st.warning("The explanation data is missing chart fields.")
            else:
                chart_data["shap_value"] = pd.to_numeric(
                    chart_data["shap_value"],
                    errors="coerce"
                )
                chart_data = chart_data.dropna(
                    subset=["shap_value", "feature"]
                )

                chart_data["Impact"] = chart_data["shap_value"].apply(
                    lambda value: (
                        "Increases prediction" if value > 0
                        else "Decreases prediction" if value < 0
                        else "No impact"
                    )
                )

                chart_data = chart_data.sort_values(
                    "shap_value",
                    ascending=True
                )

                if not chart_data.empty:
                    fig = px.bar(
                        chart_data,
                        x="shap_value",
                        y="feature",
                        orientation="h",
                        color="Impact",
                        color_discrete_map={
                            "Increases prediction": "#DC2626",
                            "Decreases prediction": "#16A34A",
                            "No impact": "#94A3B8"
                        },
                        labels={
                            "shap_value": "SHAP contribution (USD)",
                            "feature": "Feature",
                            "Impact": "Effect"
                        },
                        hover_data={
                            "input_value": True,
                            "description": True,
                            "shap_value": ":.2f"
                        }
                    )

                    fig.add_vline(
                        x=0,
                        line_width=1,
                        line_dash="dash",
                        line_color="gray"
                    )

                    fig.update_layout(
                        template="plotly_white",
                        height=max(350, len(chart_data) * 65),
                        margin=dict(l=10, r=20, t=25, b=10),
                        legend_title="Effect on prediction"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                    st.caption(
                        "Positive SHAP values push the model prediction "
                        "higher; negative values push it lower relative "
                        "to the baseline. These contributions describe "
                        "model behavior, not causal effects. The chart "
                        "shows the features returned by the API, not "
                        "necessarily every feature used by the model."
                    )

                    with st.expander("View detailed explanations"):
                        for feature in features:
                            st.markdown(
                                f"**{feature.get('feature', 'Feature')}**"
                            )
                            st.write(
                                f"Applicant value: "
                                f"{feature.get('input_value', 'N/A')}"
                            )
                            st.write(
                                feature.get(
                                    "description",
                                    "No description available."
                                )
                            )

                            shap_value = feature.get("shap_value")
                            if shap_value is not None:
                                st.write(
                                    f"SHAP contribution: "
                                    f"{float(shap_value):+,.2f} USD"
                                )

                            st.divider()
                else:
                    st.info("No valid SHAP values were returned.")
        else:
            st.info("No feature explanations were returned.")

else:
    # Initial dashboard state
    st.divider()
    st.subheader("Ready to Analyze")
    st.write(
        "Enter applicant details in the sidebar and select "
        "**Analyze Insurance Risk** to view the estimated charge "
        "and the factors influencing the prediction."
    )
