import logging
from typing import Tuple
import pandas as pd

LOGGER = logging.getLogger(__name__)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    LOGGER.info("Adding time-based features")
    df = df.copy()
    df["Hour"] = df["Datetime"].dt.hour
    df["Day"] = df["Datetime"].dt.day
    df["Month"] = df["Datetime"].dt.month
    df["Weekday"] = df["Datetime"].dt.dayofweek
    df["Year"] = df["Datetime"].dt.year
    return df


def build_monthly_series(df: pd.DataFrame) -> pd.Series:
    LOGGER.info("Aggregating to monthly energy consumption")
    df = df.copy()
    df = df.sort_values("Datetime")

    # Convert minute-level power (kW) to energy (kWh) per minute.
    df["Energy_kwh"] = df["Global_active_power"] / 60.0
    monthly = (
        df.set_index("Datetime")["Energy_kwh"]
        .resample("MS")
        .sum()
        .rename("Monthly_kwh")
    )
    return monthly


def build_monthly_features(monthly: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
    LOGGER.info("Building monthly lag features")
    monthly = monthly.sort_index()

    features = pd.DataFrame({"Monthly_kwh": monthly})
    features["Month"] = features.index.month
    features["Year"] = features.index.year
    features["Lag_1"] = features["Monthly_kwh"].shift(1)
    features["Lag_2"] = features["Monthly_kwh"].shift(2)
    features["Lag_3"] = features["Monthly_kwh"].shift(3)
    features["Rolling_3"] = features["Monthly_kwh"].rolling(3).mean()
    features["Rolling_6"] = features["Monthly_kwh"].rolling(6).mean()

    target = features["Monthly_kwh"].shift(-1).rename("Next_month_kwh")
    features = features.drop(columns=["Monthly_kwh"])

    combined = pd.concat([features, target], axis=1).dropna()
    y = combined["Next_month_kwh"]
    X = combined.drop(columns=["Next_month_kwh"])
    return X, y


def build_latest_feature_row(monthly: pd.Series) -> pd.DataFrame:
    monthly = monthly.sort_index()
    if len(monthly) < 6:
        raise ValueError("At least 6 months of data are required to predict next month.")

    recent = monthly.iloc[-6:]
    last_month = recent.index[-1]
    row = pd.DataFrame(
        {
            "Month": [last_month.month],
            "Year": [last_month.year],
            "Lag_1": [recent.iloc[-1]],
            "Lag_2": [recent.iloc[-2]],
            "Lag_3": [recent.iloc[-3]],
            "Rolling_3": [recent.iloc[-3:].mean()],
            "Rolling_6": [recent.mean()],
        }
    )
    return row


def select_feature_columns():
    return [
        "Month",
        "Year",
        "Lag_1",
        "Lag_2",
        "Lag_3",
        "Rolling_3",
        "Rolling_6",
    ]
