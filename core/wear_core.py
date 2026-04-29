import pandas as pd
from scipy.stats import linregress

def build_stint_dataframe(session,driver):
    
    laps = session.laps.pick_driver(driver).copy()

    laps = laps.reset_index(drop=True)

    laps["Lap_Number"] = laps["LapNumber"]
    laps["Lap_Time"] = laps["LapTime"].dt.total_seconds()
    laps["Compound_Type"] = laps["Compound"]
    laps["Stint_ID"] = laps["Stint"]
    laps["Pit_Lap"] = laps["PitInTime"].notna() | laps["PitOutTime"].notna()

    laps["Lap_In_Stint"] = (laps.groupby("Stint_ID").cumcount()+1)

    return laps[["Lap_Number","Stint_ID","Lap_In_Stint","Compound_Type","Lap_Time","Pit_Lap"]]
    

def stint_degradation_metrics(stint_df):
    
    results= []

    for stint,group in stint_df.groupby("Stint_ID"):

        if len(group) < 5:

            continue

        group = group.sort_values("Lap_Number")

        base_lap = group.iloc[0]["Lap_Time"]
        last_lap = group.iloc[-1]["Lap_Time"]

        degradation = last_lap - base_lap

        avg_lap = group["Lap_Time"].mean()

        results.append({
            "Stint_ID":stint,
            "Compound_Type": group["Compound_Type"].iloc[0],
            "Lap_Count":len(group),
            "Total_Degradation":degradation,
            "Avg_Lap_Time":avg_lap
        })

    return pd.DataFrame(results)

def compute_stint_degradation(stint_df, min_laps=5):

    degradation_rows = []

    required = {
        "Stint_ID",
        "Lap_In_Stint",
        "Lap_Time",
        "Compound_Type"
    }

    if not required.issubset(stint_df.columns):
        return pd.DataFrame()

    for stint, group in stint_df.groupby("Stint_ID"):

        # Remove pit laps per-stint (NOT globally)
        if "Pit_Lap" in group.columns:
            group = group[group["Pit_Lap"] == False]

        # Remove invalid lap times
        group = group.dropna(subset=["Lap_Time", "Lap_In_Stint"])

        if len(group) < min_laps:
            continue

        x = group["Lap_In_Stint"].astype(float)
        y = group["Lap_Time"].astype(float)

        slope, intercept, r, p, stderr = linregress(x, y)

        degradation_rows.append({
            "Stint_Number": stint,
            "Compound_Type": group["Compound_Type"].iloc[0],
            "Laps": len(group),
            "Degradation_s_per_lap": slope,
            "R_squared": r ** 2
        })

    return pd.DataFrame(degradation_rows)

def detect_tyre_cliff(stint_df,threshold_multiplier=0.8):

    df = stint_df.copy()

    df = df.sort_values("Lap_In_Stint")

    df["Delta_Lap_Time"] = df["Lap_Time"].diff()

    mean_delta = df["Delta_Lap_Time"].mean()

    std_delta = df["Delta_Lap_Time"].std()

    threshold = mean_delta + threshold_multiplier * std_delta

    cliff_rows = df[df["Delta_Lap_Time"] > threshold]

    if cliff_rows.empty:
        
        return None
    
    return int(cliff_rows.iloc[0]["Lap_In_Stint"])

