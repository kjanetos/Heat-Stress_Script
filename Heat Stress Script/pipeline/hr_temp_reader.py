import pandas as pd


def read_hr_temp(file=None):

    if file is None:
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename

        Tk().withdraw()

        file = askopenfilename(
            title="Select HR_TEMP File",
            filetypes=[("Excel Files", "*.xlsx")]
        )

        if not file:
            raise Exception("No HR_TEMP file selected.")

    df = pd.read_excel(file)

    return df, file