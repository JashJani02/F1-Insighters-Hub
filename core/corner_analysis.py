import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def extract_corners(telemetry,min_distance=200):

    speed = telemetry["Speed"].values

    peaks, _ = find_peaks(-speed,distance=min_distance)

    corners = []

    for index, p in enumerate(peaks,start=1):

        corners.append({
            "Corner":f"Turn{index}",
            "Distance":telemetry.iloc[p]["Distance"],
            "Min_Speed":telemetry.iloc[p]["Speed"],
            "Index":p,
        })

    return pd.DataFrame(corners)

def corner_entry_exit_metrics(telemetry,corners,window=50):\

    results= []

    for _, corner in corners.iterrows():

        index = int(corner["Index"])

        entry_index = max(index - window,0)
        exit_index = min(index + window,len(telemetry)-1)

        entry_speed = telemetry.iloc[entry_index]["Speed"]
        exit_speed = telemetry.iloc[exit_index]["Speed"]

        results.append({
            "Corner":corner["Corner"],
            "Entry_Speed":entry_speed,
            "Exit_Speed":exit_speed,
        })

    return pd.DataFrame(results)

def extract_gear_exit_metrics(telemetry,driver):

    required = {"Distance", "Speed", "nGear"}
    if not required.issubset(telemetry.columns):
        return pd.DataFrame()

    corners = extract_corners(telemetry)

    if corners.empty:
        return pd.DataFrame()

    tel = _add_corner_labels_internal(telemetry, corners)

    results = []

    for corner, group in tel.groupby("Corner"):

        if len(group) < 10:
            continue

        group = group.sort_values("Distance")

        gear_diff = group["nGear"].diff()
        upshifts = group[gear_diff > 0]

        if upshifts.empty:
            continue

        last_shift = upshifts.iloc[-1]
        exit_point = group.iloc[-1]

        results.append({
            "Corner": corner,
            "Driver": driver,
            "Shift_Distance": last_shift["Distance"],
            "Shift_Speed": last_shift["Speed"],
            "Exit_Speed": exit_point["Speed"]
        })

    return pd.DataFrame(results)


def _add_corner_labels_internal(telemetry,corners):

    tel = telemetry.copy()

    tel["Corner"] = None

    for _, corner in corners.iterrows():

        tel.loc[corner["Index"],"Corner"] = corner["Corner"]

    tel["Corner"] = tel["Corner"].ffill().bfill()

    return tel