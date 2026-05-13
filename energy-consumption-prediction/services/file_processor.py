import logging
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pymongo import MongoClient

LOGGER = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "Date",
    "Time",
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]

NUMERIC_COLUMNS = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]


class FileValidationError(Exception):
    pass


@dataclass
class ProcessingResult:
    success: bool
    message: str
    records_processed: int = 0
    prediction: dict[str, Any] | None = None


def validate_file(file_path: Path) -> None:
    if not file_path.exists():
        raise FileValidationError("Uploaded file not found")

    if file_path.stat().st_size == 0:
        raise FileValidationError("Uploaded file is empty")

    ext = file_path.suffix.lower()
    if ext not in [".csv", ".txt"]:
        raise FileValidationError(f"Invalid file format: {ext}. Use .csv or .txt")

    # Both .csv and .txt files use comma separator based on the sample files
    sep = ","
    try:
        df = pd.read_csv(file_path, sep=sep, nrows=1)
    except Exception as e:
        raise FileValidationError(f"Failed to parse file: {e}")

    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        raise FileValidationError(f"Missing required columns: {missing}")


def clean_and_process_data(file_path: Path, output_dir: Path) -> pd.DataFrame:
    # Both .csv and .txt files use comma separator based on the sample files
    sep = ","

    df = pd.read_csv(file_path, sep=sep, low_memory=False)

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            raise FileValidationError(f"Missing required column: {col}")

    df.replace("?", pd.NA, inplace=True)
    df.dropna(subset=EXPECTED_COLUMNS, inplace=True)

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=NUMERIC_COLUMNS, inplace=True)

    df = df[(df["Voltage"] > 0) & (df["Global_intensity"] >= 0)]
    df = df[(df["Global_active_power"] >= 0) & (df["Global_reactive_power"] >= 0)]

    df["Datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"], dayfirst=True, errors="coerce"
    )
    df.dropna(subset=["Datetime"], inplace=True)

    df["date_hour"] = df["Datetime"].dt.strftime("%Y-%m-%d %H:00")

    hourly_avg = df.groupby("date_hour")["Global_active_power"].mean().reset_index()
    hourly_avg.columns = ["date_hour", "avg_power"]

    hourly_avg = hourly_avg.sort_values("date_hour")

    processed_path = output_dir / "uploaded_hourly_avg.csv"
    hourly_avg.to_csv(processed_path, index=False)

    LOGGER.info(f"Processed {len(hourly_avg)} hourly records")
    return hourly_avg


def run_spark_forecast(input_csv: Path, output_csv: Path) -> dict[str, Any]:
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.regression import LinearRegression
    from pyspark.ml.evaluation import RegressionEvaluator
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, dayofmonth, hour, month

    spark = (
        SparkSession.builder.appName("EnergyForecastUpload")
        .master("local[*]")
        .getOrCreate()
    )

    data = spark.read.csv(
        str(input_csv), header=True, schema="date_hour STRING, avg_power DOUBLE"
    )
    data = data.withColumn("hour", hour(col("date_hour")))
    data = data.withColumn("day", dayofmonth(col("date_hour")))
    data = data.withColumn("month", month(col("date_hour")))

    assembler = VectorAssembler(inputCols=["hour", "day", "month"], outputCol="features")
    data = assembler.transform(data)

    train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)
    lr = LinearRegression(featuresCol="features", labelCol="avg_power")
    model = lr.fit(train_data)

    predictions = model.transform(test_data)
    selected = predictions.select("date_hour", "avg_power", "prediction")

    result_df = selected.toPandas()
    result_df.to_csv(output_csv, index=False)

    # Calculate evaluation metrics
    mae = 0.0
    rmse = 0.0
    r2 = 0.0
    
    if not result_df.empty:
        # Calculate MAE
        mae_evaluator = RegressionEvaluator(labelCol="avg_power", predictionCol="prediction", metricName="mae")
        mae = float(mae_evaluator.evaluate(predictions))
        
        # Calculate RMSE
        rmse_evaluator = RegressionEvaluator(labelCol="avg_power", predictionCol="prediction", metricName="rmse")
        rmse = float(rmse_evaluator.evaluate(predictions))
        
        # Calculate R²
        r2_evaluator = RegressionEvaluator(labelCol="avg_power", predictionCol="prediction", metricName="r2")
        r2 = float(r2_evaluator.evaluate(predictions))
        
        latest = result_df.iloc[-1]
        spark.stop()
        
        return {
            "date_hour": str(latest["date_hour"]),
            "avg_power": float(latest["avg_power"]),
            "predicted_power": float(latest["prediction"]),
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
        }
    
    spark.stop()
    return None


def store_prediction_in_mongo(
    prediction: dict[str, Any], mongo_uri: str, db_name: str, collection: str
) -> str:
    client = MongoClient(mongo_uri)
    db = client[db_name]

    record = {
        "schema_version": "1.0",
        "date_hour": prediction["date_hour"],
        "avg_power": prediction["avg_power"],
        "predicted_power": prediction["predicted_power"],
        "model": "spark_mllib_linear_regression",
        "source": "upload_file",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }

    result = db[collection].insert_one(record)
    client.close()
    return str(result.inserted_id)


def process_uploaded_file(
    file_path: Path,
    output_dir: Path,
    mongo_uri: str = "mongodb://localhost:27017/",
    mongo_db: str = "energy_predictions",
    mongo_collection: str = "predictions",
) -> ProcessingResult:
    try:
        validate_file(file_path)

        processed_df = clean_and_process_data(file_path, output_dir)

        spark_output = output_dir / "spark_predictions.csv"
        prediction = run_spark_forecast(
            output_dir / "uploaded_hourly_avg.csv", spark_output
        )

        if prediction:
            store_prediction_in_mongo(prediction, mongo_uri, mongo_db, mongo_collection)

        return ProcessingResult(
            success=True,
            message="File processed successfully",
            records_processed=len(processed_df),
            prediction=prediction,
        )

    except FileValidationError as e:
        return ProcessingResult(success=False, message=str(e))
    except Exception as e:
        LOGGER.exception("Error processing file")
        return ProcessingResult(success=False, message=f"Processing failed: {e}")