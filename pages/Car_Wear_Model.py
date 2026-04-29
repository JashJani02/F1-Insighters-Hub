import streamlit as st
import pandas as pd
import plotly.express as px
from core.sidebar import render_sidebar
from core.wear_core import build_stint_dataframe,stint_degradation_metrics,compute_stint_degradation,detect_tyre_cliff

if not render_sidebar():
    st.stop

st.header("📊 Car Wear Model")

session = st.session_state.get("session")
driver = st.session_state.get("driver_ref")

if not session or not driver:
    st.warning("Please load a Session")
    st.stop()

stint_df = build_stint_dataframe(session,driver)

st.subheader("Stint Overview")

pit_laps_df = stint_df[stint_df["Pit_Lap"] == True]

if pit_laps_df.empty:
    st.info("No pit laps detected in this session.")
else:
    st.write(pit_laps_df[["Lap_Number", "Lap_Time", "Compound_Type", "Stint_ID", "Pit_Lap"]])

st.caption("**Pit laps indicate tyre changes and define the start/end of stints.**")

fig_laps = px.line(stint_df,x="Lap_Number",y="Lap_Time",color="Stint_ID",title="Lap Time Degradation per Stint")

st.plotly_chart(fig_laps,width="stretch")

stint_metrics = stint_degradation_metrics(stint_df)

fig_deg = px.line(stint_metrics,x="Stint_ID",y="Total_Degradation",color="Compound_Type",title="Total Tyre Degradation per Stint")

st.plotly_chart(fig_deg,width="stretch")

st.subheader("Compound Change")

stint_df["Prev_Compound"] = stint_df["Compound_Type"].shift(1)

stint_df["Compound_Change"] = ((stint_df["Pit_Lap"] == True) & (stint_df["Compound_Type"] != stint_df["Prev_Compound"]))

st.write(stint_df[stint_df["Compound_Change"] == True][["Lap_Number", "Prev_Compound", "Compound_Type", "Lap_Time"]])

st.subheader("Lap Time Jump at Pit Stops")

stint_df["Prev_Lap_Time"] = stint_df["Lap_Time"].shift(1)

stint_df["Lap_Time_Jump"] = (stint_df["Lap_Time"] - stint_df["Prev_Lap_Time"])

pit_effect_df = stint_df[stint_df["Pit_Lap"] == True]

st.write(pit_effect_df[["Lap_Number", "Lap_Time", "Prev_Lap_Time", "Lap_Time_Jump", "Compound_Type"]])

fig_jump = px.scatter(pit_effect_df,x="Lap_Number",y="Lap_Time_Jump",color="Compound_Type",title="Lap Time Jump After Pit Stops")

fig_jump.add_hline(y=0,line_dash="dot")

st.plotly_chart(fig_jump,width="stretch")

st.write("Stint Degradation Summery")

st.write(stint_df[["Stint_ID", "Lap_In_Stint", "Lap_Time", "Pit_Lap"]])

degradation_df = compute_stint_degradation(stint_df, min_laps=5)

st.dataframe(degradation_df, width="stretch")

clean_deg_df = degradation_df[(degradation_df["R_squared"] >= 0.6) & (degradation_df["Laps"] >= 5)]

fig_deg = px.bar(clean_deg_df,x="Stint_Number",y="Degradation_s_per_lap",color="Compound_Type",hover_data=["Laps","R_squared"],title="Tyre Degradation Rate per Stint (s / lap)")

fig_deg.add_hline(y=0,line_dash="dot",annotation_text="No Degradation")

st.plotly_chart(fig_deg,width="stretch")

selected_stint = st.selectbox("Select Stint",sorted(stint_df["Stint_ID"].unique()))

stint_plot_df = stint_df[(stint_df["Stint_ID"] == selected_stint) & (stint_df["Pit_Lap"] == False)]

fig_stint = px.scatter(stint_plot_df,x="Lap_In_Stint",y="Lap_Time",title=f"Lap Time Evolution - Stint {selected_stint}")

st.plotly_chart(fig_stint,width="stretch")

compound_summery = (clean_deg_df.groupby("Compound_Type").agg(Avg_Degradation=("Degradation_s_per_lap","mean"),Stints=("Stint_Number","count")).reset_index())

st.dataframe(compound_summery,width="stretch")

cliff_lap = detect_tyre_cliff(stint_plot_df)

fig_stint = px.scatter(stint_plot_df,x="Lap_In_Stint",y="Lap_Time",title=f"Lap Time Evolution - Stint {selected_stint}")

if cliff_lap is not None:
    
    fig_stint.add_vline(x=cliff_lap,line_dash="dash",line_color="red",annotation_text="Tyre Cliff",annotation_position="top")

st.plotly_chart(fig_stint,width="stretch",key=f"stint_plot_{selected_stint}")