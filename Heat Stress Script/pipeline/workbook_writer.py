import pandas as pd

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def save_workbook(
    hr_df,
    summary_df,
    processed,
    hr_files,
    assessment_results,
    output_file
):

    # ============================================================
    # Create Workbook
    # ============================================================

    wb = Workbook()


    # ============================================================
    # 1. HR_TEMP sheet
    # ============================================================

    ws = wb.active
    ws.title = "HR_TEMP"

    for row in dataframe_to_rows(
        hr_df,
        index=False,
        header=True
    ):
        ws.append(row)


    # Keep Date format
    if "Date" in hr_df.columns:

        date_col = (
            hr_df.columns.get_loc("Date") + 1
        )

        for row in range(
            2,
            ws.max_row + 1
        ):

            ws.cell(
                row=row,
                column=date_col
            ).number_format = "yyyy-mm-dd"


    # ============================================================
    # 2. Summary sheet
    # ============================================================

    summary_ws = wb.create_sheet(
        "Summary"
    )

    for row in dataframe_to_rows(
        summary_df,
        index=False,
        header=True
    ):
        summary_ws.append(row)


    # ============================================================
    # 3. Processed TEMP + Weather sheets
    # ============================================================

    order = sorted(
        processed.keys(),
        key=lambda x: (
            x[0],
            x[1]
        )
    )


    for key in order:

        pid, day = key

        sheet_name = (
            f"{pid}_D{day}"
        )

        sheet = wb.create_sheet(
            sheet_name
        )

        df = processed[key]


        # --------------------------------------------------------
        # Write processed TEMP + Weather data
        # --------------------------------------------------------

        for row in dataframe_to_rows(
            df,
            index=False,
            header=True
        ):
            sheet.append(row)


        # --------------------------------------------------------
        # If HR data exists, add HR information
        # --------------------------------------------------------

        if key in hr_files:

            hr_data = hr_files[key]

            if hr_data is not None:

                print(
                    f"HR data available for "
                    f"{pid} D{day}"
                )


        # --------------------------------------------------------
        # Assessment result
        # --------------------------------------------------------

        if key in assessment_results:

            assessment = (
                assessment_results[key]
            )

            print(
                f"Assessment available for "
                f"{pid} D{day}"
            )


    # ============================================================
    # 4. Save workbook
    # ============================================================

    wb.save(
        output_file
    )


    print(
        "\nWorkbook saved:"
    )

    print(
        output_file
    )