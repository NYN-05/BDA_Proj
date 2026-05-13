import logging
from pathlib import Path
import pandas as pd

LOGGER = logging.getLogger(__name__)

RAW_COLUMNS = [
    "Date",
    "Time",
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]

NUMERIC_COLUMNS = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]


def load_raw_data(file_path: Path) -> pd.DataFrame:
    LOGGER.info("Loading raw data from %s", file_path)
    df = pd.read_csv(
        file_path,
        sep=";",
        usecols=RAW_COLUMNS,
        low_memory=False,
    )
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    LOGGER.info("Cleaning raw data")
    df = df.copy()

    missing = [col for col in RAW_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df.replace("?", pd.NA, inplace=True)
    df.dropna(subset=RAW_COLUMNS, inplace=True)

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=NUMERIC_COLUMNS, inplace=True)

    # Remove invalid rows: negative or zero voltage/intensity values are not valid.
    df = df[(df["Voltage"] > 0) & (df["Global_intensity"] >= 0)]
    df = df[(df["Global_active_power"] >= 0) & (df["Global_reactive_power"] >= 0)]
    df = df[(df["Sub_metering_1"] >= 0) & (df["Sub_metering_2"] >= 0) & (df["Sub_metering_3"] >= 0)]

    df["Datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        dayfirst=True,
        errors="coerce",
    )
    df.dropna(subset=["Datetime"], inplace=True)

    df.drop(columns=["Date", "Time"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    LOGGER.info("Cleaned rows: %d", len(df))
    return df
