import logging
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

LOGGER = logging.getLogger(__name__)


def evaluate(model_path: Path, processed_path: Path, metrics_path: Path):
    df = pd.read_csv(processed_path, parse_dates=["MonthStart"])
    df = df.sort_values("MonthStart")
    X = df.drop(columns=["MonthStart", "TargetMonthStart", "Next_month_kwh"])
    y = df["Next_month_kwh"]

    split_idx = max(int(len(df) * 0.8), 1)
    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]
    if X_test.empty:
        LOGGER.warning("Not enough data to create a test set. Skipping evaluation.")
        return

    model = joblib.load(model_path)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    mse = mean_squared_error(y_test, preds)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, preds)

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as f:
        f.write(f"MAE: {mae:.6f}\n")
        f.write(f"MSE: {mse:.6f}\n")
        f.write(f"RMSE: {rmse:.6f}\n")
        f.write(f"R2: {r2:.6f}\n")

    LOGGER.info("Saved metrics to %s", metrics_path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parents[1]
    model_path = root / "ml" / "saved_models" / "random_forest.joblib"
    processed_path = root / "output" / "processed_monthly.csv"
    metrics_path = root / "output" / "metrics.txt"

    evaluate(model_path, processed_path, metrics_path)


if __name__ == "__main__":
    main()
