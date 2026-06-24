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

question = st.text_input(
    "Example: 'Show high impact incidents that breached RTO'"
)

def simple_query(df, question):
    q = question.lower()

    result = df.copy()

    if "breach" in q:
        result = result[result["rto_breach"]]

    if "high" in q:
        result = result[result["impact"] == "High"]

    if "medium" in q:
        result = result[result["impact"] == "Medium"]

    if "low" in q:
        result = result[result["impact"] == "Low"]

    return result

if question:
    result = simple_query(df, question)

    st.write("### Results")
    st.dataframe(result, use_container_width=True)

    # Explanation layer (no external API needed)
    if len(result) > 0:
        st.write("### 🧠 Explanation")

        explanation = f"""
        Found {len(result)} incidents matching your query.

        Key observations:
        - {result['impact'].value_counts().to_dict()}
        - Average duration: {round(result['duration_hours'].mean(),2)} hours
        - RTO breaches: {result['rto_breach'].sum()}

        These incidents are considered critical because they exceed defined recovery objectives
        and impact important business services.
        """

        st.info(explanation)

# Footer
st.markdown("---")
st.caption("Demo app — simulated incident dataset (CSV-based)")
