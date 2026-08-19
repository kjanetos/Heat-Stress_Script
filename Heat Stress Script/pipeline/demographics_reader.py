import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename


def read_demographics():

    Tk().withdraw()

    file = askopenfilename(
        title="Select Demographics File",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if not file:
        raise Exception("No demographics file selected.")

    df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    demographics = {}

    for _, row in df.iterrows():

        pid = str(row["PID"]).strip()

        sex = str(row["DV_sex"]).strip().lower()

        if sex == "male":
            sex = 1
        elif sex == "female":
            sex = 2
        else:
            sex = None

        weight = row["wt_kg"]

        demographics[pid] = {
            "Sex": sex,
            "Weight": weight
        }

    return demographics