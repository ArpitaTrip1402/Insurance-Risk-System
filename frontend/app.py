
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

/* Main app background */
.stApp {
    background-color: #F4F7FC !important;
    color: #172B4D !important;
}

/* Streamlit top header */
[data-testid="stHeader"] {
    background-color: #F4F7FC !important;
}

/* Toolbar icons */
[data-testid="stToolbar"] {
    color: #12304A !important;
}

/* Main content layout */
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102A43 0%, #163D5C 100%) !important;
}

[data-testid="stSidebar"] * {
    color: #F0F6FC;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #DFE7F1;
    box-shadow: 0 3px 12px rgba(20, 48, 74, 0.06);
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #526780 !important;
    opacity: 1 !important;
    font-size: 0.95rem;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #12304A !important;
    font-weight: 700;
}

/* Alerts */
[data-testid="stAlert"] {
    background-color: #FFF4CC !important;
    color: #7C4A03 !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span {
    color: #7C4A03 !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #087E8B;
    color: #FFFFFF !important;
    border: 1px solid #087E8B;
    border-radius: 9px;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #066570;
    border-color: #066570;
    color: #FFFFFF !important;
}

/* Disclaimer */
.disclaimer {
    background-color: #E8F4F5;
    color: #164E63;
    padding: 14px 16px;
    border-radius: 8px;
    border-left: 4px solid #087E8B;
    font-size: 0.92rem;
}

/* Form fields */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background-color: #FFFFFF;
    border-radius: 8px;
    border-color: #CCD8E5;
}

/* Hide Streamlit input keyboard hints */
div[data-testid="InputInstructions"],
div[data-testid="InputInstructions"] *,
[data-testid="stForm"] small {
    display: none !important;
}

/* Sidebar expand/collapse control — target the control and its button */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button,
button[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    background: #0D9488 !important;
    border: 2px solid #FFFFFF !important;
    border-radius: 8px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.25) !important;
}

/* Keep the toggle icon white */
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
button[data-testid="collapsedControl"] svg,
button[data-testid="stSidebarCollapsedControl"] svg {
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
    fill: none !important;
    opacity: 1 !important;
}

/* Hover state */
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"] button:hover,
[data-testid="stSidebarCollapsedControl"] button:hover {
    background: #0F766E !important;
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
