import streamlit as st
from streamlit_lottie import st_lottie
import json

# Set page config for Streamlit
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
thyroid_lottie = load_lottiefile("thyroid.json")
population_lottie = load_lottiefile("population.json")

# Title and description
st.title("🧬 Genetic Health Risk Dashboard")
st.write("Use this dashboard to estimate your disease risk based on genetics and history.")
st.markdown("### 🔍 Choose a disease to assess:")

# Define reusable card function
def disease_card(animation, label, page, key):
    # Create a container for each card
    with st.container():
        # Add Lottie animation
        st_lottie(animation, height=150, key=key)
        # Display button below each Lottie animation
        if st.button(label):
            st.switch_page(page)

# Create 2-column layout for displaying cards
col1, col2 = st.columns(2)

# First column (Asthma, Heart Failure)
with col1:
    st.markdown("#### 🌬️ Asthma")
    disease_card(asthma_lottie, "Predict Asthma Risk", "pages/model_asthma.py", "model_asthma")
    st.markdown("___")

    st.markdown("#### ❤️ Heart Failure")
    disease_card(heart_lottie, "Predict Heart Risk", "pages/model_heart_failure.py", "model_heart_failure")
    st.markdown("___")

    st.markdown("#### 🦋 Thyroid Risk")
    disease_card(thyroid_lottie, "Predict Thyroid Risk", "pages/model_thyroid.py", "model_thyroid")

# Second column (Lung Disease, Stroke)
with col2:
    st.markdown("#### 🫁 Lung Disease")
    disease_card(lung_lottie, "Predict Lung Risk", "pages/model_lungs.py", "model_lungs")
    st.markdown("___")

    st.markdown("#### 🧠 Stroke")
    disease_card(brain_lottie, "Predict Stroke Risk", "pages/model_stroke.py", "model_stroke")
    st.markdown("___")

    st.markdown("#### 🧬 Population LD Stream")
    disease_card(population_lottie, "Explore Population-linked Variants", "pages/population_ld_stream.py", "population_stream_ld")
    

# Footer
st.markdown("---")
st.caption("🚀 Created by GenHackers with love ❤️")
