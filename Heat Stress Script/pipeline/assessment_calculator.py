import pandas as pd
import math


def classify_work_intensity(mr):

    if mr < 115:
        return "Rest"

    elif mr < 235:
        return "Light"

    elif mr < 360:
        return "Moderate"

    elif mr < 470:
        return "Heavy"

    else:
        return "Very Heavy"


def calculate_assessment(hr_df, sex, weight, age):

    # ============================================================
    # Copy HR data
    # ============================================================

    df = hr_df.copy()


    # ============================================================
    # Normalize column names
    # ============================================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    print("\n[ASSESSMENT] HR columns:")
    print(df.columns.tolist())


    # ============================================================
    # Find BPM column
    # ============================================================

    bpm_col = None

    for col in df.columns:

        if str(col).strip().upper() == "BPM":

            bpm_col = col

            break


    if bpm_col is None:

        raise ValueError(
            "BPM column not found. "
            f"Available columns: {df.columns.tolist()}"
        )


    # ============================================================
    # Convert BPM to numeric
    # ============================================================

    bpm = pd.to_numeric(
        df[bpm_col],
        errors="coerce"
    ).dropna()
    
    # Exclude invalid zero BPM values
    bpm = bpm[bpm > 0]


    if bpm.empty:

        raise ValueError(
            "No BPM data found."
        )


    # ============================================================
    # HR calculations
    # ============================================================

    hr_max = bpm.max()

    hr_rest = bpm.min()

    hrr = hr_max - hr_rest


    # ============================================================
    # Energy Expenditure
    # ============================================================

    gender = 1 if sex.lower() == "male" else 0
 
    ee = (
        gender * (
            -55.0969
            + 0.6309 * bpm
            + 0.1988 * weight
            + 0.2017 * age
        )
        +
        (1 - gender) * (
            -20.4022
            + 0.4472 * bpm
            - 0.1263 * weight
            + 0.074 * age
        )
    )


    # ============================================================
    # Metabolic Rate
    # ============================================================

    mr = ee * 16.67

    average_mr = mr.mean()


    # ============================================================
    # Action Limit / TLV
    # ============================================================

    action_limit = (
        60.0
        - 14.1 * math.log10(average_mr)
    )


    tlv = (
        56.7
        - 11.5 * math.log10(average_mr)
    )


    # ============================================================
    # Work Intensity
    # ============================================================

    work_intensity = classify_work_intensity(
        average_mr
    )


    # ============================================================
    # Return assessment results
    # ============================================================

    return {

        "Sex": sex,

        "Weight (kg)": round(
            weight,
            2
        ),

        "Age": round(
            age,
            2
        ),

        "HR Max (BPM)": round(
            hr_max,
            2
        ),

        "HR Rest (BPM)": round(
            hr_rest,
            2
        ),

        "HRR": round(
            hrr,
            2
        ),

        "Energy Expenditure (kcal/min)": round(
            ee,
            2
        ),

        "Metabolic Rate (W)": round(
            average_mr,
            2
        ),

        "Action Limit (°C)": round(
            action_limit,
            2
        ),

        "TLV (°C)": round(
            tlv,
            2
        ),

        "Work Intensity": work_intensity
    }