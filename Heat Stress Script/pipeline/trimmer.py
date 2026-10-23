
import pandas as pd
import re


def trim_to_work_window(
    df,
    time_col,
    start_time,
    end_time
):
    df = df.copy()

    # -------------------------------------------------------
    # 1. Validate time column
    # -------------------------------------------------------

    if time_col not in df.columns:
        raise ValueError(
            f"Time column not found: {time_col}"
        )

    # -------------------------------------------------------
    # 2. Normalize TEMP timestamps
    #    Remove UTC offset without shifting clock time,
    #    preserving the existing local wall-clock time.
    # -------------------------------------------------------

    def normalize_time(value):

        if pd.isna(value):
            return pd.NaT

        value = str(value).strip()

        value = re.sub(
            r'([+-]\d{2}:?\d{2})$',
            '',
            value
        )

        return pd.to_datetime(
            value,
            errors="coerce"
        )

    df[time_col] = df[time_col].apply(
        normalize_time
    )

    # -------------------------------------------------------
    # 3. Validate Master Data times
    # -------------------------------------------------------

    start_time = pd.to_datetime(
        start_time,
        errors="coerce"
    )

    end_time = pd.to_datetime(
        end_time,
        errors="coerce"
    )

    if pd.isna(start_time):
        raise ValueError(
            "Invalid start time in Master Data."
        )

    if pd.isna(end_time):
        raise ValueError(
            "Invalid end time in Master Data."
        )

    # Remove timezone metadata from Master Data times
    # while preserving the displayed clock time.
    if start_time.tzinfo is not None:
        start_time = start_time.tz_localize(None)

    if end_time.tzinfo is not None:
        end_time = end_time.tz_localize(None)

    if start_time > end_time:
        raise ValueError(
            f"Start time ({start_time}) is after "
            f"end time ({end_time})."
        )

    # -------------------------------------------------------
    # 4. Remove invalid timestamps
    # -------------------------------------------------------

    before_rows = len(df)

    df = df.dropna(
        subset=[time_col]
    ).copy()

    invalid_rows = before_rows - len(df)

    # -------------------------------------------------------
    # 5. Filter work window
    #    Include timestamps exactly at end_time.
    # -------------------------------------------------------

    df = df[
        (df[time_col] >= start_time)
        &
        (df[time_col] <= end_time)
    ].copy()

    # -------------------------------------------------------
    # 6. Report results
    # -------------------------------------------------------

    print("\n===== Work Window =====")
    print("Start:", start_time)
    print("End  :", end_time)
    print("Invalid timestamps removed:", invalid_rows)
    print("Rows remaining:", len(df))

    if not df.empty:
        print("First time:", df[time_col].min())
        print("Last time :", df[time_col].max())
    else:
        print(
            "WARNING: No TEMP records found "
            "within the work window."
        )

    return df
