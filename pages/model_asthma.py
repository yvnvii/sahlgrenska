import streamlit as st
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Load model and scaler
model = load_model("data/asthma_risk_model.keras")
scaler = joblib.load("data/asthma_scaler.pkl")

# Define features used in the model
feature_names = [
    'Gender',
    'Age_Years',
    'Treated_For_Anemia_Past_3mo',
    'Doctor_Said_Overweight',
    'Ever_Had_Blood_Transfusion',
    'Doctor_Said_Arthritis',
    'Doctor_Said_Gout',
    'Told_Had_Heart_Failure',
    'Told_Had_Coronary_Heart_Disease',
    'Told_Had_Angina',
    'Told_Had_Heart_Attack',
    'Told_Had_Stroke',
    'Told_Had_Thyroid_Problem',
    'Told_Had_Emphysema',
    'Told_Had_Chronic_Bronchitis',
    'Told_Had_COPD',
    'Told_Had_Liver_Condition',
    'Told_Had_Liver_Condition_Youth',
    'Liver_Condition_Fatty_Liver',
    'Liver_Condition_Fibrosis',
    'Liver_Condition_Cirrhosis',
    'Liver_Condition_Hepatitis',
    'Liver_Condition_Autoimmune_Hepatitis',
    'Abdominal_Pain_Past_Year',
    'Location_Of_Most_Uncomfortable_Pain',
    'Doctor_Said_Gallstones',
    'Had_Gallbladder_Surgery',
    'Told_Had_Jaundice',
    'Told_Had_Cancer_Or_Malignancy',
    'Type_First_Cancer',
    'Relative_Had_Asthma',
    'Relative_Had_Diabetes',
    'Relative_Had_Heart_Attack',
    'Doctor_Told_To_Lose_Weight',
    'Doctor_Told_To_Exercise',
    'Doctor_Told_To_Reduce_Salt',
    'Doctor_Told_To_Reduce_Fat_Calories',
    'Currently_Losing_Weight',
    'Currently_Exercising',
    'Currently_Reducing_Salt',
    'Currently_Reducing_Fat_Calories',
    'Currently_Taking_Osteoporosis_Meds'
]

# Define label mappings
option_labels = {
    1: "Yes",
    2: "No",
    7: "Refused",
    9: "Don't know"
}

option_labels_gender = {
    1: "Male",
    2: "Female"
}

st.title("🫁 Asthma Risk Predictor")
st.write("Answer the questions below to estimate your risk of having asthma.")

user_input = {}

for feature in feature_names:
    if feature == "Gender":
        response = st.selectbox(
            "Gender",
            options=list(option_labels_gender.keys()),
            format_func=lambda x: option_labels_gender[x]
        )
    elif feature == "Age_Years":
        response = st.slider("Age (in years)", min_value=0, max_value=150, value=30)
    else:
        response = st.selectbox(
            label=feature.replace('_', ' '),
            options=list(option_labels.keys()),
            format_func=lambda x: option_labels[x]
        )
    
    user_input[feature] = response

# Prediction
if st.button("Calculate Risk"):
    input_df = pd.DataFrame([user_input])
    
    try:
        input_scaled = scaler.transform(input_df)
        risk_score = model.predict(input_scaled)[0][0]

        st.subheader("📊 Estimated Risk")
        st.write(f"Your predicted risk of asthma is **{risk_score:.2%}**")

        if risk_score > 0.7:
            st.error("⚠️ High risk – please consider consulting a healthcare professional.")
        elif risk_score > 0.4:
            st.warning("⚠️ Moderate risk – worth monitoring.")
        else:
            st.success("✅ Low risk – keep taking care of your health!")

    except Exception as e:
        st.error(f"Something went wrong during prediction: {e}")
