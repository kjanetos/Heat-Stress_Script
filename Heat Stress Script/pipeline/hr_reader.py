import os
import glob
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory


def read_hr_files():

    Tk().withdraw()

    folder = askdirectory(
        title="Select HR Folder"
    )

    if not folder:
        raise Exception("No HR folder selected.")

    hr_files = {}

    files = glob.glob(
        os.path.join(folder, "*.xlsx")
    )

    for file in files:

        filename = os.path.basename(file)

        # Example:
        # DCC740C2_D1_HR_20260730.xlsx

        parts = filename.replace(".xlsx", "").split("_")

        if len(parts) < 3:
            continue

        pid = parts[0]

        day = int(parts[1].replace("D", ""))

        df = pd.read_excel(
            file,
            header=13
        )

        hr_files[(pid, day)] = df

    return hr_files