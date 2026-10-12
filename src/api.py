from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import joblib
import pandas as pd
import shap

import os
import psycopg
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "insurance_model.pkl"

model = joblib.load(MODEL_PATH)

load_dotenv(BASE_DIR / ".env")


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "insurance_risk_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )

# --------------------------------------------------
# 2. Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Insurance Risk & Premium API",
    description="API for predicting insurance charges and risk category",
    version="1.0.0"
)


# --------------------------------------------------
# 3. Input schema
# --------------------------------------------------

class InsuranceInput(BaseModel):
    age: int = Field(ge=18, le=100)
    sex: Literal["male", "female"]
    bmi: float = Field(gt=0, le=100)
    children: int = Field(ge=0, le=20)
    smoker: Literal["yes", "no"]
    region: Literal[
        "southwest",
        "southeast",
        "northwest",
        "northeast"
    ]

class InsuranceResponse(BaseModel):
    predicted_charge: float
    risk_category: Literal[
        "Low Risk",
        "Medium Risk",
        "High Risk"
    ]


# --------------------------------------------------
# 4. Risk classification
# --------------------------------------------------

def classify_risk(predicted_charge):

    if predicted_charge <= 9386.1613:
        return "Low Risk"

    elif predicted_charge <= 16657.71745:
        return "Medium Risk"

    else:
        return "High Risk"


# --------------------------------------------------
# 5. Home endpoint
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Insurance Risk & Premium API is running"
    }


# --------------------------------------------------
# 6. Prediction endpoint
# --------------------------------------------------

@app.post("/predict", response_model=InsuranceResponse)
def predict(data: InsuranceInput):
    input_data = pd.DataFrame([{
        "age": data.age,
        "sex": data.sex,
        "bmi": data.bmi,
        "children": data.children,
        "smoker": data.smoker,
        "region": data.region
    }])

    try:
        predicted_charge = float(model.predict(input_data)[0])
        risk = classify_risk(predicted_charge)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Please try again later."
        )

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO prediction_history (
                        age, sex, bmi, children, smoker, region,
                        predicted_charge, risk_category
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        data.age,
                        data.sex,
                        data.bmi,
                        data.children,
                        data.smoker,
                        data.region,
                        round(predicted_charge, 2),
                        risk
                    )
                )

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Prediction was generated, but saving history failed. "
                   "Please check the database connection."
        )

    return {
        "predicted_charge": round(predicted_charge, 2),
        "risk_category": risk
    }


@app.post("/explain")
def explain(data: InsuranceInput):
    try:
        # 1. Prepare the input
        input_data = pd.DataFrame([{
            "age": data.age,
            "sex": data.sex,
            "bmi": data.bmi,
            "children": data.children,
            "smoker": data.smoker,
            "region": data.region
        }])

        # 2. Access the trained preprocessing and model steps
        preprocessor = model.named_steps["preprocessor"]
        xgb_model = model.named_steps["model"]

        # 3. Apply the same preprocessing used during training
        transformed_data = preprocessor.transform(input_data)

        if hasattr(transformed_data, "toarray"):
            transformed_data = transformed_data.toarray()

        feature_names = preprocessor.get_feature_names_out()

        # 4. Generate SHAP explanations
        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(transformed_data)

        contributions = shap_values[0]

        # Obtain the model's baseline prediction
        baseline_charge = float(
            explainer.expected_value
        )

        # 5. Map transformed features to readable names and values
        feature_details = {
            "num__age": ("Age", data.age),
            "num__bmi": ("BMI", data.bmi),
            "num__children": ("Number of children", data.children),
            "cat__sex_male": ("Sex: Male", data.sex == "male"),
            "cat__sex_female": ("Sex: Female", data.sex == "female"),
            "cat__smoker_yes": ("Smoker status", "Yes" if data.smoker == "yes" else "No"),
            "cat__smoker_no": ("Smoker status", "No" if data.smoker == "no" else "Yes"),
            "cat__region_northeast": ("Region: Northeast", data.region == "northeast"),
            "cat__region_northwest": ("Region: Northwest", data.region == "northwest"),
            "cat__region_southeast": ("Region: Southeast", data.region == "southeast"),
            "cat__region_southwest": ("Region: Southwest", data.region == "southwest")
        }

        # 6. Rank features by absolute SHAP contribution
        ranked_indices = sorted(
            range(len(contributions)),
            key=lambda i: abs(float(contributions[i])),
            reverse=True
        )

        top_features = []

        for i in ranked_indices[:5]:
            raw_name = str(feature_names[i])
            shap_value = float(contributions[i])

            display_name, input_value = feature_details.get(
                raw_name,
                (raw_name, None)
            )

            if shap_value > 0:
                effect = "increases prediction"
                description = (
                    f"{display_name} pushes the predicted charge higher "
                    "than the model baseline."
                )
            elif shap_value < 0:
                effect = "decreases prediction"
                description = (
                    f"{display_name} pushes the predicted charge lower "
                    "than the model baseline."
                )
            else:
                effect = "no effect"
                description = (
                    f"{display_name} has no contribution to this prediction."
                )

            top_features.append({
                "feature": display_name,
                "input_value": input_value,
                "shap_value": round(shap_value, 2),
                "effect": effect,
                "description": description
            })

        # 7. Get the final prediction and risk category
        predicted_charge = float(model.predict(input_data)[0])
        risk = classify_risk(predicted_charge)

        return {
            "predicted_charge": round(predicted_charge, 2),
            "risk_category": risk,
            "baseline_charge": round(baseline_charge, 2),
            "explanation": top_features,
            "explanation_note": (
                "Positive SHAP values increase the prediction relative "
                "to the baseline; negative values decrease it. "
                "These contributions describe model behavior, not causation."
            )
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate prediction explanation."
        )



@app.get("/history")
def get_prediction_history():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, age, sex, bmi, children, smoker, region,
                        predicted_charge, risk_category, created_at
                    FROM prediction_history
                    ORDER BY created_at DESC, id DESC
                    LIMIT 100
                    """
                )

                rows = cur.fetchall()

        return [
            {
                "id": row[0],
                "age": row[1],
                "sex": row[2],
                "bmi": float(row[3]),
                "children": row[4],
                "smoker": row[5],
                "region": row[6],
                "predicted_charge": float(row[7]),
                "risk_category": row[8],
                "created_at": row[9].isoformat() if row[9] else None
            }
            for row in rows
        ]

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve prediction history."
        )

