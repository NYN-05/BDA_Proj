import logging
import subprocess
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def run_mapreduce() -> None:
    """Run MapReduce processing to generate hourly averages"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parent
    
    # Run the MapReduce processor
    mapreduce_script = root / "hadoop_runner.py"
    result = subprocess.run(
        ["python", str(mapreduce_script)],
        cwd=str(root),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("MapReduce processing failed.")
    
    LOGGER.info("MapReduce processing completed successfully")


def run_spark_forecast() -> None:
    """Run Spark MLlib forecasting on processed data"""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parent
    mapreduce_output = root / "output" / "mapreduce_hourly_avg.csv"

    if not mapreduce_output.exists():
        raise FileNotFoundError(
            "MapReduce output not found. Run MapReduce processing first."
        )

    spark_script = root / "hadoop" / "spark_forecast_local.py"
    result = subprocess.run(
        ["python", str(spark_script)],
        cwd=str(root),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Spark MLlib forecasting failed.")

    LOGGER.info("Spark MLlib forecasting completed successfully")


def main() -> None:
    """Main function - can be called to run both MapReduce and Spark forecasting"""
    try:
        run_mapreduce()
        run_spark_forecast()
    except Exception as e:
        LOGGER.error(f"Error in processing pipeline: {e}")
        raise


if __name__ == "__main__":
    main()
