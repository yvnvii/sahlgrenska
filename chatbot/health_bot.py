import streamlit as st

# --- Risk Calculation Functions ---

def calculate_bmi(weight_kg, height_cm):
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def diabetes_risk_score(age, sex, family_history, high_glucose_history,
                        on_bp_meds, smoker, physically_inactive, bmi):
    score = 0

    if 25 <= age <= 34:
        score += 0
    elif 35 <= age <= 44:
        score += 2
    elif 45 <= age <= 54:
        score += 4
    elif 55 <= age <= 64:
        score += 6
    elif age >= 65:
        score += 8

    if sex.lower() == "male":
        score += 3
    if family_history:
        score += 3
    if high_glucose_history:
        score += 6
    if on_bp_meds:
        score += 2
    if smoker:
        score += 2
    if physically_inactive:
        score += 2

    if bmi < 25:
        score += 0
    elif 25 <= bmi < 30:
        score += 3
    elif 30 <= bmi < 35:
        score += 6
    elif bmi >= 35:
        score += 8

    return score

def interpret_diabetes_risk(score):
    if score < 5:
        return "Low"
    elif score < 10:
        return "Moderate"
    else:
        return "High"

def generate_diabetes_recommendations(risk_level):
    if risk_level == "Low":
        return ["Maintain your current healthy habits! 👍"]

    recs = [
        "Begin or increase physical activity (at least 150 mins/week).",
        "Reduce processed sugar and refined carbs.",
        "Consider regular blood sugar checks.",
        "Explore a continuous glucose monitor (CGM)."
    ]
    if risk_level == "High":
        recs.append("Speak to a healthcare provider for a full diabetes screening.")
        recs.append("Consider genetic testing for diabetes risk.")
    return recs

# --- Streamlit App ---

st.set_page_config(page_title="Diabetes Risk Checker", page_icon="🩺")

st.title("🩺 AI Diabetes Risk Checker")
st.markdown("This tool estimates your risk of developing **Type 2 Diabetes** based on known clinical factors.")

with st.form("health_form"):
    age = st.slider("Age", 18, 90, 30)
    sex = st.radio("Gender", ["Male", "Female", "Other"])
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=100.0, max_value=220.0, value=170.0)
    smoker = st.checkbox("I currently smoke")
    drink = st.checkbox("I drink alcohol")
    activity = st.selectbox("Activity level", ["Sedentary", "Moderate", "Active"])
    high_blood_sugar = st.checkbox("History of high blood sugar")
    family_diabetes = st.checkbox("Family history of diabetes")
    on_bp_meds = st.checkbox("I use blood pressure medication")

    submitted = st.form_submit_button("Calculate Risk")

if submitted:
    bmi = calculate_bmi(weight, height)
    inactive = activity.lower() == "sedentary"
    score = diabetes_risk_score(
        age, sex, family_diabetes, high_blood_sugar,
        on_bp_meds, smoker, inactive, bmi
    )
    risk_level = interpret_diabetes_risk(score)
    recs = generate_diabetes_recommendations(risk_level)

    st.subheader("📊 Results")
    st.write(f"**BMI:** {bmi}")
    st.write(f"**Diabetes Risk Score:** {score}/20+")
    st.write(f"**Risk Level:** :red[{risk_level}]")

    st.subheader("✅ Recommendations")
    for rec in recs:
        st.markdown(f"- {rec}")

    st.info("⚠️ This tool is for educational use only. Please consult a doctor for medical advice.")
