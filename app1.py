from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "incidents.csv"
IMAGE_PATH = BASE_DIR / "images/architecture.png"

st.set_page_config(page_title="Operational Resilience AI Prototype", layout="wide")

st.title("🛡️ Operational Resilience AI Prototype")

image = Image.open(IMAGE_PATH)

st.image(
    image,
    width="stretch"
)

st.markdown("""
*A lightweight proof of concept demonstrating how Generative AI can support Business Continuity Management (BCM) and Operational Resilience.*

---
""")

st.info("""
This prototype uses **simulated data** to demonstrate how AI can combine:

• Incident history

• Business Impact Analysis (BIA)

• BCM testing

• Policies

to generate operational resilience insights and assessments.
""")

# Load data
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(f"Data file not found: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
    df["duration_hours"] = (df["end_time"] - df["start_time"]).dt.total_seconds() / 3600
    df["duration_hours"] = df["duration_hours"].fillna(0)
    df["rto_breach"] = df["duration_hours"] > df["rto_hours"]
    return df

df = load_data()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🛡️ Operational Resilience AI")

st.sidebar.info("""
**Prototype Status**

✅ Version 1 - Natural-language Incident Analysis

✅ Version 2 - AI-generated Resilience Assessments

🚧 Version 3 - Retrieval-Augmented Generation (RAG) (planned)

🚧 Version 4 - AI Agent (planned)
""")

with st.sidebar.expander("🏗️ Architecture"):

    st.write("""
    Frontend
    • Streamlit

    Backend
    • Python

    AI
    • Ollama
    • Qwen 3.6

    Data
    • CSV files
    """)

st.sidebar.markdown("---")

st.sidebar.subheader("📂 Data Sources")

st.sidebar.markdown("""
✔ Incidents

✔ Business Impact Analysis (BIA)

✔ BCM Tests

✔ Policies
""")

# Sidebar filters

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Explore incident data")

impact_filter = st.sidebar.multiselect(
    "Impact level",
    options=df["impact"].unique(),
    default=df["impact"].unique()
)

service_filter = st.sidebar.multiselect(
    "Service",
    options=df["service"].unique(),
    default=df["service"].unique()
)

show_only_breaches = st.sidebar.checkbox("Show only RTO breaches", value=True)

# Apply filters
filtered_df = df[
    (df["impact"].isin(impact_filter)) &
    (df["service"].isin(service_filter))
]

if show_only_breaches:
    filtered_df = filtered_df[filtered_df["rto_breach"]]

st.sidebar.markdown("---")

st.sidebar.subheader("ℹ️ About")

st.sidebar.caption("""
This prototype demonstrates how
Generative AI can support
Operational Resilience by combining
multiple BCM datasets.

All data is simulated.
""")

# Main table
st.subheader("📊 Incident Overview")
st.dataframe(filtered_df, width="stretch")

# KPI section
col1, col2, col3 = st.columns(3)

col1.metric("Total incidents", len(df))
col2.metric("RTO breaches", df["rto_breach"].sum())
col3.metric("High impact breaches",
            len(df[(df["rto_breach"]) & (df["impact"] == "High")]))

# Natural language query (simple version)
st.subheader("💬 Ask a question")

st.markdown("""
### Example questions

- Show critical incidents that exceeded recovery objectives
- Show critical incidents that exceeded recovery objectives in Payments
- Show medium impact incidents
- Show Banking incidents
- Show RTO breaches
""")

question = st.text_input(
    "Example: 'Show high impact incidents that breached RTO'"
)

def simple_query(df, question):

    q = question.lower()

    result = df.copy()

    # ---------------------------
    # RTO breach synonyms
    # ---------------------------
    breach_terms = [
        "breach",
        "breached",
        "exceeded",
        "exceed",
        "rto",
        "recovery objective",
        "recovery objectives",
        "recovery target",
        "recovery targets"
    ]

    if any(term in q for term in breach_terms):
        result = result[result["rto_breach"]]

    # ---------------------------
    # High impact synonyms
    # ---------------------------
    high_terms = [
        "critical",
        "high",
        "severe",
        "major"
    ]

    if any(term in q for term in high_terms):
        result = result[result["impact"] == "High"]

    # ---------------------------
    # Medium impact synonyms
    # ---------------------------
    medium_terms = [
        "medium",
        "moderate"
    ]

    if any(term in q for term in medium_terms):
        result = result[result["impact"] == "Medium"]

    # ---------------------------
    # Low impact synonyms
    # ---------------------------
    low_terms = [
        "low",
        "minor"
    ]

    if any(term in q for term in low_terms):
        result = result[result["impact"] == "Low"]

    # ---------------------------
    # Service recognition
    # ---------------------------
    for service in df["service"].unique():

        service_name = str(service).lower()

        if service_name in q:
            result = result[result["service"] == service]

    # ---------------------------
    # Sort by duration descending
    # ---------------------------
    result = result.sort_values(
        by="duration_hours",
        ascending=False
    )

    return result

if question:

    result = simple_query(df, question)

    st.write("### Results")
    st.dataframe(result, width="stretch")

    # Explanation section
    st.write("### 🧠 Explanation")

    if len(result) > 0:

        longest = result.iloc[0]

        explanation = f"""
Found {len(result)} matching incidents.

The most severe incident was {longest['incident_id']} ({longest['title']}),
which lasted {round(longest['duration_hours'],2)} hours.

Average duration:
{round(result['duration_hours'].mean(),2)} hours.

Number of RTO breaches:
{result['rto_breach'].sum()}.

Services impacted:
{', '.join(result['service'].unique())}.
"""

        st.info(explanation)

# Footer
st.markdown("---")

st.caption("""
**Operational Resilience AI Prototype**

Prototype using simulated data for demonstration purposes only.

Created by **Aleksandar Grcic**  
🔗 [LinkedIn](https://www.linkedin.com/in/aleksandar-grcic)
""")