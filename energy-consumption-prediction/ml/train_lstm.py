import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_absolute_error, r2_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "lstm_model.keras"
SCALER_PATH = PROJECT_ROOT / "ml" / "saved_models" / "lstm_scaler.gz"
PLOTS_DIR = PROJECT_ROOT / "visualization" / "charts"

SEED = 42
np.random.seed(SEED)
import tensorflow as tf
tf.random.set_seed(SEED)


def create_sequences(data, seq_len=6):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len])
    return np.array(X), np.array(y)


def train_lstm(model_path: Path, scaler_path: Path):
    df = pd.read_csv(
        PROJECT_ROOT / "output" / "processed_monthly.csv",
        parse_dates=["MonthStart"],
    ).sort_values("MonthStart")

    y_raw = df["Next_month_kwh"].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    y_scaled = scaler.fit_transform(y_raw.reshape(-1, 1)).flatten()

    X_seq, y_seq = create_sequences(y_scaled, seq_len=6)
    split = int(len(X_seq) * 0.8)
    X_train, X_test = X_seq[:split], X_seq[split:]
    y_train, y_test = y_seq[:split], y_seq[split:]

    LOGGER.info("Train: %d, Test: %d, Target range: %.2f-%.2f kWh",
                len(X_train), len(X_test), y_raw.min(), y_raw.max())

    model = Sequential(
        [
            LSTM(48, activation="tanh", input_shape=(6, 1)),
            BatchNormalization(),
            Dropout(0.25),
            Dense(24, activation="relu"),
            Dense(1),
        ]
    )
    model.compile(optimizer=Adam(learning_rate=0.003), loss="mse", metrics=["mae"])

    early_stop = EarlyStopping(monitor="val_loss", patience=60, restore_best_weights=True)
    reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=20, min_lr=1e-5)

    model.fit(
        X_train, y_train,
        epochs=500,
        batch_size=4,
        validation_split=0.15,
        callbacks=[early_stop, reduce_lr],
        verbose=0,
    )

    preds = model.predict(X_test, verbose=0).flatten()
    preds_inv = scaler.inverse_transform(preds.reshape(-1, 1)).flatten()
    y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    mae = mean_absolute_error(y_test_inv, preds_inv)
    rmse = np.sqrt(np.mean((y_test_inv - preds_inv) ** 2))
    r2 = r2_score(y_test_inv, preds_inv)

    LOGGER.info("MAE: %.4f kWh  RMSE: %.4f kWh  R2: %.4f", mae, rmse, r2)
    LOGGER.info("Test actuals: %s", [f"{v:.2f}" for v in y_test_inv])
    LOGGER.info("Test preds:   %s", [f"{v:.2f}" for v in preds_inv])

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_path)
    joblib.dump(scaler, scaler_path)

    LOGGER.info("Model saved to %s", model_path)
    return mae, rmse, r2


def predict_next(model, scaler, monthly_values: np.ndarray) -> float:
    seq_len = 6
    scaled = scaler.transform(monthly_values.reshape(-1, 1)).flatten()
    seq = scaled[-seq_len:].reshape(1, seq_len, 1)
    pred_scaled = model.predict(seq, verbose=0)[0, 0]
    return float(scaler.inverse_transform([[pred_scaled]])[0, 0])


if __name__ == "__main__":
    train_lstm(MODEL_PATH, SCALER_PATH)
