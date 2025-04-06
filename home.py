import streamlit as st
from streamlit_lottie import st_lottie
import json

st.set_page_config(page_title="Genetic Health Risk Dashboard", page_icon="🧬", layout="wide")

# Load local Lottie JSON files
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# Load animations
asthma_lottie = load_lottiefile("health.json")
heart_lottie = load_lottiefile("heart.json")
lung_lottie = load_lottiefile("lung.json")
brain_lottie = load_lottiefile("brain.json")

st.title("🧬 Genetic Health Risk Dashboard")
st.write("Use this dashboard to estimate your disease risk based on genetics and history.")
st.markdown("### 🔍 Choose a disease to assess:")

# Define reusable card function
def disease_card(animation, label, page, key):
    with st.container():
        st_lottie(animation, height=150, key=key)
        if st.button(label):
            st.switch_page(page)

# Create 2-column layout
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown("#### 🌬️ Asthma")
        disease_card(asthma_lottie, "Predict Asthma Risk", "pages/model_asthma.py", "asthma")
        st.markdown("___")

    with st.container():
        st.markdown("#### ❤️ Heart Failure")
        disease_card(heart_lottie, "Predict Heart Risk", "pages/model_heart_failure.py", "heart")

with col2:
    with st.container():
        st.markdown("#### 🫁 Lung Disease")
        disease_card(lung_lottie, "Predict Lung Risk", "pages/model_lungs.py", "lung")
        st.markdown("___")

    with st.container():
        st.markdown("#### 🧠 Stroke")
        disease_card(brain_lottie, "Predict Stroke Risk", "pages/model_stroke.py", "stroke")

st.markdown("---")
st.caption("🚀 Created by GenHackers with love ❤️")
