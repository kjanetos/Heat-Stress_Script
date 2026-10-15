
import os
import glob
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory


def read_processed_files():

    # ----------------------------------------------------
    # Select folder
    # ----------------------------------------------------

    root = Tk()
    root.withdraw()

    folder = askdirectory(
        title="Select Processed Folder"
    )

    root.destroy()

    if not folder:
        raise Exception("No folder selected.")

    print("\n==============================")
    print("Reading Processed Files")
    print("==============================")

    print("Selected folder:")
    print(folder)

    processed = {}

    # ----------------------------------------------------
    # Find processed TEMP files
    # ----------------------------------------------------

    files = glob.glob(
        os.path.join(folder, "*_processed.csv")
    )

    print("\nProcessed files found:")

    if files:
        for file in files:
            print(" -", os.path.basename(file))
    else:
        print("No processed TEMP files found.")

    # ----------------------------------------------------
    # Read processed TEMP files
    # ----------------------------------------------------

    for file in files:

        filename = os.path.basename(file)

        # Example: DCG22ABE_D3_processed.csv
        name = os.path.splitext(filename)[0]

        name = name.replace(
            "_processed",
            "",
            1
        )

        if "_D" not in name:
            print(f"\nSkipping file: {filename}")
            print("Could not determine PID and Day.")
            continue

        try:
            pid, day = name.rsplit("_D", 1)
            pid = pid.strip()
            day = int(day)

        except Exception as e:
            print(f"\nSkipping file: {filename}")
            print("Reason:", e)
            continue

        print(f"\nReading: {filename}")

        try:
            df = pd.read_csv(file)

        except Exception as e:
            print(f"Could not read {filename}: {e}")
            continue

        print(f"PID = {pid}")
        print(f"Day = {day}")
        print(f"Rows = {len(df)}")

        processed[(pid, day)] = df

    # ----------------------------------------------------
    # Find status files for participants with missing TEMP
    # ----------------------------------------------------

    status_files = glob.glob(
        os.path.join(folder, "*_status.csv")
    )

    print("\nStatus files found:")

    if status_files:
        for file in status_files:
            print(" -", os.path.basename(file))
    else:
        print("No status files found.")

    # ----------------------------------------------------
    # Read status files
    # ----------------------------------------------------

    for file in status_files:

        filename = os.path.basename(file)

        try:
            status_df = pd.read_csv(file)

            if status_df.empty:
                print(f"Skipping empty status file: {filename}")
                continue

            # Check required columns
            required_columns = {"PID", "Day"}

            if not required_columns.issubset(status_df.columns):
                print(
                    f"Skipping {filename}: "
                    "PID or Day column is missing."
                )
                continue

            pid_value = status_df.iloc[0]["PID"]
            day_value = status_df.iloc[0]["Day"]

            if pd.isna(pid_value) or pd.isna(day_value):
                print(
                    f"Skipping {filename}: "
                    "PID or Day is empty."
                )
                continue

            pid = str(pid_value).strip()
            day = int(day_value)

            # Add the participant if TEMP data was not loaded
            if (pid, day) not in processed:

                processed[(pid, day)] = pd.DataFrame()

                print(
                    f"Added missing TEMP participant: "
                    f"PID={pid}, Day=D{day}"
                )

            else:
                print(
                    f"TEMP data already exists for "
                    f"PID={pid}, Day=D{day}"
                )

        except Exception as e:
            print(f"Could not read status file {filename}: {e}")

    # ----------------------------------------------------
    # Final check
    # ----------------------------------------------------

    if not processed:
        raise ValueError(
            "No processed TEMP files or status files "
            "were found in the selected folder."
        )

    print("\n==============================")
    print("All Participants Loaded")
    print("==============================")

    print("Total participants/days:", len(processed))

    for pid, day in sorted(processed.keys()):
        if processed[(pid, day)].empty:
            print(f"PID: {pid}, Day: D{day} - TEMP Missing")
        else:
            print(f"PID: {pid}, Day: D{day} - TEMP Available")

    return processed
