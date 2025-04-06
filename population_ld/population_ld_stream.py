import streamlit as st
import requests
from collections import defaultdict

ENSEMBL_API = "https://rest.ensembl.org"

# ------------------------------
# API Functions
# ------------------------------

def get_genes(phenotype_term, species="homo_sapiens"):
    url = f"{ENSEMBL_API}/phenotype/term/{species}/{phenotype_term}?content-type=application/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        genes = [entry.get("Gene") for entry in data if "Gene" in entry]
        variations = [entry.get("Variation") for entry in data if "Variation" in entry]
        return genes + variations
    else:
        st.error(f"Error fetching genes for '{phenotype_term}': {response.status_code}")
        return []

def get_ld_variants(species, variant_id, population):
    url = f"{ENSEMBL_API}/ld/{species}/{variant_id}/{population}?d_prime=1.0;r2=0.85"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [entry.get("variation2") for entry in data if "variation2" in entry]
    except:
        return []

def get_variant_traits(variant_id):
    url = f"{ENSEMBL_API}/variation/homo_sapiens/{variant_id}?phenotypes=1"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        traits = [item.get("trait") for item in data.get("phenotypes", []) if "trait" in item]
        return list(set(traits))
    except:
        return []

@st.cache_data(show_spinner=False)
def get_populations(species="homo_sapiens"):
    url = f"{ENSEMBL_API}/info/variation/populations/{species}?content-type=application/json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        populations = response.json()

        pop_map = {}
        for pop in populations:
            name = pop.get("name")
            desc = (pop.get("description") or "").strip()
            label = f"{desc} [{name}]" if desc else name
            if name:
                pop_map[label] = name

        return pop_map
    except Exception as e:
        st.warning(f"Failed to fetch population list: {e}")
        return {}

# ------------------------------
# Session State Setup
# ------------------------------

if "variant_list" not in st.session_state:
    st.session_state.variant_list = None
if "ld_storage" not in st.session_state:
    st.session_state.ld_storage = None
if "linked_pheno_map" not in st.session_state:
    st.session_state.linked_pheno_map = None

# ------------------------------
# UI
# ------------------------------

st.title("🔬 Phenotype-linked Variant Explorer")

if st.button("🔄 Reset Analysis"):
    st.session_state.variant_list = None
    st.session_state.ld_storage = None
    st.session_state.linked_pheno_map = None

phenotype_input = st.text_input("Enter a phenotype term (e.g. Huntington's disease):")

population_map = get_populations()
if not population_map:
    st.error("⚠️ No populations available. Please check Ensembl API or try again later.")
    st.stop()

selected_display = st.selectbox(
    "Select a population:",
    list(population_map.keys()),
    key="population_selector"
)
population_input = population_map.get(selected_display)

# ------------------------------
# Variant + Trait Retrieval (cached by session_state)
# ------------------------------

if phenotype_input and population_input:
    st.write(f"Searching for variants associated with: **{phenotype_input}** in population **{population_input}**")

    if st.session_state.variant_list is None or st.session_state.ld_storage is None or st.session_state.linked_pheno_map is None:
        variant_list = get_genes(phenotype_input)
        st.session_state.variant_list = variant_list

        progress_text = "🔍 Searching for linked variants and phenotypes..."
        my_bar = st.progress(0, text=progress_text)

        ld_storage = {}
        for i, var in enumerate(variant_list):
            percent = (i / len(variant_list)) * 0.5
            my_bar.progress(percent, text=progress_text)
            ld_variants = get_ld_variants("homo_sapiens", var, population_input)
            if ld_variants:
                ld_storage[var] = ld_variants

        st.session_state.ld_storage = ld_storage

        linked_pheno_map = {}
        total_variant2s = sum(len(v) for v in ld_storage.values())
        count = 0
        for variant1, variant2_list in ld_storage.items():
            traits = set()
            for var2 in variant2_list:
                count += 1
                percent = 0.5 + (count / total_variant2s) * 0.5
                my_bar.progress(percent, text=progress_text)
                traits.update(get_variant_traits(var2))
            if traits:
                linked_pheno_map[variant1] = list(traits)

        st.session_state.linked_pheno_map = linked_pheno_map
    else:
        variant_list = st.session_state.variant_list
        ld_storage = st.session_state.ld_storage
        linked_pheno_map = st.session_state.linked_pheno_map

    # ------------------------------
    # Show Results
    # ------------------------------

    if linked_pheno_map:
        st.subheader("🧬 Variants linked to phenotypes via LD")
        for variant1, traits in linked_pheno_map.items():
            st.markdown(f"**{variant1}** is linked to:")
            for trait in traits:
                st.write(f"- {trait}")

        # ------------------------------
        # Trait Comparison UI
        # ------------------------------

        st.subheader("🧬 Trait Similarity to Parents")

        trait_agreement_count = 0
        trait_comparison_results = defaultdict(dict)

        for trait in sorted(set(t for traits in linked_pheno_map.values() for t in traits)):
            st.markdown(f"#### Trait: **{trait}**")
            col1, col2 = st.columns(2)
            with col1:
                pat_response = st.radio(
                    f"Similar to pathogenic parent?",
                    ["I don't know", "Yes", "No"],
                    key=f"patresp_{trait}"
                )
            with col2:
                nonpat_response = st.radio(
                    f"Similar to non-pathogenic parent?",
                    ["I don't know", "Yes", "No"],
                    key=f"nonpatresp_{trait}"
                )

            trait_comparison_results[trait]["pat"] = pat_response
            trait_comparison_results[trait]["nonpat"] = nonpat_response

            if pat_response == "Yes" and nonpat_response != "Yes":
                trait_agreement_count += 1
                st.markdown("🧬 **Flag:** Trait may be linked to pathogenic parent.")

        st.markdown("---")
        st.markdown(f"### 🔢 Traits likely inherited from the pathogenic parent: **{trait_agreement_count}**")

        if trait_agreement_count >= 3:
            st.warning("⚠️ Several traits suggest inheritance from the pathogenic parent. Consider discussing with a genetics expert.")
        elif trait_agreement_count == 0:
            st.success("✅ No strong inheritance pattern detected.")
        else:
            st.info("🧬 Some shared traits suggest possible inheritance.")
    else:
        st.info("No phenotype-linked variants found via LD.")
