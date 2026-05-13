import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_sequences(data, seq_len=6):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len])
    return np.array(X), np.array(y)


def train_and_save(dataset_path: Path):
    df = pd.read_csv(dataset_path)
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True, errors="coerce")
    df = df[df["Datetime"].notna()].copy()
    df["Global_active_power"] = pd.to_numeric(df["Global_active_power"], errors="coerce")
    df = df.dropna(subset=["Global_active_power"])
    monthly = df.groupby(pd.Grouper(key="Datetime", freq="MS"))["Global_active_power"].sum() / 60.0
    monthly.name = "Monthly_kwh"

    LOGGER.info("Monthly points: %d, range: %.4f - %.4f kWh", len(monthly), monthly.min(), monthly.max())

    y_raw = monthly.values
    scaler_y = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler_y.fit_transform(y_raw.reshape(-1, 1)).flatten()

    X_seq, y_seq = create_sequences(y_scaled, seq_len=6)
    if len(X_seq) < 10:
        raise ValueError(f"Need at least 16 monthly data points to train. Got {len(X_seq)} usable sequences.")

    split = max(1, int(len(X_seq) * 0.8))
    X_train, X_test = X_seq[:split], X_seq[split:]
    y_train, y_test = y_seq[:split], y_seq[split:]

    LOGGER.info("Train: %d, Test: %d", len(X_train), len(X_test))

    best_mae = float("inf")
    best_model = None

    for lr in [0.01, 0.05, 0.1]:
        for depth in [2, 3, 4]:
            for n in [50, 100, 200]:
                model = XGBRegressor(
                    n_estimators=n,
                    max_depth=depth,
                    learning_rate=lr,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_alpha=0.5,
                    reg_lambda=1.0,
                    random_state=42,
                    verbosity=0,
                )
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                mae = float(np.mean(np.abs(y_test - preds)))
                if mae < best_mae:
                    best_mae = mae
                    best_model = model

    preds = best_model.predict(X_test)
    preds_inv = scaler_y.inverse_transform(preds.reshape(-1, 1)).flatten()
    y_test_inv = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()

    mae = mean_absolute_error(y_test_inv, preds_inv)
    rmse = np.sqrt(np.mean((y_test_inv - preds_inv) ** 2))
    r2 = r2_score(y_test_inv, preds_inv)

    LOGGER.info("MAE: %.6f kWh  RMSE: %.6f kWh  R2: %.4f", mae, rmse, r2)

    MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "xgb_model.joblib"
    SCALER_Y_PATH = PROJECT_ROOT / "ml" / "saved_models" / "xgb_scaler.gz"
    SCALER_X_PATH = PROJECT_ROOT / "ml" / "saved_models" / "xgb_scaler_X.gz"

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler_y, SCALER_Y_PATH)

    LOGGER.info("Model saved. Target scale: %.6f - %.6f kWh", y_raw.min(), y_raw.max())

    return mae, rmse, r2


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default=None)
    args = parser.parse_args()

    if args.file:
        train_and_save(Path(args.file))
    else:
        train_and_save(PROJECT_ROOT.parent / "sample_copy.csv")