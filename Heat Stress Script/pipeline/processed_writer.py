import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def save_processed(df, pid, day, output_folder):

    if not output_folder:
        raise ValueError("Output folder is required.")

    # ========================================================
    # Processed file name
    # ========================================================

    filename = f"{pid}_D{day}_processed.csv"

    output_path = os.path.join(
        output_folder,
        filename
    )

    # ========================================================
    # Save as CSV
    # ========================================================

    df.to_csv(
        output_path,
        index=False
    )

    print("\nProcessed file saved:")
    print(output_path)

    return output_path