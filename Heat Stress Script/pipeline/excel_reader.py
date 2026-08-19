import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename


def read_hr_temp():

    # Select HR_TEMP File
    Tk().withdraw()

    hr_temp_file = askopenfilename(
        title="Select HR_TEMP File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )

    if not hr_temp_file:
        raise Exception("No file selected.")

    # Select Field Collection ID Tracker 
    tracker_file = askopenfilename(     
        title="Select Field Collection ID Tracker File",     
        filetypes=[("Excel Files", "*.xlsx *.xls")] 
    ) 

    if not tracker_file:     
        raise Exception("No tracker file selected.")

    # Read HR_TEMP
    df = pd.read_excel(hr_temp_file)

    # Read Field Collection ID Tracker 
    tracker_df = pd.read_excel(tracker_file)

    # Match Collection ID to Site Address 
    df = df.merge(     
        tracker_df[["Collection ID", "Site Address"]],     
        on="Collection ID",     
        how="left"
    )

    # Convert times
    df["Onset_Time"] = pd.to_datetime(df["Onset_Time"])
    df["Offset_Time"] = pd.to_datetime(df["Offset_Time"])

    # First Start Time
    start_time = df["Onset_Time"].min()

    # Last End Time
    end_time = df["Offset_Time"].max()

    # Date
    work_date = start_time.strftime("%Y-%m-%d")

    return (
        df,
        hr_temp_file,
        work_date,
        start_time,
        end_time
    )