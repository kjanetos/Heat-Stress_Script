from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.utils import get_column_letter


def get_header_map(ws):

    headers = {}

    for col in range(1, ws.max_column + 1):

        value = ws.cell(row=1, column=col).value

        if value is not None:
            headers[str(value).strip()] = col

    return headers


def ensure_column(ws, header):

    headers = get_header_map(ws)

    if header in headers:
        return headers[header]

    col = ws.max_column + 1

    ws.cell(row=1, column=col).value = header

    return col


def write_assessment_results(
    workbook_file,
    assessment_results,
    output_file
):

    wb = load_workbook(workbook_file)

    summary = wb["Summary"]

    green = PatternFill(fill_type="solid", fgColor="92D050")
    yellow = PatternFill(fill_type="solid", fgColor="FFFF00")
    orange = PatternFill(fill_type="solid", fgColor="FFC000")
    dark_orange = PatternFill(fill_type="solid", fgColor="ED7D31")
    red = PatternFill(fill_type="solid", fgColor="FF3101")

    low_fill = PatternFill(fill_type="solid", fgColor="C6EFCE")
    moderate_fill = PatternFill(fill_type="solid", fgColor="FFF2CC")
    high_fill = PatternFill(fill_type="solid", fgColor="FCE4D6")

    pid_col = ensure_column(summary, "PID")
    day_col = ensure_column(summary, "Day")

    wbgteff_col = ensure_column(summary, "WBGTeff Mean (°C)")

    sex_col = ensure_column(summary, "Sex")
    weight_col = ensure_column(summary, "Weight (kg)")

    hrmax_col = ensure_column(summary, "HR Max (BPM)")
    hrrest_col = ensure_column(summary, "HR Rest (BPM)")
    hrr_col = ensure_column(summary, "HRR")
    ee_col = ensure_column(summary, "Energy Expenditure (kcal/min)")
    mr_col = ensure_column(summary, "Metabolic Rate (W)")
    al_col = ensure_column(summary, "Action Limit (°C)")
    tlv_col = ensure_column(summary, "TLV (°C)")
    work_col = ensure_column(summary, "Work Intensity")
    recommendation_col = ensure_column(summary, "Work/Rest Recommendation")
    risk_col = ensure_column(summary, "Heat Stress Risk")
    status_col = ensure_column(summary, "Status")

    # =====================================================
    # Per-row assessment results
    # =====================================================
    for row in range(2, summary.max_row + 1):

        pid_value = summary.cell(row=row, column=pid_col).value
        day_value = summary.cell(row=row, column=day_col).value

        # Skip blank/incomplete rows instead of raising on None
        if pid_value is None or day_value is None:
            continue

        pid = str(pid_value).strip()

        try:
            day = int(day_value)
        except (TypeError, ValueError):
            summary.cell(row=row, column=status_col).value = "Invalid Day"
            continue

        key = (pid, day)

        if key not in assessment_results:

            summary.cell(
                row=row,
                column=status_col
            ).value = "No HR File"

            continue

        result = assessment_results[key]

        summary.cell(row=row, column=sex_col).value = result["Sex"]
        summary.cell(row=row, column=weight_col).value = result["Weight (kg)"]
        summary.cell(row=row, column=hrmax_col).value = result["HR Max (BPM)"]
        summary.cell(row=row, column=hrrest_col).value = result["HR Rest (BPM)"]
        summary.cell(row=row, column=hrr_col).value = result["HRR"]
        summary.cell(row=row, column=ee_col).value = result["Energy Expenditure (kcal/min)"]
        summary.cell(row=row, column=mr_col).value = result["Metabolic Rate (W)"]
        summary.cell(row=row, column=al_col).value = result["Action Limit (°C)"]
        summary.cell(row=row, column=tlv_col).value = result["TLV (°C)"]

        # Work Intensity
        cell = summary.cell(row=row, column=work_col)
        cell.value = result["Work Intensity"]

        if result["Work Intensity"] == "Rest":
            cell.fill = green
        elif result["Work Intensity"] == "Light":
            cell.fill = yellow
        elif result["Work Intensity"] == "Moderate":
            cell.fill = orange
        elif result["Work Intensity"] == "Heavy":
            cell.fill = dark_orange
        elif result["Work Intensity"] == "Very Heavy":
            cell.fill = red

        wbgteff = summary.cell(row=row, column=wbgteff_col).value

        al = result["Action Limit (°C)"]
        tlv = result["TLV (°C)"]

        risk_cell = summary.cell(row=row, column=risk_col)

        if wbgteff is None:
            # No weather value to compare against -- can't classify risk
            risk = None
            risk_cell.value = "N/A"
        else:
            if wbgteff < al:
                risk = "Low Risk"
            elif wbgteff < tlv:
                risk = "Moderate Risk"
            else:
                risk = "High Risk"

            risk_cell.value = risk

            if risk == "Low Risk":
                risk_cell.fill = low_fill
            elif risk == "Moderate Risk":
                risk_cell.fill = moderate_fill
            else:
                risk_cell.fill = high_fill

        # -----------------------------
        # Work / Rest Recommendation
        # -----------------------------
        work = result["Work Intensity"]

        if wbgteff is None:
            recommendation = "N/A"

        elif work == "Rest":
            recommendation = "100%"

        elif work == "Light":

            if wbgteff < 28.0:
                recommendation = "100%"
            elif wbgteff < 28.5:
                recommendation = "75-100%"
            elif wbgteff < 29.5:
                recommendation = "50-75%"
            elif wbgteff < 30.0:
                recommendation = "25-50%"
            else:
                recommendation = "0-25%"

        elif work == "Moderate":

            if wbgteff < 25.0:
                recommendation = "100%"
            elif wbgteff < 26.0:
                recommendation = "75-100%"
            elif wbgteff < 27.0:
                recommendation = "50-75%"
            elif wbgteff < 29.0:
                recommendation = "25-50%"
            else:
                recommendation = "0-25%"

        elif work == "Heavy":

            if wbgteff < 24.0:
                recommendation = "100%"
            elif wbgteff < 25.5:
                recommendation = "75-100%"
            elif wbgteff < 28.0:
                recommendation = "50-75%"
            else:
                recommendation = "25-50%"

        elif work == "Very Heavy":

            if wbgteff < 24.5:
                recommendation = "75-100%"
            elif wbgteff < 27.5:
                recommendation = "25-50%"
            else:
                recommendation = "0-25%"

        else:
            recommendation = "N/A"

        summary.cell(row=row, column=recommendation_col).value = recommendation

        # Status
        summary.cell(row=row, column=status_col).value = "Success"

    # =====================================================
    # Move Status column to the end (once, after all rows processed)
    # =====================================================
    headers = get_header_map(summary)
    status_col = headers["Status"]
    last_col = summary.max_column

    if status_col != last_col:

        status_values = []

        for r in range(1, summary.max_row + 1):
            status_values.append(
                summary.cell(row=r, column=status_col).value
            )

        summary.delete_cols(status_col)

        new_col = summary.max_column + 1

        for r, value in enumerate(status_values, start=1):
            summary.cell(row=r, column=new_col).value = value

    # =====================================================
    # Reference Sheet (built once, not per row)
    # =====================================================
    reference = wb.create_sheet("Reference")

    header_fill = PatternFill(fill_type="solid", fgColor="D9EAD3")
    bold = Font(bold=True)

    thin = Side(style="thin")

    border = Border(
        left=thin,
        right=thin,
        top=thin,
        bottom=thin
    )

    # -----------------------------------------------------
    # Work Intensity Classification
    # -----------------------------------------------------
    reference["A1"] = "Work Intensity Classification"
    reference["A1"].font = Font(bold=True, size=14)

    reference["A3"] = "Category"
    reference["B3"] = "Metabolic Rate (W)"

    reference["A3"].font = bold
    reference["B3"].font = bold

    reference["A3"].fill = header_fill
    reference["B3"].fill = header_fill

    intensity_rows = [
        ("Rest", "<115", green),
        ("Light", "115–235", yellow),
        ("Moderate", "235–360", orange),
        ("Heavy", "360–470", dark_orange),
        ("Very Heavy", ">470", red),
    ]

    for i, (category, value, fill) in enumerate(intensity_rows, start=4):
        reference.cell(row=i, column=1).value = category
        reference.cell(row=i, column=2).value = value
        reference.cell(row=i, column=1).fill = fill
        reference.cell(row=i, column=2).fill = fill

    reference.column_dimensions["A"].width = 22
    reference.column_dimensions["B"].width = 20

    # -----------------------------------------------------
    # Work-Rest Allocation (WBGTeff thresholds table)
    # -----------------------------------------------------
    reference.merge_cells("D1:H1")

    reference["D1"] = "Work-Rest Allocations Based on Unacclimatized Workers"
    reference["D1"].font = Font(bold=True, size=14)
    reference["D1"].alignment = Alignment(horizontal="center")

    headers_row = ["Allocation", "Light", "Moderate", "Heavy", "Very Heavy"]

    for col, text in enumerate(headers_row, start=4):
        cell = reference.cell(row=3, column=col)
        cell.value = text
        cell.font = bold
        cell.fill = header_fill
        cell.border = border

    work_rows = [
        ("75-100%", 28.0, 25.0, None, None),
        ("50-75%", 28.5, 26.0, 24.0, None),
        ("25-50%", 29.5, 27.0, 25.5, 24.5),
        ("0-25%", 30.0, 29.0, 28.0, 27.5),
    ]

    for r, row_data in enumerate(work_rows, start=4):
        for c, value in enumerate(row_data, start=4):
            cell = reference.cell(row=r, column=c)
            cell.value = value
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")

    reference.column_dimensions["D"].width = 24
    reference.column_dimensions["E"].width = 12
    reference.column_dimensions["F"].width = 12
    reference.column_dimensions["G"].width = 12
    reference.column_dimensions["H"].width = 12

    # -----------------------------------------------------
    # Heat Stress Risk Classification
    # -----------------------------------------------------
    reference["A11"] = "Heat Stress Risk Classification"
    reference["A11"].font = Font(bold=True, size=14)

    reference["A13"] = "Risk"
    reference["B13"] = "Criteria"

    reference["A13"].font = bold
    reference["B13"].font = bold

    reference["A13"].fill = header_fill
    reference["B13"].fill = header_fill

    risk_rows = [
        ("Low Risk", "WBGTeff < AL", low_fill),
        ("Moderate Risk", "AL ≤ WBGTeff < TLV", moderate_fill),
        ("High Risk", "WBGTeff ≥ TLV", high_fill),
    ]

    for i, (risk_name, criteria, fill) in enumerate(risk_rows, start=14):
        reference.cell(row=i, column=1).value = risk_name
        reference.cell(row=i, column=2).value = criteria
        reference.cell(row=i, column=1).fill = fill
        reference.cell(row=i, column=2).fill = fill

    # =====================================================
    # Save once, at the very end
    # =====================================================
    wb.save(output_file)