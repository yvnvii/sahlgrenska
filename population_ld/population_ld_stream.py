import streamlit as st
import requests

ENSEMBL_API = "https://rest.ensembl.org"

def should_flag(user, pathogenic_parent, non_pathogenic_parent):
    return user and pathogenic_parent and not non_pathogenic_parent


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





# Streamlit UI
st.title("Phenotype-linked Variant Explorer")

phenotype_input = st.text_input("Enter a phenotype term (e.g. Huntington's disease):")

# Fetch population map
population_map = get_populations()
if not population_map:
    st.error("⚠️ No populations available. Please check Ensembl API or try again later.")
    st.stop()

selected_display = st.selectbox(
    "Select a population:",
    list(population_map.keys()),
    key="population_selector"
)

# Get the actual Ensembl population ID for API use
population_input = population_map.get(selected_display)


if phenotype_input and population_input:
    st.write(f"Searching for variants associated with: **{phenotype_input}** in population **{population_input}**")
    variant_list = get_genes(phenotype_input)


    progress_text = "Operation in progress. Please wait."
    complete_text = "Operation completed."
    percent_complete = 0
    my_bar = st.progress(percent_complete, text = progress_text)


    ld_storage = {}
    count = 0
    for var in variant_list:

        count = count +1
        percent = (count / len(variant_list)) * 0.5  # scale to 50%
        my_bar.progress(percent_complete + percent, text=progress_text)
        ld_variants = get_ld_variants("homo_sapiens", var, population_input)
        if ld_variants:
            ld_storage[var] = ld_variants

    linked_pheno_map = {}
    count = 0
    total_variant2s = sum(len(v) for v in ld_storage.values())
    for variant1, variant2_list in ld_storage.items():
        traits = set()
        for var2 in variant2_list:
            count = count +1
            percent = 0.5 + (count / total_variant2s) * 0.5  # second half of the bar

            if percent != 1:
                my_bar.progress(percent_complete + percent, text=progress_text)

            else:
                my_bar.progress((percent_complete + percent), text=progress_text)

            t = get_variant_traits(var2)
            traits.update(t)
        if traits:
            linked_pheno_map[variant1] = list(traits)

    if linked_pheno_map:
        st.subheader("Variants linked to phenotypes via LD")
        for variant1, traits in linked_pheno_map.items():
            st.markdown(f"**{variant1}** is linked to:")
            for trait in traits:
                st.write(f"- {trait}")


        st.subheader("Parental Phenotype Comparison")
        for trait in sorted(set(t for traits in linked_pheno_map.values() for t in traits)):
            st.markdown(f"#### Trait: {trait}")
            col1, col2, col3 = st.columns(3)
            with col1:
                user_has = st.checkbox("You have it", key=f"user_{trait}")
            with col2:
                pathogenic = st.checkbox("Pathogenic parent has it", key=f"pat_{trait}")
            with col3:
                non_pathogenic = st.checkbox("Non-pathogenic parent has it", key=f"nonpat_{trait}")

            if should_flag(user_has, pathogenic, non_pathogenic):
                st.success(f"⚠️ Trait '{trait}' may be inherited from the pathogenic parent only.")
    else:
        st.info("No phenotype-linked variants found via LD.")
