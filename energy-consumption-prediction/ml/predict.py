import logging
from pathlib import Path
import joblib
import pandas as pd

from preprocessing.clean_data import load_raw_data, clean_data
from preprocessing.feature_engineering import build_monthly_series, build_latest_feature_row, select_feature_columns

LOGGER = logging.getLogger(__name__)


def predict_next_month(model_path: Path, scaler_path: Path, dataset_path: Path) -> pd.DataFrame:
    raw = load_raw_data(dataset_path)
    df = clean_data(raw)
    monthly = build_monthly_series(df)

    latest_row = build_latest_feature_row(monthly)
    feature_cols = select_feature_columns()

    scaler = joblib.load(scaler_path)
    X_scaled = scaler.transform(latest_row[feature_cols])

    model = joblib.load(model_path)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    prediction = model.predict(X_scaled)[0]

    next_month = (monthly.index[-1] + pd.offsets.MonthBegin(1)).date()
    out_df = pd.DataFrame(
        {
            "MonthStart": [next_month],
            "Predicted_next_month_kwh": [prediction],
        }
    )
    return out_df


def generate_predictions(model_path: Path, scaler_path: Path, dataset_path: Path, output_path: Path):
    out_df = predict_next_month(model_path, scaler_path, dataset_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    LOGGER.info("Saved next-month prediction to %s", output_path)


def main():
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    model_path = root / "ml" / "saved_models" / "random_forest.joblib"
    scaler_path = root / "ml" / "saved_models" / "scaler.joblib"
    dataset_path = root / "dataset" / "household_power_consumption.txt"
    output_path = root / "output" / "next_month_prediction.csv"

    generate_predictions(model_path, scaler_path, dataset_path, output_path)


if __name__ == "__main__":
    main()
