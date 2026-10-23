import pandas as pd
import tempfile
import os

from pipeline.weather_api import (
    get_coordinates,
    get_hourly_weather,
    get_weather_for_time,
)

from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

from pipeline.raw_temp_reader import read_raw_temp
from pipeline.master_data_reader import (
    load_master_data,
    get_start_end_time,
)
from Utils.data_utils import select_participant_day
from pipeline.trimmer import trim_to_work_window
from pipeline.processed_writer import save_processed

from pipeline.wbgt import (
    estimate_globe_temperature,
    calculate_wbgt,
    calculate_twa_wbgt,
)

from pipeline.cav_input import load_cav_intervals

from pipeline.nas_reader import find_raw_temp
from pipeline.nas_reader import download_raw_temp

root = Tk()
root.withdraw()

master_file = askopenfilename(
    title="Select Master Data File"
)

if not master_file:
    root.destroy()
    raise Exception("No master data file was selected.")

site_name = os.path.splitext(
    os.path.basename(master_file)
)[0]

master_df = load_master_data(master_file)

pid, day = select_participant_day(master_df)

day = int(float(day))

output_folder = askdirectory(
    title="Select Output Folder"
)

if not output_folder:
    raise Exception("No output folder was selected.")

# ============================================================
# Search Raw TEMP in NAS
# ============================================================

remote_temp_file = find_raw_temp(
    pid,
    day
)


# ============================================================
# If found in NAS
# ============================================================

if remote_temp_file is not None:

    # Download Raw TEMP to a temporary folder
    download_folder = tempfile.mkdtemp(
        prefix="raw_temp_"
    )

    raw_temp_file = download_raw_temp(
        remote_temp_file,
        download_folder
    )

    if not raw_temp_file:
        raise Exception(
            "The Raw TEMP file was found in NAS, "
            "but the download failed."
        )

    print(
        "\n[CHECKPOINT] NAS raw file downloaded "
        "to temporary folder."
    )

# ============================================================
# If NOT found in NAS
# ============================================================

else:

    print(
        f"\nRaw TEMP file not found for {pid} D{day}."
    )

    from tkinter import messagebox

    messagebox.showinfo(
        "Raw TEMP Not Found",
        f"Raw TEMP file for PID {pid}, D{day} "
        "was not found on NAS.\n"
        "Please select the Raw TEMP CSV file manually."
    )

    raw_temp_file = askopenfilename(
        title=f"Select Raw TEMP File - PID {pid}, D{day}",
        filetypes=[("CSV Files", "*.csv")]
    )

    # --------------------------------------------------------
    # If a file is selected manually
    # --------------------------------------------------------
    if raw_temp_file:

        print("\n[CHECKPOINT] Raw TEMP file selected manually:")
        print(raw_temp_file)

    # --------------------------------------------------------
    # If no file is selected, create Missing status CSV
    # --------------------------------------------------------
    else:

        status_df = pd.DataFrame([{
            "PID": pid,
            "Day": day,
            "TEMP Status": "Missing"
        }])

        status_file = os.path.join(
            output_folder,
            f"{pid}_D{day}_status.csv"
        )

        status_df.to_csv(
            status_file,
            index=False
        )

        print("\nTEMP status file created:")
        print(status_file)

        root.destroy()
        raise SystemExit(0)


# ============================================================
# Read Raw TEMP
# ============================================================

print(
    f"\n[CHECKPOINT] About to call read_raw_temp() on: "
    f"{raw_temp_file}"
)

df = read_raw_temp(raw_temp_file)

print(
    "[CHECKPOINT] read_raw_temp() finished successfully."
)

# ============================================================
# Find TEMP time column 
# ============================================================

time_columns = [
    col
    for col in df.columns
    if str(col).strip().lower().startswith("time [utc-ofs=")
]

if not time_columns:
    raise ValueError(
        "TEMP time column was not found."
    )

TIME_COL = time_columns[0]

print("\nDetected TEMP time column:")
print(TIME_COL)


start_time, end_time = get_start_end_time(
    master_df,
    pid,
    day
)

df = trim_to_work_window(
    df,
    TIME_COL,
    start_time,
    end_time
)

# Add Weather Columns
df["Temperature (°C)"] = None
df["Relative Humidity (%)"] = None
df["Dew Point (°C)"] = None
df["Apparent Temperature (°C)"] = None
df["Wet Bulb (°C)"] = None
df["Globe Temperature (°C)"] = None
df["WBGT (°C)"] = None
df["Clothing Type"] = None
df["CAV"] = None
df["WBGTeff (°C)"] = None

print("\n[CHECKPOINT] Reached site address prompt.")

