import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
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

CHARTS_DIR = PROJECT_ROOT / "visualization" / "charts"
OUTPUT_DIR = PROJECT_ROOT / "output"

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGODB_DB", "energy_predictions")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION", "predictions")

from services.spark_predictions import get_latest_prediction, store_prediction
from services.file_processor import process_uploaded_file, ProcessingResult


class PredictionResponse(BaseModel):
    id: str | None
    schema_version: str
    date_hour: str
    avg_power: float
    predicted_power: float
    model: str
    source: str
    generated_at: str


class UploadResponse(BaseModel):
    success: bool
    message: str
    records_processed: int | None = None
    prediction: PredictionResponse | None = None


@app.get("/")
def root():
    return {"status": "ok", "message": "Energy Prediction API", "endpoints": ["/upload", "/predict", "/predictions/latest"]}


@app.get("/db/health")
def db_health():
    from pymongo import MongoClient

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MongoDB ping failed: {exc}")
    finally:
        client.close()
    return {"status": "ok"}


@app.get("/predictions/latest")
def latest_prediction_endpoint():
    doc = get_latest_prediction(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    if not doc:
        raise HTTPException(status_code=404, detail="No predictions found. Upload a file first.")
    return doc


@app.get("/charts/{name}")
def get_chart(name: str):
    path = CHARTS_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Chart '{name}' not found")
    return FileResponse(path, media_type="image/png")


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        return UploadResponse(success=False, message="No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in [".csv", ".txt"]:
        return UploadResponse(
            success=False,
            message="Invalid file format. Use .csv or .txt files containing energy consumption data."
        )

    temp_dir = PROJECT_ROOT / "temp_uploads"
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / file.filename
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        result: ProcessingResult = process_uploaded_file(
            temp_path,
            OUTPUT_DIR,
            MONGO_URI,
            MONGO_DB,
            MONGO_COLLECTION,
        )

        if not result.success:
            return UploadResponse(success=False, message=result.message)

        if result.prediction:
            from services.spark_predictions import SparkPredictionRecord
            record = SparkPredictionRecord(
                date_hour=result.prediction["date_hour"],
                avg_power=result.prediction["avg_power"],
                predicted_power=result.prediction["predicted_power"],
                model="spark_mllib_linear_regression",
                source="upload_file",
                generated_at=result.prediction.get("generated_at", ""),
                mae=result.prediction.get("mae"),
                rmse=result.prediction.get("rmse"),
                r2=result.prediction.get("r2"),
            )
            inserted_id = store_prediction(record, MONGO_URI, MONGO_DB, MONGO_COLLECTION)

            return UploadResponse(
                success=True,
                message=f"Successfully processed {result.records_processed} records",
                records_processed=result.records_processed,
                prediction=PredictionResponse(
                    id=inserted_id,
                    schema_version="1.0",
                    date_hour=result.prediction["date_hour"],
                    avg_power=result.prediction["avg_power"],
                    predicted_power=result.prediction["predicted_power"],
                    model="spark_mllib_linear_regression",
                    source="upload_file",
                    generated_at=record.generated_at,
                ),
            )

        return UploadResponse(success=False, message="No prediction generated")

    except Exception as e:
        return UploadResponse(success=False, message=f"Error processing file: {str(e)}")
    finally:
        if temp_path.exists():
            temp_path.unlink()


@app.post("/predict")
async def predict() -> PredictionResponse:
    from services.spark_predictions import latest_prediction as spark_latest_prediction

    spark_csv = OUTPUT_DIR / "spark_predictions.csv"
    if not spark_csv.exists():
        raise HTTPException(
            status_code=404,
            detail="No predictions available. Please upload a file first using /upload endpoint."
        )

    record = spark_latest_prediction(spark_csv)
    inserted_id = store_prediction(record, MONGO_URI, MONGO_DB, MONGO_COLLECTION)

    payload = record.as_dict()
    payload["id"] = inserted_id
    return PredictionResponse(**payload)