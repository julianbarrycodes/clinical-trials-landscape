"""
Step 5: Clinical Trials Landscape dashboard (Streamlit)

Run locally (on your Mac, not in Colab):
    pip install streamlit pandas plotly
    streamlit run app.py

Expects trials.db (from store_in_sqlite.py) in the same folder.
"""

import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Clinical Trials Landscape", layout="wide")


@st.cache_data
def load_data():
    conn = sqlite3.connect("trials.db")
    trials = pd.read_sql("""
        SELECT t.*, c.condition_query
        FROM trials t
        JOIN trial_conditions c ON t.nct_id = c.nct_id
    """, conn)
    quality = pd.read_sql("SELECT * FROM data_quality", conn)
    conn.close()
    return trials, quality


df, quality = load_data()

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")

conditions = sorted(df["condition_query"].unique())
sel_conditions = st.sidebar.multiselect("Condition", conditions, default=conditions)

phases = sorted(df["phase_clean"].dropna().unique())
sel_phases = st.sidebar.multiselect("Phase", phases, default=phases)

sponsor_types = sorted(df["sponsor_type"].dropna().unique())
sel_sponsors = st.sidebar.multiselect("Sponsor type", sponsor_types, default=sponsor_types)

years = df["start_year"].dropna()
min_year, max_year = int(years.min()), int(years.max())
sel_years = st.sidebar.slider("Start year", min_year, max_year, (max(min_year, 2010), max_year))

f = df[
    df["condition_query"].isin(sel_conditions)
    & df["phase_clean"].isin(sel_phases)
    & df["sponsor_type"].isin(sel_sponsors)
    & df["start_year"].between(*sel_years)
]

# ---------------- Header & KPIs ----------------
st.title("Clinical Trials Landscape")
st.caption("Source: ClinicalTrials.gov API v2 · Built with Python, SQLite and Streamlit")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Trials", f"{f['nct_id'].nunique():,}")
k2.metric("Recruiting", f"{(f.drop_duplicates('nct_id')['status'] == 'RECRUITING').sum():,}")
k3.metric("Industry-sponsored", f"{(f.drop_duplicates('nct_id')['sponsor_type'] == 'INDUSTRY').mean():.0%}")
k4.metric("Median enrollment", f"{f.drop_duplicates('nct_id')['enrollment'].median():.0f}")

tab_overview, tab_sponsors, tab_quality, tab_data = st.tabs(
    ["Overview", "Sponsors", "Data quality", "Data"]
)

# ---------------- Overview ----------------
with tab_overview:
    by_year = f.groupby(["start_year", "condition_query"])["nct_id"].nunique().reset_index(name="trials")
    st.plotly_chart(
        px.line(by_year, x="start_year", y="trials", color="condition_query",
                title="New trials per year", markers=True),
        use_container_width=True,
    )

    c1, c2 = st.columns(2)
    by_phase = f.groupby(["phase_clean", "condition_query"])["nct_id"].nunique().reset_index(name="trials")
    c1.plotly_chart(
        px.bar(by_phase, x="phase_clean", y="trials", color="condition_query",
               barmode="group", title="Trials by phase"),
        use_container_width=True,
    )
    by_status = f.drop_duplicates("nct_id")["status"].value_counts().reset_index()
    by_status.columns = ["status", "trials"]
    c2.plotly_chart(px.pie(by_status, names="status", values="trials", title="Trial status"),
                    use_container_width=True)

# ---------------- Sponsors ----------------
with tab_sponsors:
    top = (f.drop_duplicates("nct_id")
             .query("sponsor_type == 'INDUSTRY'")["sponsor"]
             .value_counts().head(15).reset_index())
    top.columns = ["sponsor", "trials"]
    st.plotly_chart(
        px.bar(top, x="trials", y="sponsor", orientation="h", title="Top 15 industry sponsors")
          .update_yaxes(autorange="reversed"),
        use_container_width=True,
    )

# ---------------- Data quality ----------------
with tab_quality:
    st.subheader("Data quality checks")
    st.write("Checks run during cleaning: completeness, uniqueness, validity and consistency.")
    st.dataframe(quality, use_container_width=True)

# ---------------- Raw data ----------------
with tab_data:
    st.dataframe(
        f[["nct_id", "title", "condition_query", "phase_clean", "status",
           "sponsor", "sponsor_type", "start_year", "enrollment"]],
        use_container_width=True,
    )
    st.download_button("Download filtered data (CSV)", f.to_csv(index=False), "trials_filtered.csv")
