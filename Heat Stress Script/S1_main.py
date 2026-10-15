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

from pipeline.cav_input import select_cav

from pipeline.nas_reader import find_raw_temp
from pipeline.nas_reader import download_raw_temp

from tkinter import messagebox

Tk().withdraw()

master_file = askopenfilename(
    title="Select Master Data File"
)

site_name = os.path.splitext(
    os.path.basename(master_file)
)[0]

master_df = load_master_data(master_file)

pid, day = select_participant_day(master_df)

day = int(float(day))

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

    # Save NAS Raw TEMP only temporarily.
    # It will NOT be saved to the user's output folder.
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

    messagebox.showinfo(
        "Raw TEMP",
        "Raw TEMP file was not found in NAS.\n"
        "Please select the Raw TEMP file manually."
    )

    raw_temp_file = askopenfilename(
        title="Select Raw Temp File"
    )


# ============================================================
# Check file selection
# ============================================================

if not raw_temp_file:

    raise Exception(
        "No Raw TEMP file was selected."
    )

print(f"\n[CHECKPOINT] About to call read_raw_temp() on: {raw_temp_file}")

df = read_raw_temp(raw_temp_file)

print("[CHECKPOINT] read_raw_temp() finished successfully.")

# ============================================================
# Find TEMP time column regardless of UTC offset
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

CAV_TABLE = {
    1: ("Short sleeves and pants", -1),
    2: ("Work clothes (long sleeve shirt and pants)", 0),
    3: ("Cloth coveralls", 0),
    4: ("SMS polypropylene coveralls", 0.5),
    5: ("Polyolefin coveralls", 1),
    6: ("Double-layer woven clothing", 3),
    7: ("Limited-use vapour-barrier coveralls", 11),
    8: ("Adding a hood (full head and neck covering; not face)", 1)
}

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

clothing, cav = select_cav(pid, day)

df["Clothing Type"] = clothing
df["CAV"] = cav
df["WBGTeff (°C)"] = df["WBGT (°C)"] + cav

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

output_folder = askdirectory(
    title="Select Output Folder"
)

if not output_folder:
    raise Exception("No output folder was selected.")

save_processed(
    df,
    pid,
    day,
    output_folder
)

print("\nCompleted!")