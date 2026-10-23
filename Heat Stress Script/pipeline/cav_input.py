
import pandas as pd
from tkinter.filedialog import askopenfilename


CAV_TABLE = {
    1: ("Short sleeves and pants of woven material", -1),
    2: ("Work clothes (long sleeve shirt and pants)", 0),
    3: ("Cloth (woven material) coveralls", 0),
    4: (
        "SMS (Spunbond - Meltblown - Spunbond) "
        "polypropylene coveralls",
        0.5
    ),
    5: ("Polyolefin coveralls", 1),
    6: ("Double-layer woven clothing", 3),
    7: ("Limited-use vapour-barrier coveralls", 11),
    8: (
        "Adding a hood (full head and neck covering; not face)",
        1
    ),
}


def load_cav_intervals(file_path=None):

    if not file_path:
        file_path = askopenfilename(
            title="Select Live Notation Excel File",
            filetypes=[
                ("Excel Files", "*.xlsx *.xlsm"),
                ("All Files", "*.*")
            ]
        )

    if not file_path:
        print("CAV file selection cancelled.")
        return None

    wbgt_df = pd.read_excel(
        file_path,
        sheet_name="WBGT"
    )

    # Normalize column names
    wbgt_df.columns = (
        wbgt_df.columns.astype(str).str.strip()
    )

    required_columns = [
        "Start Time",
        "End Time",
        "Duration",
        "Clothing Type"
    ]

    missing = [
        col for col in required_columns
        if col not in wbgt_df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in WBGT sheet: {missing}"
        )

    # Map exact clothing names to CAV values
    clothing_to_cav = {
        name.strip(): cav
        for name, cav in CAV_TABLE.values()
    }

    intervals = []

    for _, row in wbgt_df.iterrows():

        start = pd.to_datetime(
            row["Start Time"], errors="coerce"
        )
        end = pd.to_datetime(
            row["End Time"], errors="coerce"
        )

        if pd.isna(start) or pd.isna(end):
            raise ValueError(
                "Invalid Start Time or End Time "
                "in the WBGT sheet."
            )

        if start >= end:
            raise ValueError(
                f"Invalid interval: {start} - {end}"
            )

        clothing_text = str(
            row["Clothing Type"]
        ).strip()

        if not clothing_text or clothing_text.lower() == "nan":
            raise ValueError(
                f"Clothing Type is empty for {start} - {end}"
            )

        # Split multiple clothing items separated by semicolons
        clothing_items = [
            item.strip()
            for item in clothing_text.split(";")
            if item.strip()
        ]

        unknown_items = [
            item for item in clothing_items
            if item not in clothing_to_cav
        ]

        if unknown_items:
            raise ValueError(
                "Unknown Clothing Type(s): "
                + ", ".join(unknown_items)
            )

        # Sum individual CAV values.
        # Confirm that additive CAV is the intended rule
        # for all multi-item combinations before final use.
        cav = sum(
            clothing_to_cav[item]
            for item in clothing_items
        )

        intervals.append({
            "Start Time": start,
            "End Time": end,
            "Duration": row["Duration"],
            "Clothing Type": "; ".join(clothing_items),
            "CAV": cav
        })

    intervals.sort(
        key=lambda item: item["Start Time"]
    )

    # Reject overlapping intervals; adjacent boundaries are allowed
    for i in range(1, len(intervals)):
        previous = intervals[i - 1]
        current = intervals[i]

        if current["Start Time"] < previous["End Time"]:
            raise ValueError(
                "Overlapping clothing intervals detected:\n"
                f"{previous['Start Time']} - "
                f"{previous['End Time']}\n"
                f"{current['Start Time']} - "
                f"{current['End Time']}"
            )

    print("\nLoaded Clothing Intervals:")

    for interval in intervals:
        print(
            interval["Start Time"],
            "to",
            interval["End Time"],
            "|",
            interval["Clothing Type"],
            "| CAV:",
            interval["CAV"]
        )

    return intervals