site_address = input("Site Address: ").strip()

if not site_address:
    raise Exception("Site Address is required.")

lat, lon = get_coordinates(site_address)

if lat is None:
    raise Exception(f"Could not geocode address: {site_address}")

work_date = pd.Timestamp(start_time).strftime("%Y-%m-%d")

weather = get_hourly_weather(
    lat,
    lon,
    work_date
)

for index, row in df.iterrows():

    weather_row = get_weather_for_time(
        weather,
        row[TIME_COL]
    )

    if weather_row is None:
        continue

    globe_temp = estimate_globe_temperature(
        weather_row["Temperature"],
        weather_row["Solar Radiation"],
        weather_row["Wind Speed"]
    )

    wbgt = calculate_wbgt(
        weather_row["Temperature"],
        weather_row["Wet Bulb"],
        globe_temp
    )

    df.loc[index, "Temperature (°C)"] = round(weather_row["Temperature"], 2)
    df.loc[index, "Relative Humidity (%)"] = round(weather_row["Relative Humidity"], 2)
    df.loc[index, "Dew Point (°C)"] = round(weather_row["Dew Point"], 2)
    df.loc[index, "Apparent Temperature (°C)"] = round(weather_row["Apparent Temperature"], 2)
    df.loc[index, "Wet Bulb (°C)"] = round(weather_row["Wet Bulb"], 2)
    df.loc[index, "Globe Temperature (°C)"] = round(globe_temp, 2)
    df.loc[index, "WBGT (°C)"] = round(wbgt, 2)

df_calc = df.copy()

gaps = df_calc[TIME_COL].diff().shift(-1)

df_calc["Duration"] = gaps.fillna(gaps.median())

twa = calculate_twa_wbgt(df_calc)

df["TWA WBGT (°C)"] = twa


# ============================================================
# Load clothing intervals from Live Notation
# ============================================================

cav_intervals = load_cav_intervals()

# Initialize columns
df["Clothing Type"] = None
df["CAV"] = None
df["WBGTeff (°C)"] = None

if cav_intervals is None:
    print("CAV file selection cancelled. Skipping CAV calculation.")

else:
    # Normalize TEMP timestamps
    df[TIME_COL] = pd.to_datetime(
        df[TIME_COL],
        errors="coerce"
    )

    print("\n[DEBUG] TEMP time samples:")
    print(df[TIME_COL].head(5).to_list())

    print("\n[DEBUG] Clothing interval samples:")

    for interval in cav_intervals[:3]:
        print(
            repr(interval["Start Time"]),
            "to",
            repr(interval["End Time"]),
            "|",
            interval["Clothing Type"],
            "| CAV:",
            interval["CAV"]
        )

    # Apply clothing intervals
    for i, interval in enumerate(cav_intervals):
        interval_start = interval["Start Time"]
        interval_end = interval["End Time"]

        # Include start, exclude end to avoid duplicate boundary matches
        mask = (
            (df[TIME_COL] >= interval_start)
            & (df[TIME_COL] < interval_end)
        )

        # Include the final endpoint of the last interval
        if i == len(cav_intervals) - 1:
            mask = (
                (df[TIME_COL] >= interval_start)
                & (df[TIME_COL] <= interval_end)
            )

        df.loc[mask, "Clothing Type"] = interval["Clothing Type"]
        df.loc[mask, "CAV"] = interval["CAV"]

    # Calculate effective WBGT
    df["WBGTeff (°C)"] = (
        pd.to_numeric(df["WBGT (°C)"], errors="coerce")
        + pd.to_numeric(df["CAV"], errors="coerce")
    )

    # Check matching results
    matched = df["Clothing Type"].notna().sum()
    unmatched = df["Clothing Type"].isna().sum()

    print(f"CAV matched rows: {matched}")
    print(f"CAV unmatched rows: {unmatched}")

    if unmatched > 0:
        print("Unmatched TEMP timestamps:")
        print(
            df.loc[ df["Clothing Type"].isna(), TIME_COL]
            .head(10)
            .to_list()
        )

# Convert time to a clean datetime format before saving
df[TIME_COL] = pd.to_datetime(
    df[TIME_COL],
    errors="coerce"
)

# Remove timezone information if present
if hasattr(df[TIME_COL].dt, "tz") and df[TIME_COL].dt.tz is not None:
    df[TIME_COL] = df[TIME_COL].dt.tz_localize(None)

# Remove microseconds
df[TIME_COL] = df[TIME_COL].dt.floor("s")

save_processed(
    df,
    pid,
    day,
    output_folder
)

print("\nCompleted!")

root.destroy()