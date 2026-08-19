import pandas as pd


def _convert_excel_serial(series):
    return pd.to_datetime(series, unit="A", origin="1899-12-30")


def _ensure_datetime(series):
    if pd.api.types.is_numeric_dtype(series):
        return _convert_excel_serial(series)
    return pd.to_datetime(series)


def load_master_data(master_file,
                    sheet_name="Important TimeStamps + Notes"):

    df = pd.read_excel(master_file, sheet_name=sheet_name)

    df.columns = df.columns.str.strip()

    df["Participant"] = df["Participant"].astype(str).str.strip()
    df["Day"] = pd.to_numeric(df["Day"], errors="coerce")

    return df

def get_start_end_time(master_df, pid, day):

    row = master_df[
        (master_df["Participant"] == pid)
        &
        (master_df["Day"] == day)
    ]

    if row.empty:
        raise ValueError(f"{pid} Day {day} not found.")

    collection_date = pd.to_datetime(row["Date"]).iloc[0].date()

    start_clock = row["emg_sensor_init_time"].iloc[0]
    end_clock = row["day_end"].iloc[0]

    start_time = pd.Timestamp.combine(
        collection_date,
        start_clock
    )

    end_time = pd.Timestamp.combine(
        collection_date,
        end_clock
    )

    if end_time < start_time:
        end_time += pd.Timedelta(days=1)

    return start_time, end_time

