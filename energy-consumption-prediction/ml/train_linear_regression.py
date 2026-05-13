import logging
from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

LOGGER = logging.getLogger(__name__)


def train_linear_regression(processed_path: Path, model_path: Path):
    df = pd.read_csv(processed_path, parse_dates=["MonthStart"])
    df = df.sort_values("MonthStart")

    X = df.drop(columns=["MonthStart", "TargetMonthStart", "Next_month_kwh"])
    y = df["Next_month_kwh"]

    split_idx = max(int(len(df) * 0.8), 1)
    X_train = X.iloc[:split_idx]
    y_train = y.iloc[:split_idx]

    model = LinearRegression()
    model.fit(X_train, y_train)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    LOGGER.info("Saved Linear Regression model to %s", model_path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parents[1]
    processed_path = root / "output" / "processed_monthly.csv"
    model_path = root / "ml" / "saved_models" / "linear_regression.joblib"

    train_linear_regression(processed_path, model_path)


if __name__ == "__main__":
    main()
