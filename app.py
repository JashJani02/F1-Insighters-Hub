import streamlit as st
import fastf1 as f1
from core.fastf1_loader import load_session
from core.sidebar import render_sidebar

render_sidebar()   

st.set_page_config(page_title="F1 Insighters Hub",layout="wide")

st.title("F1 Insighters Hub")

st.markdown("""

Welcome to **F1 Insight Hub**.

This project is built to analyze:
- Telemetry
- Tracks
- Cars & component wear
- Races (near-live)

Use the sidebar to navigate.

Select the session below to begin your Analysis.
""")

YEARS = list(range(2018,2026))

SESSION_TYPES = {
    "Practice 1":"FP1",
    "Practice 2":"FP2",
    "Practice 3":"FP3",
    "Qualifyhing":"Q",
    "Sprint":"S",
    "Race":"R"
}

col1, col2, col3 = st.columns(3)

with col1:
    year = st.selectbox("Session",YEARS,index=len(YEARS)-1)

with col2:
    gp_list = f1.get_event_schedule(year)["EventName"].tolist()
    gp = st.selectbox("Grand Prix",gp_list)

with col3:
    session_label = st.selectbox("Session Type",list(SESSION_TYPES.keys()))

    session_type = SESSION_TYPES[session_label]

st.divider()

if st.button("Load Session",width="stretch"):

    with st.spinner("Loading Session Data..."):

        session = load_session(year,gp,session_type)

        st.session_state["session"] = session
        st.session_state["year"] = year
        st.session_state["gp"] = gp
        st.session_state["session_type"] = session_type

    st.success(f"Loaded {year}, {gp} - {session_label}")