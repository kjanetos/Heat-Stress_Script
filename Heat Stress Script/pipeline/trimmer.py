import pandas as pd
import re


def trim_to_work_window(
    df,
    time_col,
    start_time,
    end_time
):

    # Include the entire ending second
    end_time = pd.to_datetime(end_time) + pd.Timedelta(seconds=1)

    return df[
        (df[time_col] >= start_time)
        &
        (df[time_col] < end_time)
    ].copy()

    df = df.copy()

    # -------------------------------------------------------
    # TEMP time
    # Ignore UTC-OFS in the timestamp
    # -------------------------------------------------------

    def remove_timezone(value):

        if pd.isna(value):
            return pd.NaT

        value = str(value)

        # Remove timezone information such as:
        # -04:00
        # -05:00
        # +00:00
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
        remove_timezone
    )

    # -------------------------------------------------------
    # Master Data start / end time
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
            f"Invalid start time: {start_time}"
        )

    if pd.isna(end_time):
        raise ValueError(
            f"Invalid end time: {end_time}"
        )

    # Remove timezone from Master Data too
    if start_time.tzinfo is not None:
        start_time = start_time.tz_localize(None)

    if end_time.tzinfo is not None:
        end_time = end_time.tz_localize(None)

    # -------------------------------------------------------
    # Print for verification
    # -------------------------------------------------------

    print("\n===== Work Window =====")
    print("Start:", start_time)
    print("End  :", end_time)

    # -------------------------------------------------------
    # Keep only work-window data
    # -------------------------------------------------------

    df = df.dropna(
        subset=[time_col]
    )

    df = df[
        (df[time_col] >= start_time)
        &
        (df[time_col] <= end_time)
    ].copy()

    print("\n===== TEMP After Trimming =====")
    print("Rows remaining:", len(df))

    if not df.empty:
        print("First time:", df[time_col].min())
        print("Last time :", df[time_col].max())

    return df