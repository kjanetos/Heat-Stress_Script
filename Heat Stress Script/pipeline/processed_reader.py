import os
import glob
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory


def read_processed_files():

    Tk().withdraw()

    folder = askdirectory(
        title="Select Processed Folder"
    )

    if not folder:
        raise Exception(
            "No folder selected."
        )

    print("\n==============================")
    print("Reading Processed Files")
    print("==============================")

    print("Selected folder:")
    print(folder)

    processed = {}

    # ----------------------------------------------------
    # Find CSV processed files
    # ----------------------------------------------------

    files = glob.glob(
        os.path.join(folder, "*_processed.csv")
    )

    print("\nProcessed files found:")

    for file in files:
        print(
            " -",
            os.path.basename(file)
        )

    if not files:
        raise ValueError(
            "No processed CSV files were found "
            "in the selected folder."
        )

    # ----------------------------------------------------
    # Read files
    # ----------------------------------------------------

    for file in files:

        filename = os.path.basename(file)

        # Example:
        # DCG22ABE_D3_processed.csv

        name = os.path.splitext(filename)[0]

        # Remove "_processed"
        name = name.replace(
            "_processed",
            "",
            1
        )

        # Example:
        # DCG22ABE_D3

        if "_D" not in name:

            print(
                "\nSkipping file:",
                filename
            )

            print(
                "Could not determine PID and Day."
            )

            continue

        try:

            pid, day = name.rsplit(
                "_D",
                1
            )

            day = int(day)

        except Exception as e:

            print(
                "\nSkipping file:",
                filename
            )

            print(
                "Reason:",
                e
            )

            continue

        # ------------------------------------------------
        # Read CSV
        # ------------------------------------------------

        print(
            f"\nReading: {filename}"
        )

        df = pd.read_csv(
            file
        )

        print(
            f"PID = {pid}"
        )

        print(
            f"Day = {day}"
        )

        print(
            f"Rows = {len(df)}"
        )

        processed[
            (pid, day)
        ] = df

    # ----------------------------------------------------
    # Final check
    # ----------------------------------------------------

    print("\n==============================")
    print("Processed Files Loaded")
    print("==============================")

    print(
        "Number of processed files:",
        len(processed)
    )

    for key in processed.keys():

        print(
            " -",
            key
        )

    if not processed:

        raise ValueError(
            "No valid processed CSV files were found."
        )

    return processed