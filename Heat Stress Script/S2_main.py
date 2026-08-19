import os
import tempfile
import pandas as pd

from tkinter import Tk
from tkinter.filedialog import (
    askopenfilename,
    asksaveasfilename
)

from pipeline.processed_reader import read_processed_files
from pipeline.workbook_writer import save_workbook
from pipeline.summary_builder import build_summary

from pipeline.hr_temp_reader import read_hr_temp

from pipeline.demographics_reader import read_demographics
from pipeline.assessment_calculator import calculate_assessment

from pipeline.azure_hr_reader import (
    find_hr_file,
    download_hr_file
)

from pipeline.assessment_writer import (
    write_assessment_results
)


# ============================================================
# Clean HR Data
# ============================================================

def clean_hr_data(hr_data):

    hr_data = hr_data.copy()

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    hr_data.columns = (
        hr_data.columns
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Check BPM column
    # --------------------------------------------------------

    if "BPM" not in hr_data.columns:

        raise ValueError(
            "BPM column not found after reading HR file. "
            f"Available columns: {hr_data.columns.tolist()}"
        )

    # --------------------------------------------------------
    # Convert BPM to numeric
    # --------------------------------------------------------

    before_rows = len(hr_data)

    hr_data["BPM"] = pd.to_numeric(
        hr_data["BPM"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove BPM = 0 and invalid BPM values
    # --------------------------------------------------------

    hr_data = hr_data[
        hr_data["BPM"] > 0
    ].copy()

    after_rows = len(hr_data)

    removed_rows = (
        before_rows - after_rows
    )

    print(
        f"[HR CLEANING] Removed {removed_rows} "
        f"invalid HR rows (BPM <= 0 or invalid)."
    )

    print(
        f"[HR CLEANING] Remaining HR rows: "
        f"{after_rows}"
    )

    # --------------------------------------------------------
    # Check if any valid HR data remains
    # --------------------------------------------------------

    if hr_data.empty:

        raise ValueError(
            "No valid HR data remains after removing "
            "BPM = 0 or invalid values."
        )

    return hr_data


# ============================================================
# Initialize Tkinter
# ============================================================

Tk().withdraw()


# ============================================================
# STEP 1
# Read Processed TEMP + Weather files
# ============================================================

print("\n" + "=" * 60)
print("STEP 1 - Read Processed TEMP files")
print("=" * 60)

processed = read_processed_files()

if not processed:

    raise Exception(
        "No processed TEMP files were found."
    )

print("\nProcessed files found:")

for pid, day in processed.keys():

    print(
        f"  PID : {pid}   Day : D{day}"
    )


# ============================================================
# STEP 2
# Select existing HR_TEMP Export Workbook
# ============================================================

print("\n" + "=" * 60)
print("STEP 2 - Select HR_TEMP Export Workbook")
print("=" * 60)

hr_export_file = askopenfilename(
    title="Select HR_TEMP Export Workbook",
    filetypes=[
        ("Excel Files", "*.xlsx")
    ]
)

if not hr_export_file:

    raise Exception(
        "No HR_TEMP export workbook selected."
    )

print(
    "\nSelected HR_TEMP workbook:"
)

print(
    hr_export_file
)


# ------------------------------------------------------------
# Read existing HR_TEMP data
# ------------------------------------------------------------

hr_df, _ = read_hr_temp(
    hr_export_file
)


# ============================================================
# STEP 3
# Search and Download HR files from Azure
# ============================================================

print("\n" + "=" * 60)
print("STEP 3 - Search HR files in Azure")
print("=" * 60)


hr_files = {}


download_folder = tempfile.mkdtemp(
    prefix="HR_Azure_"
)


for (pid, day), processed_df in processed.items():

    print("\n" + "-" * 60)

    print(
        "Searching HR for:"
    )

    print(
        "PID :", pid
    )

    print(
        "Day : D" + str(day)
    )

    print("-" * 60)


    # ========================================================
    # Search Azure
    # ========================================================

    hr_blob = find_hr_file(
        pid,
        day
    )


    # ========================================================
    # HR NOT FOUND IN AZURE
    # ========================================================

    if hr_blob is None:

        print(
            f"No HR file found in Azure for "
            f"{pid} D{day}"
        )

        print(
            "Please select the HR file manually."
        )


        manual_hr_file = askopenfilename(
            title=f"Select HR File - {pid} D{day}",
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("All Files", "*.*")
            ]
        )


        # ----------------------------------------------------
        # No HR file available
        # ----------------------------------------------------

        if not manual_hr_file:

            print(
                f"No HR file available for "
                f"{pid} D{day}."
            )

            print(
                "HR assessment will be skipped."
            )

            hr_files[
                (pid, day)
            ] = None

            continue


        # ----------------------------------------------------
        # Manual HR file selected
        # ----------------------------------------------------

        print(
            "\nManually selected HR file:"
        )

        print(
            manual_hr_file
        )


        # ----------------------------------------------------
        # Read manual HR workbook
        # ----------------------------------------------------

        hr_data = pd.read_excel(
            manual_hr_file,
            sheet_name="1MIN",
            header=13
        )


        # ----------------------------------------------------
        # Clean HR data
        # ----------------------------------------------------

        hr_data = clean_hr_data(
            hr_data
        )


        print(
            "\n[DEBUG] HR columns:"
        )

        print(
            hr_data.columns.tolist()
        )


        print(
            "HR rows:",
            len(hr_data)
        )


        # ----------------------------------------------------
        # Store HR data
        # ----------------------------------------------------

        hr_files[
            (pid, day)
        ] = hr_data


        continue


    # ========================================================
    # HR FOUND IN AZURE
    # ========================================================

    hr_file = download_hr_file(
        hr_blob,
        download_folder
    )


    print(
        "\nDownloaded HR file:"
    )

    print(
        hr_file
    )


    # --------------------------------------------------------
    # Read Azure HR workbook
    # --------------------------------------------------------

    hr_data = pd.read_excel(
        hr_file,
        sheet_name="1MIN",
        header=13
    )


    # --------------------------------------------------------
    # Clean HR data
    # --------------------------------------------------------

    hr_data = clean_hr_data(
        hr_data
    )


    print(
        "\n[DEBUG] HR columns:"
    )

    print(
        hr_data.columns.tolist()
    )


    print(
        "HR rows:",
        len(hr_data)
    )


    # --------------------------------------------------------
    # Store HR data
    # --------------------------------------------------------

    hr_files[
        (pid, day)
    ] = hr_data


# ============================================================
# STEP 4
# Select Demographics
# ============================================================

print("\n" + "=" * 60)
print("STEP 4 - Select Demographics")
print("=" * 60)


demographics = read_demographics()


# ============================================================
# STEP 5
# Calculate Heat Stress Assessment
# ============================================================

print("\n" + "=" * 60)
print("STEP 5 - Calculate Heat Stress Assessment")
print("=" * 60)


assessment_results = {}


for (pid, day), hr_data in hr_files.items():


    # ========================================================
    # No HR file
    # ========================================================

    if hr_data is None:

        print(
            f"Skipping assessment for "
            f"{pid} D{day}"
            " - HR file not found."
        )

        continue


    # ========================================================
    # Demographics
    #
    # IMPORTANT:
    # Match Demographics by PID ONLY.
    # Day is NOT used.
    # ========================================================

    if pid not in demographics:

        print(
            f"Skipping assessment for "
            f"{pid} D{day}"
            " - Demographics not found."
        )

        continue


    # ========================================================
    # Get Sex and Weight
    # ========================================================

    sex = demographics[
        pid
    ][
        "Sex"
    ]


    weight = demographics[
        pid
    ][
        "Weight"
    ]


    print(
        f"Calculating assessment: "
        f"{pid} D{day}"
    )


    # ========================================================
    # Calculate Assessment
    # ========================================================

    assessment_results[
        (pid, day)
    ] = calculate_assessment(
        hr_data,
        sex,
        weight
    )


print(
    "\nAssessment results created:",
    len(assessment_results)
)


# ============================================================
# STEP 6
# Build Summary
# ============================================================

print("\n" + "=" * 60)
print("STEP 6 - Build Summary")
print("=" * 60)


summary_df = build_summary(
    processed
)


# ============================================================
# STEP 7
# Create Temporary HR_TEMP_With_Weather Workbook
# ============================================================

print("\n" + "=" * 60)
print("STEP 7 - Create Temporary Workbook")
print("=" * 60)


temp_workbook = os.path.join(
    tempfile.gettempdir(),
    "HR_TEMP_With_Weather_temp.xlsx"
)


save_workbook(
    hr_df,
    summary_df,
    processed,
    hr_files,
    assessment_results,
    temp_workbook
)


print(
    "\nTemporary workbook created:"
)

print(
    temp_workbook
)


# ============================================================
# STEP 8
# Select FINAL Output File
# ============================================================

print("\n" + "=" * 60)
print("STEP 8 - Save Final Heat Stress Assessment")
print("=" * 60)


output = asksaveasfilename(
    title="Save Final Heat Stress Assessment",
    defaultextension=".xlsx",
    initialfile="HR_TEMP_HeatStress_Assessment.xlsx",
    filetypes=[
        ("Excel Files", "*.xlsx")
    ]
)


if not output:

    raise Exception(
        "No output file selected."
    )


# ============================================================
# STEP 9
# Apply Assessment Writer
# ============================================================

print(
    "\nApplying Heat Stress Assessment..."
)


write_assessment_results(
    temp_workbook,
    assessment_results,
    output
)


# ============================================================
# STEP 10
# Delete Temporary Workbook
# ============================================================

if os.path.exists(
    temp_workbook
):

    os.remove(
        temp_workbook
    )


# ============================================================
# Completed
# ============================================================

print("\n" + "=" * 60)
print("Completed!")
print("=" * 60)


print(
    "\nFinal file:"
)

print(
    output
)