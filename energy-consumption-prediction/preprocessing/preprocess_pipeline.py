import logging
from pathlib import Path
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from preprocessing.clean_data import load_raw_data, clean_data
from preprocessing.feature_engineering import (
    build_monthly_series,
    build_monthly_features,
    select_feature_columns,
)

LOGGER = logging.getLogger(__name__)


def run_preprocessing(dataset_path: Path, output_path: Path, scaler_path: Path) -> pd.DataFrame:
    df = load_raw_data(dataset_path)
    df = clean_data(df)

    monthly = build_monthly_series(df)
    if len(monthly) < 12:
        raise ValueError("At least 12 months of data are required for training.")
    X, y = build_monthly_features(monthly)
    feature_cols = select_feature_columns()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X[feature_cols])
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols, index=X.index)

    processed = X_scaled.reset_index().rename(columns={"Datetime": "MonthStart"})
    processed["TargetMonthStart"] = processed["MonthStart"] + pd.offsets.MonthBegin(1)
    processed["Next_month_kwh"] = y.reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_path, index=False)

    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, scaler_path)

    LOGGER.info("Saved processed data to %s", output_path)
    return processed


def main():
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    dataset_path = root / "dataset" / "household_power_consumption.txt"
    output_path = root / "output" / "processed_monthly.csv"
    scaler_path = root / "ml" / "saved_models" / "scaler.joblib"

    run_preprocessing(dataset_path, output_path, scaler_path)


if __name__ == "__main__":
    main()
