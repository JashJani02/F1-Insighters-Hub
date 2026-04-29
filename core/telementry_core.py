import pandas as pd
import numpy as np

def get_fastest_lap_telementry(session,driver_code):

    laps =  session.laps.pick_driver(driver_code)

    fastest_lap = laps.pick_fastest()

    telemetry = fastest_lap.get_telemetry()

    telemetry = telemetry.copy()
    
    telemetry["Driver"] = driver_code

    return telemetry

def get_telemetry_channels(session,driver_code,channels):

    laps = session.laps.pick_driver(driver_code)

    fastest_lap = laps.pick_fastest()

    telemetry = fastest_lap.get_telemetry().copy()

    data = []

    for channel in channels:

        df = telemetry[["Distance",channel]].copy()

        df.rename(columns={channel:"Value"},inplace=True)

        df["Channel"] = channel

        df["Driver"] = driver_code

        data.append(df)

    return pd.concat(data,ignore_index=True)

def get_delta_dataframe(session,driver_ref,driver_comp):

    lap_ref = session.laps.pick_driver(driver_ref).pick_fastest()
    tel_ref = lap_ref.get_telemetry().copy()

    lap_comp = session.laps.pick_driver(driver_comp).pick_fastest()
    tel_comp = lap_comp.get_telemetry().copy()

    tel_ref = tel_ref[["Distance","Speed","X","Y"]].rename(columns={"Speed":"Speed_ref"})
    tel_comp = tel_comp[["Distance","Speed"]].rename(columns={"Speed":"Speed_comp"})

    tel_comp_interpolated = pd.merge_asof(tel_ref.sort_values("Distance"),tel_comp.sort_values("Distance"),on="Distance",direction="nearest")

    return tel_comp_interpolated

def compute_delta(delta_df):

    vel_ref = delta_df["Speed_ref"]/3.6
    vel_comp = delta_df["Speed_comp"]/3.6

    distance = delta_df["Distance"].diff().fillna(0)

    time_ref = distance/vel_ref
    time_comp = distance/vel_comp

    delta_time = (time_comp - time_ref).cumsum()

    delta_df["Delta_time"] = delta_time

    return delta_df

def add_minisectors(delta_df,num_sectors=25):

    total_distance = delta_df["Distance"].max()

    sector_lenght = total_distance/num_sectors

    delta_df["Minisector"] = (delta_df["Distance"]//sector_lenght).astype(int)

    return delta_df

def minisector_dominance(delta_df,driver_ref,driver_comp):

    sector_delta = (delta_df.groupby("Minisector")["Delta_time"].last().diff().fillna(0))

    dominance = sector_delta.apply(lambda x: driver_comp if x<0 else driver_ref)

    return dominance.reset_index(name="Winner")

def merge_dominance(delta_df,dominance_df):

    return delta_df.merge(dominance_df,on="Minisector")

def get_gear_telemetry(session,driver_code):

    laps = session.laps.pick_driver(driver_code)

    fastest_lap = laps.pick_fastest()

    telemetry = fastest_lap.get_telemetry().copy()

    df = telemetry[["Distance","nGear"]].copy()

    df["Driver"] = driver_code

    return df