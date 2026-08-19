import pandas as pd


def find_time_column(df):

    for col in df.columns:

        col_str = str(col).strip().lower()

        if col_str.startswith("time [utc-ofs="):
            return col

    raise ValueError(
        "TEMP time column was not found."
    )


def build_summary(processed):

    rows = []

    print("\n==============================")
    print("Building Summary")
    print("==============================")

    print("Number of processed items:", len(processed))

    for (pid, day), df in processed.items():

        print(
            f"\nProcessing PID={pid}, Day={day}"
        )

        if df.empty:
            print("WARNING: DataFrame is empty. Skipping.")
            continue

        # -----------------------------------------
        # Find TIME column automatically
        # -----------------------------------------

        time_col = find_time_column(df)

        print("Time column:", time_col)

        # -----------------------------------------
        # Make sure time is datetime
        # -----------------------------------------

        df[time_col] = pd.to_datetime(
            df[time_col],
            errors="coerce"
        )

        df = df.dropna(
            subset=[time_col]
        ).copy()

        if df.empty:
            print(
                "WARNING: No valid time data. Skipping."
            )
            continue

        row = {}

        # -----------------------------------------
        # Basic information
        # -----------------------------------------

        row["Date"] = df.iloc[0][time_col].date()

        row["PID"] = pid
        row["Day"] = day

        start = df.iloc[0][time_col]
        end = df.iloc[-1][time_col]

        row["Start Time"] = start.time()
        row["End Time"] = end.time()

        duration = (
            end - start
        ).total_seconds() / 3600

        row["Duration (hrs)"] = round(
            duration,
            2
        )

        # -----------------------------------------
        # Temperature
        # -----------------------------------------

        row["Temperature Mean (°C)"] = round(
            df["Temperature (°C)"].mean(),
            2
        )

        row["Temperature Min (°C)"] = round(
            df["Temperature (°C)"].min(),
            2
        )

        row["Temperature Max (°C)"] = round(
            df["Temperature (°C)"].max(),
            2
        )

        # -----------------------------------------
        # Humidity
        # -----------------------------------------

        row["Humidity Mean (%)"] = round(
            df["Relative Humidity (%)"].mean(),
            2
        )

        row["Humidity Min (%)"] = round(
            df["Relative Humidity (%)"].min(),
            2
        )

        row["Humidity Max (%)"] = round(
            df["Relative Humidity (%)"].max(),
            2
        )

        # -----------------------------------------
        # Dew Point
        # -----------------------------------------

        row["Dew Point Mean (°C)"] = round(
            df["Dew Point (°C)"].mean(),
            2
        )

        row["Dew Point Min (°C)"] = round(
            df["Dew Point (°C)"].min(),
            2
        )

        row["Dew Point Max (°C)"] = round(
            df["Dew Point (°C)"].max(),
            2
        )

        # -----------------------------------------
        # Apparent Temperature
        # -----------------------------------------

        row["Apparent Temperature Mean (°C)"] = round(
            df["Apparent Temperature (°C)"].mean(),
            2
        )

        row["Apparent Temperature Min (°C)"] = round(
            df["Apparent Temperature (°C)"].min(),
            2
        )

        row["Apparent Temperature Max (°C)"] = round(
            df["Apparent Temperature (°C)"].max(),
            2
        )

        # -----------------------------------------
        # WBGT
        # -----------------------------------------

        row["WBGT Mean (°C)"] = round(
            df["WBGT (°C)"].mean(),
            2
        )

        row["WBGT Min (°C)"] = round(
            df["WBGT (°C)"].min(),
            2
        )

        row["WBGT Max (°C)"] = round(
            df["WBGT (°C)"].max(),
            2
        )

        # -----------------------------------------
        # Effective WBGT
        # -----------------------------------------

        row["WBGTeff Mean (°C)"] = round(
            df["WBGTeff (°C)"].mean(),
            2
        )

        # -----------------------------------------
        # TWA WBGT
        # -----------------------------------------

        row["TWA WBGT (°C)"] = (
            df["TWA WBGT (°C)"].iloc[0]
        )

        # -----------------------------------------
        # HR
        # -----------------------------------------

        row["HR Max (BPM)"] = None
        row["HR Rest (BPM)"] = None
        row["HRR"] = None
        row["Energy Expenditure (kcal/min)"] = None

        # -----------------------------------------
        # Status
        # -----------------------------------------

        row["Status"] = None

        rows.append(row)

    # ---------------------------------------------
    # Create summary
    # ---------------------------------------------

    summary = pd.DataFrame(rows)

    print("\n==============================")
    print("Summary Result")
    print("==============================")

    print("Number of summary rows:", len(summary))
    print("Columns:", summary.columns.tolist())

    print(summary.head())

    if summary.empty:

        raise ValueError(
            "No valid processed data was found. "
            "The problem is likely in S2_main.py "
            "where 'processed' is created."
        )

    # ---------------------------------------------
    # Sort
    # ---------------------------------------------

    summary = summary.sort_values(
        ["PID", "Day"]
    ).reset_index(drop=True)

    return summary