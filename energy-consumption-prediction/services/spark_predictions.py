import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

LOGGER = logging.getLogger(__name__)

SPARK_SCHEMA_VERSION = "1.0"


@dataclass
class SparkPredictionRecord:
    date_hour: str
    avg_power: float
    predicted_power: float
    model: str
    source: str
    generated_at: str
    schema_version: str = SPARK_SCHEMA_VERSION
    mae: Optional[float] = None
    rmse: Optional[float] = None
    r2: Optional[float] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "date_hour": self.date_hour,
            "avg_power": float(self.avg_power),
            "predicted_power": float(self.predicted_power),
            "model": self.model,
            "source": self.source,
            "generated_at": self.generated_at,
            "mae": self.mae,
            "rmse": self.rmse,
            "r2": self.r2,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_spark_predictions(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError("spark_predictions.csv not found. Run Spark forecast first.")
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("spark_predictions.csv is empty.")
    return df


def latest_prediction(csv_path: Path) -> SparkPredictionRecord:
    df = load_spark_predictions(csv_path)
    latest = df.iloc[-1]
    return SparkPredictionRecord(
        date_hour=str(latest["date_hour"]),
        avg_power=float(latest["avg_power"]),
        predicted_power=float(latest["prediction"]),
        model=str(latest.get("model", "spark_mllib")),
        source=str(latest.get("source", "spark_local")),
        generated_at=str(latest.get("generated_at", _now_iso())),
        mae=float(latest["mae"]) if pd.notna(latest.get("mae")) else None,
        rmse=float(latest["rmse"]) if pd.notna(latest.get("rmse")) else None,
        r2=float(latest["r2"]) if pd.notna(latest.get("r2")) else None,
    )


def store_prediction(record: SparkPredictionRecord, mongo_uri: str, db_name: str, collection: str) -> str:
    from pymongo import MongoClient

    client = MongoClient(mongo_uri)
    db = client[db_name]
    result = db[collection].insert_one(record.as_dict())
    client.close()
    return str(result.inserted_id)


def get_latest_prediction(mongo_uri: str, db_name: str, collection: str) -> dict[str, Any] | None:
    from pymongo import MongoClient

    client = MongoClient(mongo_uri)
    db = client[db_name]
    doc = db[collection].find_one(sort=[("generated_at", -1)])
    client.close()
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc