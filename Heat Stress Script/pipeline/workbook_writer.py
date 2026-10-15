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
    # 1. Summary sheet
    # ============================================================

    summary_ws = wb.active
    summary_ws.title = "Summary"

    for row in dataframe_to_rows(
        summary_df,
        index=False,
        header=True
    ):
        summary_ws.append(row)


    # ============================================================
    # 2. Processed TEMP + Weather sheets
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
        # Check original HR data
        # --------------------------------------------------------

        if key in hr_files and hr_files[key] is not None:
            print(f"HR data available for {pid} D{day}")

        # --------------------------------------------------------
        # Check assessment Results
        # --------------------------------------------------------
        if key in assessment_results:
            print(f"Assessment available for {pid} D{day}")

    # ============================================================
    # 3. Save workbook
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