import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime, time, timedelta
import os

# --- GUI File Selection ---
def select_file(title, filetypes):
    """Opens a file dialog for the user to select a single file."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return file_path

def to_time_only(value):
    """Converts various time representations (time, datetime, Timestamp, string) to a datetime.time object."""
    if isinstance(value, time):
        return value
    elif isinstance(value, (datetime, pd.Timestamp)):
        return value.time()
    elif isinstance(value, str):
        # Attempt to parse with microseconds first, then without
        try:
            return datetime.strptime(value, "%H:%M:%S.%f").time()
        except ValueError:
            return datetime.strptime(value, "%H:%M:%S").time() 
    else:
        raise ValueError(f"Unsupported type for time conversion: {type(value)}")

def select_participant_day(df):
    """Opens a GUI window for the user to select Participant and Day from a DataFrame."""
    selected = {}

    def on_submit():
        selected["participant"] = participant_cb.get()
        selected["day"] = day_cb.get()
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.title("Select Participant and Day")

    tk.Label(root, text="Participant:").grid(row=0, column=0, padx=5, pady=5)
    participant_cb = ttk.Combobox(root, values=sorted(df["Participant"].dropna().astype(str).unique()), state="readonly")
    participant_cb.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Day:").grid(row=1, column=0, padx=5, pady=5)
    day_cb = ttk.Combobox(root, values=sorted(df["Day"].dropna().astype(str).unique()), state="readonly")
    day_cb.grid(row=1, column=1, padx=5, pady=5)

    submit_btn = tk.Button(root, text="Submit", command=on_submit)
    submit_btn.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

    return selected.get("participant"), selected.get("day")

def save_data_with_timestamp(df, base_filepath, identifier, prefix):
    """
    Saves a DataFrame to Excel or Parquet with a standardized timestamped filename.
    Output type is determined by the presence of '.xlsx' or '.xls' in the prefix argument.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        base_filepath (str): Path to the input file (used to determine base directory).
        identifier (str): A string identifier for the output file (e.g., 'PXX_DYY_TEMP').
        prefix (str): A descriptor for the type of output (e.g., 'PerDay.xlsx', 'S1_Trunc').
    """
    now = datetime.now()
    yyyymmdd = now.strftime("%Y%m%d")
    hhmm = now.strftime("%H%M")
    
    base_dir = os.path.dirname(base_filepath)
    
    # 1. Determine extension and safely clean prefix if extension is present
    prefix_lower = prefix.lower()
    
    if prefix_lower.endswith('.xlsx') or prefix_lower.endswith('.xls'):
        ext = '.xlsx'
        # Safely remove the extension from the descriptive prefix string
        if prefix_lower.endswith('.xlsx'):
            prefix = prefix[:-5]
        elif prefix_lower.endswith('.xls'):
            prefix = prefix[:-4]
    else:
        ext = '.parquet'
        
    # 2. Construct output filename: {identifier}_{prefix}_{YYYYMMDD}_{HHMM}{.ext}
    # Uses '_' as the timestamp separator, as requested.
    output_filename = f"{identifier}_{prefix}_{yyyymmdd}_{hhmm}{ext}"
    output_path = os.path.join(base_dir, output_filename)
    
    # 3. Save file
    if ext == '.xlsx':
        df.to_excel(output_path, index=False)
    elif ext == '.parquet':
        df.to_parquet(output_path, index=False)
        
    print(f"✅ Saved results to {output_path}")
    return output_path