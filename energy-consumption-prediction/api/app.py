import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Energy Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

MODEL_PATH = PROJECT_ROOT / "ml" / "saved_models" / "xgb_model.joblib"
SCALER_Y_PATH = PROJECT_ROOT / "ml" / "saved_models" / "xgb_scaler.gz"
METRICS_PATH = PROJECT_ROOT / "output" / "metrics.txt"
CHARTS_DIR = PROJECT_ROOT / "visualization" / "charts"

from preprocessing.clean_data import RAW_COLUMNS
from preprocessing.feature_engineering import build_monthly_series


def create_sequences(data, seq_len=6):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len])
    return np.array(X), np.array(y)


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not found. Run `python ml/train_xgb.py` first.")
    return joblib.load(MODEL_PATH)


def load_scaler():
    if not SCALER_Y_PATH.exists():
        raise FileNotFoundError("Scaler not found. Run `python ml/train_xgb.py` first.")
    return joblib.load(SCALER_Y_PATH)


def parse_upload(raw_bytes: bytes) -> pd.DataFrame:
    import csv
    text = raw_bytes.decode("utf-8", errors="replace")
    lines = text.strip().split("\n")
    if not lines:
        raise ValueError("Empty file")
    has_semicolon = ";" in lines[0]
    sep = ";" if has_semicolon else ","
    reader = csv.DictReader(lines, delimiter=sep)
    rows = [{k.strip(): v.strip() for k, v in row.items()} for row in reader]
    df = pd.DataFrame(rows)
    for col in RAW_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return df


class PredictionResponse(BaseModel):
    predicted_kwh: float
    month_start: str
    metrics: dict | None


class BacktestResponse(BaseModel):
    mae: float
    mse: float
    rmse: float
    r2: float
    monthly: list[dict]


def build_monthly(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True, errors="coerce")
    df = df[df["Datetime"].notna()]
    for col in ["Global_active_power", "Global_reactive_power", "Voltage", "Global_intensity",
                "Sub_metering_1", "Sub_metering_2", "Sub_metering_3"]:
        df[col] = pd.to_numeric(df[col].replace("?", pd.NA), errors="coerce")
    df = df.dropna(subset=["Global_active_power"])
    monthly = df.groupby(pd.Grouper(key="Datetime", freq="MS"))["Global_active_power"].sum() / 60.0
    monthly.name = "Monthly_kwh"
    return monthly


@app.get("/")
def root():
    return {"status": "ok", "message": "Energy Prediction API"}


@app.get("/metrics")
def get_metrics():
    if not METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="Metrics not found.")
    result = {}
    for line in METRICS_PATH.read_text(encoding="utf-8").strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = float(v.strip())
    return result


@app.get("/charts/{name}")
def get_chart(name: str):
    path = CHARTS_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Chart '{name}' not found")
    return FileResponse(path, media_type="image/png")


@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    model = load_model()
    scaler = load_scaler()

    contents = await file.read()
    df = parse_upload(contents)
    monthly = build_monthly(df)

    if len(monthly) < 7:
        raise HTTPException(status_code=400, detail="Need at least 7 months of data.")

    y_raw = monthly.values
    y_scaled = scaler.transform(y_raw.reshape(-1, 1)).flatten()

    X_seq, _ = create_sequences(y_scaled, seq_len=6)
    last_seq = y_scaled[-6:].reshape(1, -1)
    pred_scaled = model.predict(last_seq)[0]
    pred = float(scaler.inverse_transform([[pred_scaled]])[0, 0])

    next_month = (monthly.index[-1] + pd.offsets.MonthBegin(1)).strftime("%Y-%m-%d")

    return PredictionResponse(
        predicted_kwh=round(pred, 6),
        month_start=next_month,
        metrics=None,
    )


@app.post("/backtest")
async def backtest(file: UploadFile = File(...)) -> BacktestResponse:
    model = load_model()
    scaler = load_scaler()

    contents = await file.read()
    df = parse_upload(contents)
    monthly = build_monthly(df)

    if len(monthly) < 7:
        raise HTTPException(status_code=400, detail="Need at least 7 months of data.")

    y_raw = monthly.values
    y_scaled = scaler.transform(y_raw.reshape(-1, 1)).flatten()

    X_seq, y_seq = create_sequences(y_scaled, seq_len=6)
    preds_scaled = model.predict(X_seq)
    preds = scaler.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()
    y_vals = scaler.inverse_transform(y_seq.reshape(-1, 1)).flatten()

    mae = float(np.mean(np.abs(y_vals - preds)))
    mse = float(np.mean((y_vals - preds) ** 2))
    rmse = float(np.sqrt(mse))
    ss_res = float(np.sum((y_vals - preds) ** 2))
    ss_tot = float(np.sum((y_vals - y_vals.mean()) ** 2))
    r2 = float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0

    monthly_list = [
        {"month": str(monthly.index[i + 6]), "actual": round(float(y_vals[i]), 6), "predicted": round(float(preds[i]), 6)}
        for i in range(len(preds))
    ]

    return BacktestResponse(mae=round(mae, 6), mse=round(mse, 6), rmse=round(rmse, 6), r2=round(r2, 4), monthly=monthly_list)