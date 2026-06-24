import streamlit as st
import pandas as pd

st.set_page_config(page_title="BCM AI Copilot", layout="wide")

st.title("🛡️ BCM AI Copilot")
st.caption("Analyze incidents, detect RTO breaches, and explain operational risk")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("incidents.csv")
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
    df["duration_hours"] = (df["end_time"] - df["start_time"]).dt.total_seconds() / 3600
    df["duration_hours"] = df["duration_hours"].fillna(0)
    df["rto_breach"] = df["duration_hours"] > df["rto_hours"]
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

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

# Main table
st.subheader("📊 Incident Overview")
st.dataframe(filtered_df, use_container_width=True)

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
    st.dataframe(result, use_container_width=True)

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
st.caption("Demo app — simulated incident dataset (CSV-based)")
