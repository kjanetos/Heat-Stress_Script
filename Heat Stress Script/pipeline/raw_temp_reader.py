import os
import re
import pandas as pd

TIME_COL_PATTERN = re.compile(r"time\s*\[utc-ofs=", re.IGNORECASE)


def _convert_excel_serial(series):
    return pd.to_datetime(series, unit="A", origin="1899-12-30")


def _find_header_row_csv(file_path, max_scan=50):
    with open(file_path, "r", encoding="utf-8-sig") as f:
        for i, line in enumerate(f):
            if i >= max_scan:
                break
            if TIME_COL_PATTERN.search(line):
                return i

    raise ValueError(
        f"Could not find a header row containing a 'time [UTC-OFS=...]' "
        f"column in the first {max_scan} lines of {file_path}."
    )


def _find_header_row_excel(file_path, max_scan=80):
    """Same idea as _find_header_row_csv, but for Excel files."""
    preview = pd.read_excel(file_path, header=None, nrows=max_scan)

    for i, row in preview.iterrows():
        cells = row.astype(str).str.strip()
        if cells.str.contains(TIME_COL_PATTERN).any():
            return i

    raise ValueError(
        f"Could not find a header row containing a 'time [UTC-OFS=...]' "
        f"column in the first {max_scan} rows of {file_path}."
    )


def _find_time_col(columns):
    for col in columns:
        if TIME_COL_PATTERN.search(str(col)):
            return col

    raise KeyError(
        f"No 'time [UTC-OFS=...]' column found.\nAvailable columns: {list(columns)}"
    )


def read_raw_temp(file_path, time_col=None):

    ext = os.path.splitext(file_path)[1].lower()

    if time_col is not None:
        time_col = time_col.strip()

    if ext == ".csv":
        header_row = _find_header_row_csv(file_path)
        df = pd.read_csv(
            file_path,
            sep=",",
            skiprows=header_row,
            encoding="utf-8-sig",
        )
    else:
        header_row = _find_header_row_excel(file_path)
        df = pd.read_excel(file_path, header=header_row)

    df.columns = df.columns.str.strip()

    if time_col is None:
        time_col = _find_time_col(df.columns)
    elif time_col not in df.columns:
        raise KeyError(
            f"Column '{time_col}' not found in file after locating header "
            f"row {header_row}.\nAvailable columns: {df.columns.tolist()}"
        )

    print(f"Using time column: {time_col}")

    if pd.api.types.is_numeric_dtype(df[time_col]):

        df[time_col] = _convert_excel_serial(
            df[time_col]
        )

    else:

        df[time_col] = pd.to_datetime(
            df[time_col],
            errors="coerce"
        )


    print(
        f"Using time column: {time_col}"
    )

    print(
        "First TEMP time:",
        df[time_col].iloc[0]
    )

    print(df.columns.tolist())
    print(df.head())

    return df

def _get_utc_offset(time_col):
    """
    Get UTC offset from column name.

    Examples:
        time [UTC-OFS=-0400] -> -04:00
        time [UTC-OFS=-0500] -> -05:00
    """

    match = re.search(
        r"UTC-OFS=([+-])(\d{2})(\d{2})",
        str(time_col),
        re.IGNORECASE
    )

    if not match:
        return None

    sign = -1 if match.group(1) == "-" else 1

    hours = int(match.group(2))
    minutes = int(match.group(3))

    return sign * (hours * 60 + minutes)