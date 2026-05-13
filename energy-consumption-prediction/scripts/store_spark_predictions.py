import logging
from pathlib import Path

from services.spark_predictions import latest_prediction, store_prediction

LOGGER = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parents[1]
    spark_csv = root / "output" / "spark_predictions.csv"

    record = latest_prediction(spark_csv)
    inserted_id = store_prediction(
        record,
        mongo_uri="mongodb://localhost:27017/",
        db_name="energy_predictions",
        collection="predictions",
    )
    LOGGER.info("Stored Spark prediction with id %s", inserted_id)


if __name__ == "__main__":
    main()