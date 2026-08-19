import pandas as pd
 
def estimate_globe_temperature(
    air_temp,
    solar_radiation,
    wind_speed
):
    globe_temp = (
        air_temp
        + (0.0178 * solar_radiation)
        - (0.45 * wind_speed)
    )
 
    return round(globe_temp, 2)
 
 
def calculate_wbgt(
    air_temp,
    wet_bulb,
    globe_temp
):
    wbgt = (
        0.7 * wet_bulb
        + 0.2 * globe_temp
        + 0.1 * air_temp
    )
 
    return round(wbgt, 2)
 
 
def calculate_twa_wbgt(day_df):
 
    day_df = day_df.copy()
 
    total_weighted_wbgt = 0
    total_duration = 0
 
    for _, row in day_df.iterrows():
 
        if pd.isna(row["WBGT (°C)"]) or pd.isna(row["Duration"]):
            continue
 
        duration = pd.to_timedelta(row["Duration"])
        duration_hours = duration.total_seconds() / 3600
 
        total_weighted_wbgt += row["WBGT (°C)"] * duration_hours
        total_duration += duration_hours
 
    if total_duration == 0:
        return None
 
    return round(total_weighted_wbgt / total_duration, 2)