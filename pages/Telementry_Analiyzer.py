import pandas as pd
import streamlit as st
import plotly.express as px
from core.telementry_core import get_fastest_lap_telementry, get_telemetry_channels, get_delta_dataframe, compute_delta,add_minisectors, minisector_dominance, merge_dominance,get_gear_telemetry
from core.sidebar import render_sidebar
from core.corner_analysis import extract_corners,corner_entry_exit_metrics,extract_gear_exit_metrics

if not render_sidebar():
    st.stop()

st.header("📊 Telementry Analyzer")


if "session" not in st.session_state:
    st.warning("Please load a Session")
    st.stop()


session = st.session_state["session"] #! Session state loader

driver_1 = st.session_state.get("driver_ref")
driver_2 = st.session_state.get("driver_comp")

if not driver_1 or not driver_2:
    st.warning("Please select the Drivers from the Sidebar")

    st.stop()

full_tel_1 = get_fastest_lap_telementry(session,driver_1)
full_tel_2 = get_fastest_lap_telementry(session,driver_2)

combined = pd.concat([full_tel_1,full_tel_2],ignore_index=True)

fig = px.line(combined,x="Distance",y="Speed",color="Driver",title="Fastest Lap Speed Comparision")

st.plotly_chart(fig,width="stretch")

st.subheader("Throttle & Brake Comparsion")

channels = ["Throttle","Brake"]

channel_tel_1 = get_telemetry_channels(session,driver_1,channels)
channel_tel_2 = get_telemetry_channels(session,driver_2,channels)

combined_tel = pd.concat([channel_tel_1,channel_tel_2],ignore_index=True)

throttle_df =combined_tel[combined_tel["Channel"]=="Throttle"]

fig_throttle = px.line(throttle_df,x="Distance",y="Value",color="Driver",title="Throttle vs Distance")

st.plotly_chart(fig_throttle,width="stretch")

brake_df =combined_tel[combined_tel["Channel"]=="Brake"]

fig_brake = px.line(brake_df,x="Distance",y="Value",color="Driver",title="Brake vs Distance",line_dash="Driver")

st.plotly_chart(fig_brake,width="stretch")

st.subheader("Gear Change Analysis")

gear_1 = get_gear_telemetry(session,driver_1)
gear_2 = get_gear_telemetry(session,driver_2)

gear_combined = pd.concat([gear_1,gear_2],ignore_index=True)

fig_gear = px.line(gear_combined,x="Distance",y="nGear",color="Driver",title="Gear vs Distance")

fig_gear.update_layout(yaxis=dict(title="Gear",tickmode="linear",dtick=1))

st.plotly_chart(fig_gear,width="stretch")

st.subheader("⏱️ Delta Time Analysis")

delta_df = get_delta_dataframe(session,driver_1,driver_2)

delta_df = compute_delta(delta_df)

fig_delta = px.line(delta_df,x="Distance",y="Delta_time",title=f"Delta Time: {driver_2} vs {driver_1}")

fig_delta.add_hline(y=0,line_dash="dot")

st.plotly_chart(fig_delta,width="stretch")

st.subheader("Minisector Dominance")

delta_df = add_minisectors(delta_df,num_sectors=25)

dominance_df = minisector_dominance(delta_df,driver_1,driver_2)

delta_df = merge_dominance(delta_df,dominance_df)

fig_dom = px.scatter(delta_df,x="Distance",y="Speed_ref",color="Winner",title=f"Mini-sector Dominance between {driver_1} vs {driver_2}",opacity=0.8)

st.plotly_chart(fig_dom,width="stretch")

st.subheader("Track Map Dominance")

fig_map = px.scatter(delta_df,x="X",y="Y",color="Winner",title=f"Track Map Mini-sector Dominance between {driver_1} vs {driver_2}",opacity=0.9)

fig_map.update_traces(marker=dict(size=4))

fig_map.update_layout(yaxis=dict(scaleanchor="x"))

st.plotly_chart(fig_map,width="stretch")

st.subheader("Corner Entry/Exit Analysis")

corners_1 = extract_corners(full_tel_1)

corners_2 = extract_corners(full_tel_2)

metrics_1 = corner_entry_exit_metrics(full_tel_1,corners_1)

metrics_2 = corner_entry_exit_metrics(full_tel_2,corners_2)

metrics_1["Driver"] = driver_1

metrics_2["Driver"] = driver_2

corner_df = pd.concat([metrics_1,metrics_2],ignore_index=True)

#! Checking df data
st.write("Corner DF columns:", corner_df.columns.tolist())
st.write(corner_df.head())

corner_long = corner_df.melt(id_vars=["Corner","Driver"],value_vars=["Entry_Speed","Exit_Speed"],var_name="Phase",value_name="Speed")

corner_long["Phase"] = corner_long["Phase"].str.replace("_"," ")

fig_corner = px.bar(corner_long,x="Corner",y="Speed",color="Driver",barmode="group",facet_row="Phase",title="Corner Entry/Exit Speed Comparison") #! Original Bar graph

st.plotly_chart(fig_corner,width="stretch")

fig_corner = px.line(corner_long,x="Corner",y="Speed",color="Driver",line_dash="Phase",markers=True,title="Corner Entry/Exit Speed Comparison") #! Testing of Horizontal Line Graph

st.write(corner_df.head())

st.write(corner_long.head())

fig_corner.update_yaxes(categoryorder="category ascending")

st.plotly_chart(fig_corner,width="stretch") #! Plots only Major Braking zones/corners

st.write(full_tel_1.columns)

gear_exit_1 = extract_gear_exit_metrics(full_tel_1,driver_1)
gear_exit_2 =  extract_gear_exit_metrics(full_tel_2,driver_2)

gear_exit = pd.concat([gear_exit_1,gear_exit_2],ignore_index=True)

ref = gear_exit[gear_exit["Driver"] == driver_1][["Corner","Exit_Speed"]].rename(columns={"Exit_Speed":"Ref_Exit_Speed"})

gear_exit = gear_exit.merge(ref,on="Corner",how="left")

gear_exit["Exit_Gain"] = gear_exit["Exit_Speed"] - gear_exit["Ref_Exit_Speed"]

fig_shift = px.scatter(gear_exit,x="Exit_Gain",y="Shift_Speed",color="Driver",hover_data=["Corner"],title="Gear Shift Speed vs Corner Exit Speed")

fig_shift.add_hline(y=0,line_dash="dot")

st.plotly_chart(fig_shift,width="stretch")